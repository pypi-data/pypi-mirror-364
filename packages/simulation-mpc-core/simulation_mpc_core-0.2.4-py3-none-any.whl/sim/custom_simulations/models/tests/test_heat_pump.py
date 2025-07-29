from unittest import TestCase

import numpy as np
import pandas as pd

from src.imby.sim.custom_simulations import MPCModel
from src.imby.sim.custom_simulations.models.demand import HeatDemandModel
from src.imby.sim.custom_simulations.models.heat_pump import (
    ElectricityDrivenHeatPumpModel,
    ElectricityDrivenHeatPumpMultiCOPModel,
    MitsubishiEcodanXSpaceHeatingDHWHeatPumpModel,
)
from src.imby.sim.custom_simulations.models.heat_storage import (
    StratifiedStorageTankModel,
)


class TestElectricityDrivenHeatPumpModel(TestCase):
    def test_solution(self):
        model = MPCModel(
            component_models=[
                HeatDemandModel("demand"),
                StratifiedStorageTankModel("storage"),
                ElectricityDrivenHeatPumpModel("heat_pump"),
            ],
            flow_connections=[
                ("demand.heat", "heat_pump.condenser_heat", "storage.heat")
            ],
            objective_variables=["heat_pump.power"],
        )

        timestamps = 1528090200 + 900 * np.arange(24 * 4)
        on_committed = np.nan * np.ones(len(timestamps))
        on_committed[0] = 1

        data = pd.DataFrame(
            data={
                "demand.heat": 7e3,
                "heat_pump.heat_max": 10e3,
                "heat_pump.heat_min": 5e3,
                "heat_pump.on_committed": on_committed,
                "storage.temperature_max": 80,
                "storage.temperature_min": 50,
            },
            index=pd.to_datetime(timestamps, unit="s"),
        )
        par = {
            "heat_pump.minimum_on_time": 3600,
            "heat_pump.minimum_off_time": 3600,
            "heat_pump.last_on_change": 1528090200 - 3600,
            "storage.volume": 5,
        }
        ini = {"storage.temperature": 60, "heat_pump.on": 0}
        result = model.solve(data, par, ini)
        # print(result)
        self.assertEqual(result["heat_pump.on"][0], 1)
        self.assertEqual(result["heat_pump.on"][1], 1)
        self.assertEqual(result["heat_pump.on"][2], 1)
        self.assertEqual(result["heat_pump.on"][3], 1)


class TestElectricityDrivenHeatPumpMultiCOPModel(TestCase):
    def test_solution(self):
        model = MPCModel(
            component_models=[
                HeatDemandModel("demand"),
                StratifiedStorageTankModel("storage"),
                ElectricityDrivenHeatPumpMultiCOPModel(
                    "heat_pump", cop_index=["50", "100"]
                ),
            ],
            flow_connections=[
                ("demand.heat", "heat_pump.condenser_heat", "storage.heat")
            ],
            objective_variables=["heat_pump.power"],
        )

        timestamps = 1528090200 + 900 * np.arange(24 * 4)
        on_committed_50 = np.nan * np.ones(len(timestamps))
        on_committed_50[0] = 0
        on_committed_100 = np.nan * np.ones(len(timestamps))
        on_committed_100[0] = 1

        data = pd.DataFrame(
            data={
                "demand.heat": 7e3,
                "heat_pump.50.heat_max": 5e3,
                "heat_pump.50.heat_min": 5e3,
                "heat_pump.100.heat_max": 5e3,
                "heat_pump.100.heat_min": 5e3,
                "heat_pump.50.on_committed": on_committed_50,
                "heat_pump.100.on_committed": on_committed_100,
                "storage.temperature_max": 80,
                "storage.temperature_min": 50,
            },
            index=pd.to_datetime(timestamps, unit="s"),
        )
        par = {
            "heat_pump.50.minimum_on_time": 3600,
            "heat_pump.50.minimum_off_time": 3600,
            "heat_pump.50.last_on_change": 1528090200 - 3600,
            "heat_pump.100.minimum_on_time": 3600,
            "heat_pump.100.minimum_off_time": 3600,
            "heat_pump.100.last_on_change": 1528090200 - 5 * 3600,
            "heat_pump.minimum_on_time": 0,
            "heat_pump.minimum_off_time": 3600,
            "heat_pump.last_on_change": 1528090200 - 3600,
            "storage.volume": 5,
        }
        ini = {
            "storage.temperature": 60,
            "heat_pump.on": 0,
            "heat_pump.50.on": 0,
            "heat_pump.100.on": 0,
        }
        result = model.solve(data, par, ini)
        # print(result)
        # print(result[['heat_pump.50.condenser_heat', 'heat_pump.100.condenser_heat', 'heat_pump.condenser_heat']])
        # print(result[['heat_pump.50.on', 'heat_pump.100.on', 'heat_pump.on']])
        self.assertEqual(result["heat_pump.100.on"][0], 1)
        self.assertEqual(result["heat_pump.100.on"][1], 1)
        self.assertEqual(result["heat_pump.100.on"][2], 1)
        self.assertEqual(result["heat_pump.100.on"][3], 1)


class TestMitsubishiEcodanXSpaceHeatingDHWHeatPumpModel(TestCase):
    def test_solution(self):
        model = MPCModel(
            component_models=[
                HeatDemandModel("sh_demand"),
                HeatDemandModel("dhw_demand"),
                StratifiedStorageTankModel("dhw_storage"),
                MitsubishiEcodanXSpaceHeatingDHWHeatPumpModel("heat_pump"),
            ],
            flow_connections=[
                ("sh_demand.heat", "heat_pump.sh.condenser_heat"),
                (
                    "dhw_demand.heat",
                    "dhw_storage.heat",
                    "heat_pump.dhw.condenser_heat",
                ),
            ],
            objective_variables=["heat_pump.power"],
        )

        timestamps = 1528090200 + 900 * np.arange(24 * 4)
        on_committed_sh = np.nan * np.ones(len(timestamps))
        on_committed_dhw = np.nan * np.ones(len(timestamps))
        sh_demand_heat = np.zeros(len(timestamps))
        sh_demand_heat[0:20] = 3e3
        sh_demand_heat[-20:-1] = 3e3
        dhw_demand_heat = np.zeros(len(timestamps))
        dhw_demand_heat[-16:-12] = 2e3

        data = pd.DataFrame(
            data={
                "sh_demand.heat": sh_demand_heat,
                "dhw_demand.heat": dhw_demand_heat,
                "heat_pump.sh.water_temperature": 35.0,
                "heat_pump.dhw.water_temperature": 55.0,
                "heat_pump.sh.on_committed": on_committed_sh,
                "heat_pump.dhw.on_committed": on_committed_dhw,
                "dhw_storage.temperature_max": 55.0,
                "dhw_storage.temperature_min": 45.0,
                "heat_pump.ambient_temperature": 8.0 + 2 * np.sin(
                    timestamps / 3600 / 24
                ),
            },
            index=pd.to_datetime(timestamps, unit="s"),
        )
        par = {"dhw_storage.volume": 0.3}
        ini = {"dhw_storage.temperature": 50}
        result = model.solve(data, par, ini)
        # print(result)

        self.assertEqual(result["heat_pump.sh.on"][0], 1)
        self.assertEqual(result["heat_pump.sh.on"][19], 1)
        self.assertEqual(result["heat_pump.sh.on"][-16], 1)
        self.assertEqual(result["heat_pump.sh.on"][-2], 1)
