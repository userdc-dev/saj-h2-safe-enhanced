
(()=>{"use strict";
const ids={pv:"total_solar_power",home:"home_consumption",battery:"battery_power",soc:"battery_state_of_charge",stored:"estimated_battery_energy",grid:"grid_power_raw_signed",solarToday:"solar_today",homeToday:"home_consumed_today",chargeToday:"battery_charged_today",dischargeToday:"battery_discharged_today",importDay:"grid_imported_today_estimated",exportDay:"grid_exported_today_estimated",import:"grid_energy_imported_estimated",export:"grid_energy_exported_estimated",signed:"grid_power_signed_import_export",importPower:"grid_import_direction_unverified",exportPower:"grid_export_direction_unverified",solarTotal:"solar_total",homeTotal:"home_consumed_total",chargeTotal:"battery_charged_total",dischargeTotal:"battery_discharged_total",forecast:"today_s_solar_forecast",outlook:"today_s_solar_outlook_actual_remaining",remaining:"solar_forecast_remaining_today",tomorrow:"tomorrow_s_solar_forecast",week:"next_7_days_solar_forecast",learning:"forecast_learning"};
const palette={pv:"#edb34b",home:"#53a5ee",battery:"#3fc5a0",grid:"#b681e6"};
const el=(tag,cls,label)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(label!==undefined)e.textContent=String(label);return e};
const append=(parent,...items)=>{parent.append(...items.filter(Boolean));return parent};
const valid=v=>typeof v==="number"&&Number.isFinite(v),units=(v,u)=>valid(v)?v.toFixed(2)+" "+u:"—",kw=v=>!valid(v)?"—":Math.abs(v)>=1000?units(v/1000,"kW"):Math.round(v)+" W";
const css=[
":host{display:block;color:var(--primary-text-color,#eee);font-family:inherit}",
"*{box-sizing:border-box}.app{max-width:1550px;margin:auto;padding:15px;display:grid;gap:13px}",
".panel{border:1px solid var(--divider-color,#444);background:var(--card-background-color,#202020);padding:17px;border-radius:14px}",
".head{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:12px}",
"h2,h3,h4{margin:0}h2{font-size:19px}h3{font-size:17px}h4{font-size:13px}",
".muted{color:var(--secondary-text-color,#aaa);font-size:12px;line-height:1.55}.good{color:#43b95f}.bad{color:#e68c76}",
"button,select{border:1px solid var(--divider-color,#555);color:inherit;border-radius:9px;background:var(--card-background-color,#242424);padding:8px 11px;cursor:pointer;font:inherit}",
".track{background:rgba(140,140,140,.23);height:9px;border-radius:8px;overflow:hidden}.track>span{display:block;height:100%;background:var(--primary-color,#0ea7ca)}",
".batteryBar{height:13px;margin:10px 0 15px}.meters{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;margin:13px 0}",
".meterHeader{display:flex;justify-content:space-between;gap:7px;margin-bottom:8px;font-size:12px}.scroll{overflow-x:auto}",
".flow{width:100%;min-width:685px;table-layout:fixed;border-collapse:separate;border-spacing:0;border:1px solid var(--divider-color,#444);border-radius:10px;overflow:hidden}",
".flow th,.flow td{padding:10px 7px;text-align:center;border-bottom:1px solid var(--divider-color,#444);border-right:1px solid var(--divider-color,#444);font-size:12px}",
".flow tr>*:last-child{border-right:0}.flow tr:last-child>*{border-bottom:0}.flow th{background:rgba(150,150,150,.06)}",
".flow .power td{font-size:19px;font-weight:700}.flow .today td{background:rgba(130,130,130,.07);vertical-align:top}",
".today b{display:block;color:var(--secondary-text-color,#aaa);font-size:11px;margin-bottom:7px}",
".daily{display:flex;justify-content:space-between;gap:5px;margin:4px 0;font-size:11px}.daily strong{white-space:nowrap;font-variant-numeric:tabular-nums}",
".legend{display:flex;gap:8px;flex-wrap:wrap;margin:7px 0 12px}.legend label{display:flex;align-items:center;gap:6px;border:1px solid var(--divider-color,#444);border-radius:8px;padding:7px;cursor:pointer;font-size:12px}",
".legend input{accent-color:var(--primary-color,#0ba7c9)}.dot{width:9px;height:9px;border-radius:50%;display:inline-block}",
"svg{width:100%;height:auto;max-height:370px;cursor:crosshair;touch-action:pan-y}.tooltip{border:1px solid var(--divider-color,#444);background:rgba(145,145,145,.07);padding:10px;border-radius:9px;display:flex;gap:13px;flex-wrap:wrap;min-height:40px;font-size:12px;font-variant-numeric:tabular-nums}",
".stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.stat{border:1px solid var(--divider-color,#444);border-radius:10px;padding:12px}.stat strong{display:block;font-size:20px;margin:5px 0}",
"details{border:1px solid var(--divider-color,#444);border-radius:10px;margin:12px 0}summary{cursor:pointer;padding:12px;font-size:13px;font-weight:650}",
"details[open]>summary{border-bottom:1px solid var(--divider-color,#444)}.rows{padding:12px}.day{display:grid;grid-template-columns:95px minmax(0,1fr) 95px;gap:10px;align-items:center;padding:8px;border-radius:7px;cursor:crosshair;font-size:12px}.day:hover,.day:focus{background:rgba(130,130,130,.10)}",
".bar{background:rgba(140,140,140,.2);height:9px;border-radius:8px;overflow:hidden}.bar span{display:block;height:100%;background:#e1b64a}",
".guide{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,270px),1fr));gap:10px;padding:12px}.group{border:1px solid var(--divider-color,#444);border-radius:9px;padding:12px;min-width:0}",
".group h4{margin-bottom:9px}.item{padding:8px 0;border-top:1px solid var(--divider-color,#444)}.item label{display:block;font-size:12px;font-weight:650}.item small{display:block;color:var(--secondary-text-color,#aaa);font-size:11px;margin:4px 0;overflow-wrap:anywhere}",
".copyRow{display:flex;gap:7px}.copyRow input{background:transparent;color:inherit;border:1px solid var(--divider-color,#555);border-radius:7px;padding:7px;font:11px monospace;min-width:0;flex:1;width:40px}.copyRow button{font-size:11px;padding:7px}",
".note{font-size:11px;line-height:1.6;margin:12px 0 0}@media(max-width:690px){.app{padding:6px}.panel{padding:11px}.meters,.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.day{grid-template-columns:70px 1fr 75px}}"
].join("\n");
class Monitor extends HTMLElement{
constructor(){super();this.attachShadow({mode:"open"});this.conf={};this.range=6;this.show={pv:true,home:true,battery:true,grid:true};this.historyData={};this.updated=0;this.pending=false;this.error="";this.tick=0;this.expanded={days:false,hours:false,guide:false};this.actualDay=[];this.actualFetched=0;this.actualLoading=false;this.actualError="";this.actualDate="";}
setConfig(config){this.conf=config||{};this.render()}
set hass(h){this.hassObj=h;if(!h)return;if(Date.now()-this.tick>9000){this.tick=Date.now();this.render();if(Date.now()-this.updated>30000)this.loadHistory()}}
getCardSize(){return 16}
state(key){
const suffix=ids[key]||key;
const direct=this.hassObj?.states?.[this.conf.entities?.[key]||
  "sensor.saj_h2_safe_monitor_"+suffix];
if(direct)return direct;
const registry=this.hassObj?.entities||{};
const match=Object.entries(registry).find(([entityId,meta])=>
  entityId.startsWith("sensor.")&&meta?.platform==="saj_h2_safe"&&
  typeof meta.unique_id==="string"&&meta.unique_id.endsWith("_"+suffix)&&
  this.hassObj?.states?.[entityId]);
return match?this.hassObj.states[match[0]]:null;
}
num(key){const x=this.state(key);if(!x||["unknown","unavailable",""].includes(String(x.state)))return null;const v=Number(x.state);return Number.isFinite(v)?v:null}
panel(title,subtitle){const p=el("section","panel"),h=el("div","head");append(h,el("h3","",title),el("span","muted",subtitle||""));return append(p,h)}
live(){
const p=this.panel("Live energy","Inverter telemetry · ~10 seconds"),soc=this.num("soc"),stored=this.num("stored"),bat=this.num("battery"),grid=this.num("grid");
const label=el("div","head");append(label,el("strong","","Battery"),el("strong","",units(soc,"%")+" · "+units(stored,"kWh")+" stored"));p.append(label);
const bar=el("div","track batteryBar"),fill=el("span");fill.style.width=(soc===null?0:Math.max(0,Math.min(100,soc)))+"%";p.append(append(bar,fill));
const meters=el("div","meters");
for(const [name,key,max] of [["Solar","pv",13200],["House","home",10000],["Battery","battery",10000],["Grid","grid",10000]]){
const v=this.num(key),card=el("div"),row=el("div","meterHeader"),track=el("div","track"),fill=el("span");
append(row,el("span","",name),el("strong","",kw(v==null?null:Math.abs(v))));
fill.style.width=(v===null?0:Math.min(100,Math.abs(v)/max*100))+"%";append(card,row,append(track,fill));meters.append(card)}p.append(meters);
const table=el("table","flow"),h=el("tr");
["☀️ Solar","🏠 House","🔋 Battery","⚡ Grid","🔮 Forecast"].forEach(t=>h.append(el("th","",t)));table.append(h);
const rows=[
[kw(this.num("pv")),kw(this.num("home")),kw(bat==null?null:Math.abs(bat)),kw(grid==null?null:Math.abs(grid)),units(this.num("outlook"),"kWh")],
["Generating","Using",bat==null?"—":bat>15?"Discharging":bat< -15?"Charging":"Idle",grid==null?"—":grid>15?"Import*":grid< -15?"Export*":"No net exchange",units(this.num("remaining"),"kWh")+" remaining"],
["","",units(soc,"%")+" SOC · "+units(stored,"kWh"),"Direction provisional",units(this.num("tomorrow"),"kWh")+" tomorrow"]
];
rows.forEach((line,i)=>{const r=el("tr",i===0?"power":"");line.forEach(v=>r.append(el("td","",v)));table.append(r)});
const today=el("tr","today"),forecast=this.num("forecast"),remaining=this.num("remaining");
const totals=[
[["Generated",this.num("solarToday")]],
[["Used",this.num("homeToday")]],
[["Charged",this.num("chargeToday")],["Discharged",this.num("dischargeToday")]],
[["Imported*",this.num("importDay")],["Exported*",this.num("exportDay")]],
[["Expected",valid(forecast)&&valid(remaining)?Math.max(0,forecast-remaining):null]]
];
totals.forEach((group,i)=>{const td=el("td");td.append(el("b","",i===4?"Forecast by now":"Today so far"));for(const [name,v] of group){const row=el("div","daily");append(row,el("span","",name),el("strong","",units(v,"kWh")));td.append(row)}today.append(td)});
table.append(today);p.append(append(el("div","scroll"),table));
p.append(el("p","muted note","*Grid import/export direction and kWh estimate are provisional; grid energy counts monitored intervals only. Solar, house and battery daily values are inverter counters. Forecast is a prediction."));
return p}
history(){
const p=this.panel("Historic Data","Recorded solar, home, signed battery and grid power · kW"),head=el("div","head"),select=el("select");
select.setAttribute("aria-label","Historic Data time range");
for(const [hours,label] of [[1/6,"10 minutes"],[6,"6 hours"],[12,"12 hours"],[24,"24 hours"],[48,"48 hours"],[168,"7 days"]]){const opt=el("option","",label);opt.value=String(hours);opt.selected=this.range===hours;select.append(opt)}
select.addEventListener("change",()=>{this.range=Number(select.value);this.updated=0;this.render();this.loadHistory(true)});head.append(select);p.append(head);
const legends=el("div","legend");
for(const [k,name] of [["pv","Solar production"],["home","House usage"],["battery","Battery ±"],["grid","Grid ±"]]){
const row=el("label"),check=el("input"),dot=el("i","dot");check.type="checkbox";check.checked=this.show[k];dot.style.background=palette[k];
check.addEventListener("change",()=>{this.show[k]=check.checked;this.render()});append(row,check,dot,el("span","",name));legends.append(row)}p.append(legends);
const ns="http://www.w3.org/2000/svg",L=50,R=900,T=23,B=254;
const svg=document.createElementNS(ns,"svg");svg.setAttribute("viewBox","0 0 920 288");svg.setAttribute("role","img");svg.setAttribute("tabindex","0");
svg.setAttribute("aria-label","Hover, tap or use arrow keys to inspect recorded power");
const shape=(name,attrs,txt)=>{const x=document.createElementNS(ns,name);Object.entries(attrs).forEach(([k,v])=>x.setAttribute(k,String(v)));if(txt!==undefined)x.textContent=String(txt);svg.append(x);return x};
const end=Date.now(),start=end-this.range*3600000;
const values=["pv","home","battery","grid"].flatMap(k=>this.show[k]?(this.historyData[k]||[]).map(p=>p.v/1000):[]);
const lo=Math.min(-2,Math.floor(Math.min(0,...values)/2)*2),hi=Math.max(2,Math.ceil(Math.max(0,...values)/2)*2);
const x=t=>L+(t-start)/(end-start)*(R-L),y=v=>B-(v-lo)/(hi-lo)*(B-T);
for(let i=0;i<=5;i++){const v=lo+(hi-lo)*i/5,Y=y(v);shape("line",{x1:L,x2:R,y1:Y,y2:Y,stroke:"currentColor","stroke-opacity":Math.abs(v)<.1?.45:.12});
shape("text",{x:L-8,y:Y+4,"font-size":12,"text-anchor":"end",fill:"currentColor"},v.toFixed(1))}
shape("text",{x:12,y:13,fill:"currentColor","font-size":12},"kW");
for(let i=0;i<=6;i++){const t=start+(end-start)*i/6;shape("text",{x:x(t),y:280,fill:"currentColor","font-size":12,"text-anchor":i===0?"start":i===6?"end":"middle"},new Date(t).toLocaleTimeString(undefined,{hour:"2-digit",minute:"2-digit"}))}
for(const k of ["pv","home","battery","grid"]){if(!this.show[k])continue;let segment=[],previous=null;
const flush=()=>{if(segment.length>1)shape("path",{d:segment.map((p,i)=>(i?"L":"M")+x(p.t).toFixed(1)+","+y(p.v/1000).toFixed(1)).join(" "),stroke:palette[k],fill:"none","stroke-width":2.4});segment=[]};
for(const point of (this.historyData[k]||[])){if(point.t<start||point.t>end)continue;if(previous!==null&&point.t-previous>(this.range<=1/6?90000:45*60000))flush();segment.push(point);previous=point.t}flush()}
const cursor=shape("line",{x1:L,x2:L,y1:T,y2:B,stroke:"currentColor","stroke-dasharray":"4 4",visibility:"hidden"});
shape("rect",{x:L,y:T,width:R-L,height:B-T,fill:"transparent","pointer-events":"all"});
const tip=el("div","tooltip",this.pending?"Loading Recorder…":this.error||"Hover, tap or use ← / → for accurate readings.");
let fraction=.5;const steps=this.range<=1/6?20:this.range*12;
const inspect=f=>{fraction=Math.max(0,Math.min(1,Math.round(f*steps)/steps));const t=start+(end-start)*fraction;
cursor.setAttribute("x1",x(t));cursor.setAttribute("x2",x(t));cursor.setAttribute("visibility","visible");tip.replaceChildren();
tip.append(el("strong","",new Date(t).toLocaleTimeString(undefined,{hour:"2-digit",minute:"2-digit",second:"2-digit"})));
for(const k of ["pv","home","battery","grid"]){if(!this.show[k])continue;const nearest=(this.historyData[k]||[]).reduce((a,p)=>!a||Math.abs(p.t-t)<Math.abs(a.t-t)?p:a,null);
const validSample=nearest&&Math.abs(nearest.t-t)<=(this.range<=1/6?45000:6*60000);
const label=el("span","",k+": "+(validSample?kw(nearest.v):"no nearby reading")+(validSample?" · "+new Date(nearest.t).toLocaleTimeString():""));label.style.color=palette[k];tip.append(label)}};
const move=e=>{const box=svg.getBoundingClientRect();if(box.width)inspect(((e.clientX-box.left)/box.width*920-L)/(R-L))};
svg.addEventListener("pointermove",move);svg.addEventListener("pointerdown",move);
svg.addEventListener("keydown",e=>{if(!["ArrowLeft","ArrowRight"].includes(e.key))return;e.preventDefault();inspect(fraction+(e.key==="ArrowRight"?1:-1)/steps)});
p.append(svg,tip,el("p","muted note","Only actual Recorder measurements are drawn. Missing periods remain gaps; battery positive means discharging and grid direction is provisional."));
return p}
async loadHistory(force=false){
if(!this.hassObj||this.pending||!force&&Date.now()-this.updated<30000)return;
this.pending=true;this.error="";const range=this.range,now=new Date(),start=new Date(now.getTime()-range*3600000);
const sources=["pv","home","battery","grid"].map(k=>[k,this.state(k)]);
try{const ids=sources.filter(([,s])=>s).map(([,s])=>s.entity_id);
if(!ids.length)throw Error("No power sensors available");
const url="history/period/"+encodeURIComponent(start.toISOString())+"?filter_entity_id="+encodeURIComponent(ids.join(","))+"&end_time="+encodeURIComponent(now.toISOString())+"&minimal_response";
const rows=await this.hassObj.callApi("GET",url);if(range!==this.range)return;
const lookup=Object.fromEntries(sources.filter(([,s])=>s).map(([k,s])=>[s.entity_id,k]));
const next={pv:[],home:[],battery:[],grid:[]};
for(const list of Array.isArray(rows)?rows:[]){const id=list.find(q=>q.entity_id)?.entity_id,key=lookup[id];if(!key)continue;
for(const item of list){const t=Date.parse(item.last_changed||item.last_updated||""),v=Number(item.state);
if(Number.isFinite(t)&&Number.isFinite(v)&&!["unknown","unavailable",""].includes(String(item.state)))next[key].push({t,v})}
next[key].sort((a,b)=>a.t-b.t)}
this.historyData=next;this.updated=Date.now()
}catch(err){this.error="Recorder unavailable: "+(err?.message||String(err));this.updated=Date.now()}
finally{this.pending=false;this.render()}}
async loadActualDay(force=false){
if(!this.hassObj||this.actualLoading)return;
const midnight=new Date();midnight.setHours(0,0,0,0);
const day=midnight.toDateString();
if(!force&&day===this.actualDate&&Date.now()-this.actualFetched<300000)return;
const sensor=this.state("solarToday");if(!sensor)return;
this.actualLoading=true;
try{
const end=new Date(),url="history/period/"+encodeURIComponent(midnight.toISOString())+"?filter_entity_id="+encodeURIComponent(sensor.entity_id)+"&end_time="+encodeURIComponent(end.toISOString())+"&minimal_response";
const response=await this.hassObj.callApi("GET",url);
const list=Array.isArray(response)?response.flat():[];
const points=list.filter(q=>!["unknown","unavailable",""].includes(String(q.state))).map(q=>({t:Date.parse(q.last_changed||q.last_updated||""),v:Number(q.state)})).filter(q=>Number.isFinite(q.t)&&Number.isFinite(q.v)&&q.v>=0);
points.sort((a,b)=>a.t-b.t);
this.actualDay=points;this.actualDate=day;this.actualFetched=Date.now();this.actualError="";
}catch(error){this.actualError=error?.message||String(error);this.actualDate=day;this.actualFetched=Date.now()}
finally{this.actualLoading=false;this.render()}}
forecastChart(){
const pane=el("section","panel"),heading=el("div","head");
append(heading,el("h3","","Actual vs projected · Today"),
el("span","muted","Cumulative solar energy · hover for kWh"));
pane.append(heading);
const hourly=this.state("forecast")?.attributes?.today_hourly||[];
const midnight=new Date();midnight.setHours(0,0,0,0);const start=midnight.getTime();
if(this.actualDate!==midnight.toDateString()||Date.now()-this.actualFetched>300000)this.loadActualDay();
if(!Array.isArray(hourly)||!hourly.length){
pane.append(el("p","muted","Waiting for today's hourly solar forecast."));return pane}
let sum=0;
const forecast=[{t:start,v:0}];
for(const rec of [...hourly].sort((a,b)=>a.start-b.start)){
const ts=(Number(rec.start)+3600)*1000;
const v=Number(rec.kwh);
if(Number.isFinite(ts)&&Number.isFinite(v)&&v>=0){sum+=v;forecast.push({t:ts,v:sum})}}
const actual=this.actualDay||[];
const max=Math.max(1,...forecast.map(q=>q.v),...actual.map(q=>q.v));
const ns="http://www.w3.org/2000/svg",L=48,R=901,T=22,B=238;
const svg=document.createElementNS(ns,"svg");svg.setAttribute("viewBox","0 0 920 280");svg.setAttribute("tabindex","0");svg.setAttribute("role","img");svg.setAttribute("aria-label","Forecast and actual solar kWh. Hover, tap or use arrow keys");
const shape=(name,attrs,text)=>{const e=document.createElementNS(ns,name);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));if(text!==undefined)e.textContent=String(text);svg.append(e);return e};
const x=t=>L+(t-start)/86400000*(R-L),y=v=>B-v/max*(B-T);
for(let i=0;i<=4;i++){const v=max*i/4,Y=y(v);
shape("line",{x1:L,x2:R,y1:Y,y2:Y,stroke:"currentColor","stroke-opacity":.14});
shape("text",{x:L-8,y:Y+4,fill:"currentColor","font-size":12,"text-anchor":"end"},v.toFixed(0))}
for(let h=0;h<=24;h+=4){shape("text",{x:x(start+h*3600000),y:266,fill:"currentColor","font-size":12,"text-anchor":h===0?"start":h===24?"end":"middle"},String(h).padStart(2,"0")+":00")}
shape("text",{x:13,y:13,fill:"currentColor","font-size":12},"kWh");
for(const [data,color] of [[forecast,"#e6b650"],[actual,"#59a9eb"]]){
let segment=[],previous=null;
const flush=()=>{if(segment.length>1)shape("path",{d:segment.map((q,i)=>(i?"L":"M")+x(q.t).toFixed(1)+","+y(q.v).toFixed(1)).join(" "),fill:"none",stroke:color,"stroke-width":2.6});segment=[]};
for(const q of data){if(q.t<start||q.t>start+86400000)continue;if(previous!==null&&q.t-previous>45*60000)flush();segment.push(q);previous=q.t}flush()}
const cursor=shape("line",{x1:L,x2:L,y1:T,y2:B,stroke:"currentColor","stroke-dasharray":"4 4",visibility:"hidden"});
shape("rect",{x:L,y:T,width:R-L,height:B-T,fill:"transparent","pointer-events":"all"});
const tip=el("div","tooltip","Hover or tap for actual and predicted energy; blue is recorded, yellow is forecast.");
let frac=.5;
const inspect=v=>{frac=Math.max(0,Math.min(1,Math.round(v*288)/288));const t=start+frac*86400000,xx=x(t);
cursor.setAttribute("x1",xx);cursor.setAttribute("x2",xx);cursor.setAttribute("visibility","visible");tip.replaceChildren();
tip.append(el("strong","",new Date(t).toLocaleTimeString(undefined,{hour:"2-digit",minute:"2-digit"})));
const predicted=forecast.filter(q=>q.t<=t).at(-1);
const nearest=actual.reduce((a,q)=>!a||Math.abs(q.t-t)<Math.abs(a.t-t)?q:a,null);
const measured=nearest&&Math.abs(nearest.t-t)<=10*60000?nearest:null;
const pred=el("span","", "Forecast: "+(predicted?units(predicted.v,"kWh"):"—"));
const act=el("span","", "Actual: "+(measured?units(measured.v,"kWh"):"no nearby reading"));
pred.style.color="#e6b650";act.style.color="#59a9eb";tip.append(pred,act)};
const pointer=e=>{const b=svg.getBoundingClientRect();if(b.width)inspect(((e.clientX-b.left)/b.width*920-L)/(R-L))};
svg.addEventListener("pointermove",pointer);svg.addEventListener("pointerdown",pointer);
svg.addEventListener("keydown",e=>{if(!["ArrowLeft","ArrowRight"].includes(e.key))return;e.preventDefault();inspect(frac+(e.key==="ArrowRight"?1:-1)/288)});
pane.append(svg,tip,el("p","muted note","Actual = inverter daily solar counter recorded by Home Assistant. Missing hours are not filled. Forecast = Open-Meteo projected hourly production, which may change as weather forecasts refresh."));
if(this.actualError)pane.append(el("p","muted",this.actualError));
return pane}
forecast(){
const p=this.panel("Solar forecast","Weather-based prediction · read-only"),stats=el("div","stats");
for(const [name,key] of [["Today","forecast"],["Remaining today","remaining"],["Tomorrow","tomorrow"],["Next 7 days","week"]]){
const box=el("div","stat");append(box,el("span","muted",name),el("strong","",units(this.num(key),"kWh")));stats.append(box)}
p.append(stats);const sensor=this.state("forecast");
const draw=(title,data,field,flag)=>{const detail=el("details");detail.open=this.expanded[flag];detail.addEventListener("toggle",()=>this.expanded[flag]=detail.open);
detail.append(el("summary","",title));const rows=el("div","rows"),tip=el("div","tooltip","Hover or tap a row to inspect energy");
const max=Math.max(1,...data.map(v=>Number(v.kwh)||0));
for(const d of data){const n=Number(d.kwh),name=d[field]||"—",row=el("div","day"),bar=el("div","bar"),fill=el("span");
fill.style.width=(Number.isFinite(n)?Math.max(0,n):0)/max*100+"%";bar.append(fill);
append(row,el("span","",name),bar,el("strong","",units(Number.isFinite(n)?n:null,"kWh")));row.tabIndex=0;
const show=()=>tip.textContent=name+": "+units(Number.isFinite(n)?n:null,"kWh")+(d.cloud==null?"":" · cloud "+d.cloud+"%");
for(const event of ["pointerenter","pointerdown","focus","click"])row.addEventListener(event,show);
rows.append(row)}detail.append(append(rows,tip));return detail};
p.append(draw("Seven-day outlook",Array.isArray(sensor?.attributes?.daily)?sensor.attributes.daily:[],"date","days"));
p.append(draw("Hourly outlook",Array.isArray(sensor?.attributes?.hourly)?sensor.attributes.hourly:[],"time","hours"));
p.append(el("p","muted note",(this.state("learning")?.state||"Learning pending")+" · Estimates depend on weather, shading and curtailment."));
return p}
guide(){
const shell=el("details");shell.open=this.expanded.guide;shell.addEventListener("toggle",()=>this.expanded.guide=shell.open);
shell.append(el("summary","","Home Assistant Energy · Sensor IDs & copy"));
const categories=[
["Grid",[["Imported energy · kWh","import"],["Exported energy · kWh","export"],["Signed power · W","signed"],["Import power · W","importPower"],["Export power · W","exportPower"]]],
["Solar",[["Solar production energy · kWh","solarTotal"],["Solar power · W","pv"],["Solar forecast · kWh","forecast"]]],
["Battery",[["Energy charged · kWh","chargeTotal"],["Energy discharged · kWh","dischargeTotal"],["State of charge · %","soc"],["Battery power · W","battery"]]],
["Home",[["Home energy · kWh","homeTotal"],["Home power · W","home"]]]
];
const grid=el("div","guide");
for(const [title,items] of categories){const col=el("section","group");col.append(el("h4","",title));
for(const [label,key] of items){const sensor=this.state(key),item=el("div","item"),row=el("div","copyRow"),input=el("input"),copy=el("button","","Copy");
append(item,el("label","",label),el("small","",sensor?.attributes?.friendly_name||"Not available"));
input.type="text";input.readOnly=true;input.value=sensor?.entity_id||"Unavailable";input.setAttribute("aria-label",label+" entity ID");
if(sensor)input.addEventListener("click",()=>input.select());copy.disabled=!sensor;
if(sensor)copy.addEventListener("click",async()=>{try{await navigator.clipboard.writeText(sensor.entity_id);copy.textContent="Copied ✓"}catch(_){input.focus();input.select();try{document.execCommand("copy");copy.textContent="Copied ✓"}catch(_){copy.textContent="Select ID"}}});
append(row,input,copy);item.append(row);col.append(item)}grid.append(col)}
shell.append(grid,el("p","muted note","These are actual Home Assistant entity IDs. W is instantaneous power, kWh is accumulated energy. Grid power polarity and import/export estimates remain provisional."));return shell}
render(){
if(!this.shadowRoot||!this.hassObj)return;
const focus=this.shadowRoot.activeElement;if(focus?.tagName==="INPUT"&&focus.type==="text")return;
const style=el("style");style.textContent=css;const app=el("div","app"),head=el("div","head");
const solar=this.state("pv"),connected=solar&&!["unknown","unavailable"].includes(String(solar.state));
append(head,el("h2","","SAJ Energy"),el("span",connected?"good":"bad",connected?"● Connected to inverter":"● Monitoring unavailable"));
const refresh=el("button","","↻ Refresh");refresh.addEventListener("click",()=>{this.updated=0;this.loadHistory(true)});head.append(refresh);
append(app,head,this.live(),this.history(),this.forecast(),this.forecastChart(),this.guide());this.shadowRoot.replaceChildren(style,app)}
}
if(!customElements.get("saj-safe-monitor-card"))customElements.define("saj-safe-monitor-card",Monitor);
window.customCards=window.customCards||[];window.customCards.push({type:"saj-safe-monitor-card",name:"SAJ Energy Monitor",description:"Read-only live energy, historic data, forecast and sensor guide"});
})();
