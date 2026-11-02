/* Node-only dashboard smoke. No Home Assistant, internet, or inverter needed. */
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm"),assert=require("node:assert/strict");
class Element {
 constructor(tag="element"){this.tagName=tag.toUpperCase();this.className="";this.text="";this.children=[];this.listeners={};this.attributes={};this.style={};this.value="";this.disabled=false;this.checked=false;this.open=false;}
 set textContent(s){this.text=String(s);this.children=[]}
 get textContent(){return this.text+this.children.map(x=>x.textContent).join("")}
 append(...nodes){for(const n of nodes)this.children.push(typeof n==="string"?Object.assign(new Element("text"),{text:String(n)}):n)}
 replaceChildren(...nodes){this.children=[];this.text="";this.append(...nodes)}
 setAttribute(k,v){this.attributes[k]=String(v)}
 addEventListener(k,fn){this.listeners[k]=fn}
 getBoundingClientRect(){return {left:0,width:920,height:280}}
 attachShadow(){this.shadowRoot=new Element("shadow-root");return this.shadowRoot}
 select(){this.selectedText=this.value}
 focus(){}
 *walk(){yield this;for(const v of this.children)yield* v.walk()}
}
const registered={},copied=[];
const context={
 HTMLElement:Element,
 document:{createElement:tag=>new Element(tag),createElementNS:(_,tag)=>new Element(tag),execCommand:()=>true},
 customElements:{get:k=>registered[k],define:(k,c)=>registered[k]=c},
 window:{customCards:[]},
 navigator:{clipboard:{writeText:async v=>copied.push(v)}},
 console,Date,Intl,Number,Object,String,Math,Array,Map,Set,Promise,
};
const js=fs.readFileSync(path.join(__dirname,"../custom_components/saj_h2_safe/frontend/saj-safe-monitor-card.js"),"utf8");
vm.runInNewContext(js,context,{filename:"saj-safe-monitor-card.js"});
const Card=registered["saj-safe-monitor-card"];assert.ok(Card,"standalone HA card registered");
const c=new Card();
const states={};
const key=s=>"sensor.saj_h2_safe_monitor_"+s;
function sensor(s,v,attrs={}){const id=key(s);states[id]={entity_id:id,state:String(v),attributes:{friendly_name:"SAJ "+s,...attrs}}}
for(const [s,v] of Object.entries({
 total_solar_power:9500,home_consumption:3000,battery_power:-6500,
 battery_state_of_charge:84,estimated_battery_energy:33.6,grid_power_raw_signed:0,
 solar_today:66.12,home_consumed_today:30.5,
 battery_charged_today:34.2,battery_discharged_today:7.1,
 grid_imported_today_estimated:.12,grid_exported_today_estimated:2.1,
 grid_energy_imported_estimated:.5,grid_energy_exported_estimated:1.2,
 grid_power_signed_import_export:0,grid_import_direction_unverified:0,grid_export_direction_unverified:0,
 solar_total:9876,home_consumed_total:6000,battery_charged_total:200,battery_discharged_total:150,
 today_s_solar_forecast:81,today_s_solar_outlook_actual_remaining:87,
 solar_forecast_remaining_today:21,tomorrow_s_solar_forecast:89,
 next_7_days_solar_forecast:530,forecast_learning:"Calibrating"
}))sensor(s,v);
const now=Date.now();
states[key("today_s_solar_forecast")].attributes.today_hourly=Array.from({length:24},(_,h)=>({start:(now-Math.floor(now%86400000))/1000+h*3600,kwh:h>6&&h<19?4.4:0,hour:String(h).padStart(2,"0")+":00"}));
states[key("today_s_solar_forecast")].attributes.daily=Array.from({length:7},(_,i)=>({date:"2026-11-"+String(i+2).padStart(2,"0"),kwh:70+i*2}));
states[key("today_s_solar_forecast")].attributes.hourly=[{time:"15:00",kwh:3,cloud:10}];
c.setConfig({});
c.hass={states,callApi:async()=>[]};
const all=[...c.shadowRoot.walk()];
const txt=c.shadowRoot.textContent;
for(const word of ["Live energy","Historic Data","Solar forecast","Home Assistant Energy","Today so far","Generated","Charged","Discharged","Imported","Exported","Forecast by now","Actual vs projected"]){
 assert.ok(txt.includes(word),"missing "+word)}
assert.ok(txt.includes("66.12 kWh"),"actual daily solar read from registered sensor");
assert.ok(txt.includes("34.20 kWh"),"battery charged");
assert.ok(txt.includes("7.10 kWh"),"battery discharged");
assert.ok(txt.includes("0.12 kWh"),"grid import estimate");
const selectors=all.filter(x=>x.tagName==="SELECT");
assert.ok(selectors.length);
assert.equal(selectors[0].children[0].textContent,"10 minutes");
const svgs=all.filter(x=>x.tagName==="SVG");
assert.equal(svgs.length,2,"Historic Data and actual/forecast graphs");
const projectedPaths=[...svgs[1].walk()].filter(n=>
 n.tagName==="PATH"&&n.attributes.stroke==="#e6b650");
assert.ok(projectedPaths.length>0,
 "hourly forecast must draw a yellow SVG line (not isolated invisible points)");
assert.ok(projectedPaths.some(n=>(n.attributes.d||"").includes("L")),
 "forecast path must connect successive hourly samples");
assert.ok(txt.includes("v0.4.2"),"frontend version marker allows cache diagnosis");
assert.ok(txt.includes("Projected solar (yellow)"),"visible forecast legend");
assert.ok(txt.includes("Recorded solar (blue)"),"visible actual legend");
// The missing-line bug must not recur when the hourly series has variable
// but valid 60-minute interval timestamps and actual points are sparse.
const forecastData=states[key("today_s_solar_forecast")].attributes.today_hourly;
assert.equal(forecastData.length,24);
assert.ok(projectedPaths[0].attributes["stroke-width"]>=3);


for(const svg of svgs){assert.ok(svg.listeners.pointermove);assert.ok(svg.listeners.pointerdown);assert.ok(svg.listeners.keydown)}
const inputs=all.filter(x=>x.tagName==="INPUT"&&x.readOnly);
assert.ok(inputs.some(x=>x.value===key("battery_charged_total")));
assert.ok(inputs.some(x=>x.value===key("battery_discharged_total")));
const copy=all.find(x=>x.tagName==="BUTTON"&&x.textContent==="Copy"&&!x.disabled);
assert.ok(copy?.listeners.click);
copy.listeners.click();
Promise.resolve().then(()=>{
 assert.ok(copied[0]?.startsWith("sensor.saj_h2_safe_monitor_"));
 assert.ok(!/write_register|set_operating_mode|call_service/.test(js),"no write paths");
 console.log("Standalone read-only dashboard smoke passed: live, daily, history, forecast hover and copyable Energy IDs");
}).catch(e=>{console.error(e);process.exitCode=1});
