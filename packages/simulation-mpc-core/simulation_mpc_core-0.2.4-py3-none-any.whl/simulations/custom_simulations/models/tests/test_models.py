from unittest import TestCase

import numpy as np
import pandas as pd

from src.imby.sim.custom_simulations import MPCModel
from src.imby.sim.custom_simulations.models.battery import BatteryModel
from src.imby.sim.custom_simulations.models.building import BuildingModel
from src.imby.sim.custom_simulations.models.demand import (
    HeatDemandModel,
    PowerDemandModel,
)
from src.imby.sim.custom_simulations.models.ev import ChargePointModelDeprecated
from src.imby.sim.custom_simulations.models.heat_pump import (
    ElectricityDrivenHeatPumpModel,
)
from src.imby.sim.custom_simulations.models.heat_storage import (
    StratifiedStorageTankModel,
)
from src.imby.sim.custom_simulations.models.power_grid import GridModel
from src.imby.sim.custom_simulations.models.pv import PVModel


class ModelsTest(TestCase):
    def setUp(self):
        np.random.seed(0)

    def test_pv(self):
        grid = GridModel("grid")
        pv = PVModel("pv")
        model = MPCModel(
            component_models=[grid, pv],
            flow_connections=[("grid.power", "pv.power")],
            objective_variables=["grid.operational_cost"],
        )
        index = pd.to_datetime(np.arange(0, 3600, 900), unit="s")
        data = pd.DataFrame(
            data={
                "grid.consumption_price": 0.2,
                "grid.production_price": 0.2,
                "grid.consumption_power_max": 100e3,
                "grid.production_power_max": 100e3,
                "pv.power_max": 0.8 * np.random.random(len(index)),
            },
            index=index,
        )
        result = model.solve(data)
        self.assertEqual(sum(result["optimizer_termination_condition"]), 0)

    def test_battery(self):
        grid = GridModel("grid")
        battery = BatteryModel("battery")
        model = MPCModel(
            component_models=[grid, battery],
            flow_connections=[("grid.power", "battery.power")],
            objective_variables=[
                "grid.operational_cost",
                "battery.operational_cost",
            ],
        )
        index = pd.to_datetime(np.arange(0, 3600, 900), unit="s")
        data = pd.DataFrame(
            data={
                "grid.consumption_price": 0.2,
                "grid.production_price": 0.2,
                "grid.consumption_power_max": 100e3,
                "grid.production_power_max": 100e3,
                "battery.energy_max": 100 * 3.6e6,
                "battery.charge_power_max": 50e3,
                "battery.discharge_power_max": 50e3,
            },
            index=index,
        )
        par = {}
        ini = {}
        result = model.solve(data, par, ini)
        self.assertEqual(sum(result["optimizer_termination_condition"]), 0)

    def test_building_heat_pump_space_heating(self):
        grid = GridModel("grid")
        heat_pump = ElectricityDrivenHeatPumpModel("heat_pump")
        building = BuildingModel("building")
        model = MPCModel(
            component_models=[grid, heat_pump, building],
            flow_connections=[("heat_pump.condenser_heat", "building.heat")],
            objective_variables=["grid.operational_cost"],
        )
        index = pd.to_datetime(np.arange(0, 3600, 900), unit="s")
        df = pd.DataFrame(
            data={
                "grid.consumption_price": 0.2,
                "grid.production_price": 0.2,
                "grid.consumption_power_max": 100e3,
                "grid.production_power_max": 100e3,
                "heat_pump.COP": 3.0,
                "heat_pump.heat_max": 10000.0,
                "heat_pump.heat_min": 1000.0,
                "building.outdoor_temperature": 1.0,
                "building.temperature_min": 20.0,
                "building.temperature_max": 22.0,
                "building.C": 40e6,
                "building.heat_loss_UA": 100.0,
            },
            index=index,
        )
        par = {}
        ini = {
            "building.temperature": 20.0,
            "heat_pump.on": 0,
        }
        result = model.solve(df, par, ini)
        self.assertEqual(sum(result["optimizer_termination_condition"]), 0)

    def test_power_demand(self):
        demand = PowerDemandModel("demand")
        grid_model = GridModel("grid")
        model = MPCModel(
            component_models=[demand, grid_model],
            flow_connections=[("grid.power", "demand.power")],
            objective_variables=["grid.operational_cost"],
        )

        index = pd.to_datetime(np.arange(0, 3600, 900), unit="s")
        data = pd.DataFrame(
            data={
                "grid.consumption_price": 0.2,
                "grid.production_price": 0.2,
                "grid.consumption_power_max": 100e3,
                "grid.production_power_max": 100e3,
                "demand.power": 1 + np.random.random(len(index)),
            },
            index=index,
        )
        result = model.solve(data)
        self.assertEqual(sum(result["optimizer_termination_condition"]), 0)

    def test_charging_station(self):
        grid = GridModel("grid")
        charging_station = ChargePointModelDeprecated("charge_point")
        model = MPCModel(
            component_models=[grid, charging_station],
            flow_connections=[("grid.power", "charge_point.power")],
            objective_variables=[
                "grid.operational_cost",
                "charge_point.operational_cost",
            ],
        )
        index = pd.to_datetime(np.arange(0, 3600, 900), unit="s")
        data = pd.DataFrame(
            data={
                "grid.consumption_price": 0.2,
                "grid.production_price": 0.2,
                "grid.consumption_power_max": 100e3,
                "grid.production_power_max": 100e3,
                "charge_point.connected": 1,
                "charge_point.energy_max": 100 * 3.6e6,
                "charge_point.energy_min": 0,
                "charge_point.charge_power_max": 50e3,
                "charge_point.discharge_power_max": 0,
                "charge_point.battery_efficiency": 0.8,
                "charge_point.battery_capacity_cost_per_cycle": 0.0,
                "charge_point.battery_self_discharge": 0.0,
            },
            index=index,
        )
        par = {}
        ini = {}
        result = model.solve(data, par, ini)
        self.assertEqual(sum(result["optimizer_termination_condition"]), 0)

    def test_heat_pump_heat_demand(self):
        grid = GridModel("grid")
        heat_pump = ElectricityDrivenHeatPumpModel("heat_pump")
        demand = HeatDemandModel("demand")

        model = MPCModel(
            component_models=[grid, heat_pump, demand],
            flow_connections=[
                ("grid.power", "heat_pump.power"),
                ("heat_pump.condenser_heat", "demand.heat"),
            ],
            objective_variables=[
                "grid.operational_cost",
                "heat_pump.operational_cost",
            ],
        )
        index = pd.to_datetime(np.arange(0, 3600, 900), unit="s")
        data = pd.DataFrame(
            data={
                "grid.consumption_price": 0.2,
                "grid.production_price": 0.2,
                "grid.consumption_power_max": 10e3,
                "grid.production_power_max": 10e3,
                "heat_pump.heat_max": 10e3,
                "heat_pump.COP": 3,
                "demand.heat": 8e3 * np.random.random(len(index)),
            },
            index=index,
        )
        result = model.solve(data)
        self.assertEqual(sum(result["optimizer_termination_condition"]), 0)

    def test_heat_pump_storage_heat_demand(self):
        grid = GridModel("grid")
        heat_pump = ElectricityDrivenHeatPumpModel("heat_pump")
        storage = StratifiedStorageTankModel("storage")
        demand = HeatDemandModel("demand")

        model = MPCModel(
            component_models=[grid, heat_pump, storage, demand],
            flow_connections=[
                ("grid.power", "heat_pump.power"),
                ("heat_pump.condenser_heat", "demand.heat", "storage.heat"),
            ],
            objective_variables=[
                "grid.operational_cost",
                "heat_pump.operational_cost",
            ],
        )
        index = pd.to_datetime(np.arange(0, 3600, 900), unit="s")
        data = pd.DataFrame(
            data={
                "grid.consumption_price": 0.2,
                "grid.production_price": 0.2,
                "grid.consumption_power_max": 10e3,
                "grid.production_power_max": 10e3,
                "heat_pump.heat_max": 10e3,
                "heat_pump.COP": 3,
                "storage.temperature_min": 20,
                "storage.temperature_max": 45,
                "demand.heat": 8e3 * np.random.random(len(index)),
            },
            index=index,
        )
        par = {"storage.volume": 1.0}
        result = model.solve(data, par)
        self.assertEqual(sum(result["optimizer_termination_condition"]), 0)
