"""Optional read-only grid energy estimator; retains measurements across restarts.

Grid direction remains UNVERIFIED; these are accumulated monitored intervals,
not the utility's certified import/export meter. Existing SAJ monitor keys,
inverter reads and settings remain untouched.
"""
from datetime import datetime, timezone
from homeassistant.helpers.storage import Store


class GridTotals:
    def __init__(self,hass,entry):
        self.store=Store(hass,1,f"saj_h2_safe_grid_totals_{entry.entry_id}")
        self.import_kwh=0.0
        self.export_kwh=0.0
        self.import_today=0.0
        self.export_today=0.0
        self.day=None
        self.last_time=None
        self.last_power=None
        self.last_save=None
        self.tz=hass.config.time_zone or "Australia/Adelaide"

    async def load(self):
        from zoneinfo import ZoneInfo
        saved=await self.store.async_load() or {}
        self.import_kwh=max(0.0,float(saved.get("import_kwh",0)))
        self.export_kwh=max(0.0,float(saved.get("export_kwh",0)))
        today=datetime.now(ZoneInfo(self.tz)).date().isoformat()
        self.day=today
        if saved.get("day")==today:
            self.import_today=max(0.0,float(saved.get("import_today",0)))
            self.export_today=max(0.0,float(saved.get("export_today",0)))

    def sample(self,when,watts):
        from zoneinfo import ZoneInfo
        date=when.astimezone(ZoneInfo(self.tz)).date().isoformat()
        if self.day!=date:
            self.day=date
            self.import_today=self.export_today=0.0
            self.last_time=self.last_power=None
        if not isinstance(watts,(int,float)):
            self.last_time=self.last_power=None
            return
        if self.last_time is not None and self.last_power is not None:
            dt=(when-self.last_time).total_seconds()
            if 0<dt<=60:
                # Linear crossing zero splits imported and exported energy.
                p0=self.last_power
                p1=float(watts)
                if p0*p1<0:
                    t0=dt*abs(p0)/(abs(p0)+abs(p1))
                    imp=(max(0,p0)*t0/2+max(0,p1)*(dt-t0)/2)/3600000
                    exp=(max(0,-p0)*t0/2+max(0,-p1)*(dt-t0)/2)/3600000
                else:
                    avg=(p0+p1)/2
                    imp=max(avg,0)*dt/3600000
                    exp=max(-avg,0)*dt/3600000
                self.import_kwh+=imp
                self.export_kwh+=exp
                self.import_today+=imp
                self.export_today+=exp
        self.last_time=when
        self.last_power=float(watts)

    async def save(self):
        await self.store.async_save({
            "import_kwh":self.import_kwh,
            "export_kwh":self.export_kwh,
            "import_today":self.import_today,
            "export_today":self.export_today,
            "day":self.day,
        })

    def populate(self,data):
        data["grid_energy_imported_estimated"]=round(self.import_kwh,5)
        data["grid_energy_exported_estimated"]=round(self.export_kwh,5)
        data["grid_imported_today_estimated"]=round(self.import_today,5)
        data["grid_exported_today_estimated"]=round(self.export_today,5)
        data["grid_power_signed_import_export"]=data.get("grid_power")
