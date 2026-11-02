"""Offline read-only kWh, identity, and dashboard invariants."""
from datetime import datetime, timezone, timedelta
import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parents[1]
COMP=ROOT/"custom_components"/"saj_h2_safe"


class FakeStore:
    saved={}
    def __init__(self,hass,version,key):
        self.key=key
    async def async_load(self):
        return self.saved.get(self.key)
    async def async_save(self,value):
        self.saved[self.key]=dict(value)


def grid_totals_class():
    tree=ast.parse((COMP/"grid_totals.py").read_text())
    cls=next(n for n in tree.body
             if isinstance(n,ast.ClassDef) and n.name=="GridTotals")
    scope={"Store":FakeStore,"datetime":datetime,"timezone":timezone}
    exec(compile(ast.Module(body=[cls],type_ignores=[]),
                 str(COMP/"grid_totals.py"),"exec"),scope)
    return scope["GridTotals"]


class MonitoringTests(unittest.TestCase):
    def setUp(self):
        FakeStore.saved.clear()
        self.hass=SimpleNamespace(config=SimpleNamespace(time_zone="Australia/Adelaide"))
        self.entry=SimpleNamespace(entry_id="test_abc")

    def test_grid_signed_zero_crossing_and_restart(self):
        async def task():
            g=grid_totals_class()(self.hass,self.entry)
            await g.load()
            date=datetime(2026,11,2,8,0,tzinfo=timezone.utc)
            g.sample(date,1000)
            g.sample(date+timedelta(seconds=30),1000)
            self.assertAlmostEqual(g.import_kwh,1/120,places=6)
            g.sample(date+timedelta(seconds=60),-1000)
            self.assertGreater(g.export_kwh,0)
            previous=g.import_kwh
            g.sample(date+timedelta(hours=2),-1000)
            self.assertEqual(g.import_kwh,previous,"large telemetry gap cannot synthesize kWh")
            await g.save()
            restored=grid_totals_class()(self.hass,self.entry)
            await restored.load()
            self.assertAlmostEqual(restored.import_kwh,g.import_kwh)
            self.assertAlmostEqual(restored.export_kwh,g.export_kwh)
            data={"grid_power":-250}
            restored.populate(data)
            self.assertEqual(data["grid_power_signed_import_export"],-250)
            self.assertEqual(data["grid_energy_imported_estimated"],round(g.import_kwh,5))
            self.assertEqual(data["grid_energy_exported_estimated"],round(g.export_kwh,5))
        asyncio.run(task())

    def test_rollback_restores_original_card_and_cleans_only_our_resources(self):
        setup=(COMP/"frontend_setup.py").read_text()
        js=(COMP/"frontend"/"saj-safe-monitor-card.js").read_text()
        manifest=(COMP/"manifest.json").read_text()
        self.assertIn('"/saj-h2-safe/v040/saj-safe-monitor-card.js"',setup)
        self.assertIn('add_extra_js_url(hass, URL)',setup)
        self.assertIn('async_cleanup_newer_card_resource',setup)
        self.assertIn('"/saj-h2-safe/v041/saj-safe-monitor-card.js"',setup)
        self.assertIn('"/saj-h2-safe/v042/saj-safe-monitor-card.js"',setup)
        self.assertIn('resource.get("url") in old_urls',setup)
        self.assertNotIn('await resources.async_delete_item(resource["id"])',setup.split("for resource in list(resources.async_items()):")[0])
        self.assertIn('"version": "0.4.0"',manifest)
        self.assertNotIn("v0.4.2",js)

    def test_readonly_and_existing_sensor_contract(self):
        raw=(COMP/"__init__.py").read_text()
        sensor=(COMP/"sensor.py").read_text()
        const=(COMP/"const.py").read_text()
        flow=(COMP/"config_flow.py").read_text()
        ui=(COMP/"frontend"/"saj-safe-monitor-card.js").read_text()
        for forbidden in ("write_register(","write_registers(",
                          "write_coil(","write_coils("):
            self.assertNotIn(forbidden,raw)
            self.assertNotIn(forbidden,flow)
        for key in ("battery_soc","total_pv_power","home_load_power",
                    "battery_power","grid_power","battery_charge"):
            self.assertIn(key,const)
        mappings={}
        exec(compile(const,str(COMP/"const.py"),"exec"),mappings)
        self.assertIn("solar_today",mappings["ENERGY_KEYS"])
        self.assertIn("battery_charge_today",mappings["ENERGY_KEYS"])
        for key in ("grid_energy_imported_estimated","grid_energy_exported_estimated",
                    "grid_imported_today_estimated","grid_power_signed_import_export"):
            self.assertIn(key,sensor)
        self.assertIn("await discover(self.hass)",flow)
        self.assertIn("async_ensure_dashboard(hass)",raw)
        self.assertIn("Home Assistant Energy",ui)
        self.assertIn("Actual vs projected",ui)
        self.assertIn("10 minutes",ui)
        self.assertNotIn("call_service",ui)
        self.assertFalse((ROOT/"dashboards"/"saj-energy.yaml").exists())
        self.assertTrue((ROOT/"hacs.json").exists())
        self.assertTrue((ROOT/"scripts"/"install.sh").exists())


if __name__=="__main__":
    unittest.main()
