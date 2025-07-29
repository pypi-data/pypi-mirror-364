from unittest import TestCase

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.imby.sim.custom_simulations import MPCModel
from src.imby.sim.custom_simulations.models.battery import BatteryModel
from src.imby.sim.custom_simulations.models.demand import PowerDemandModel
from src.imby.sim.custom_simulations.models.power_grid import (
    CorrectingSoftPowerConstraintModel,
    GridModel,
    SoftPowerConstraintModel,
)
from src.imby.sim.custom_simulations.tests.mocks import mock_demand_power

_plot = False


class TestSoftPowerConstraintModel(TestCase):
    @staticmethod
    def create_model():
        model = MPCModel(
            component_models=[
                SoftPowerConstraintModel(
                    "load_following",
                    power_soft_min_index=["0", "1"],
                    power_soft_max_index=["0", "1"],
                ),
                GridModel("grid"),
                BatteryModel("battery"),
                PowerDemandModel("demand"),
            ],
            flow_connections=[
                ("grid.power", "demand.power", "battery.power"),
                ("load_following.power", "demand.power", "battery.power"),
            ],
            objective_variables=[
                "grid.operational_cost",
                "battery.operational_cost",
            ],
            constraint_violation_variables=["load_following.constraint_violation"],
        )
        since = 1537437600
        timestamps = np.arange(since, since + 3 * 24 * 3600, 900)
        index = pd.to_datetime(timestamps, unit="s")
        data = pd.DataFrame(
            data={
                "grid.consumption_price": 0.2,
                "grid.production_price": 0.2,
                "battery.energy_max": 100 * 3.6e6,
                "battery.charge_power_max": 50e3,
                "battery.discharge_power_max": 50e3,
                "demand.power": mock_demand_power(timestamps, scale=40e3),
                "load_following.power_max_constraint_violation_scale": 0.5,
                "load_following.power_min_constraint_violation_scale": 0.5,
                "load_following.power_soft_max_0": np.nan,
                "load_following.power_soft_max_1": np.nan,
                "load_following.power_soft_min_0": np.nan,
                "load_following.power_soft_min_1": np.nan,
            },
            index=index,
        )
        par = {}
        ini = {}
        return model, timestamps, data, par, ini

    def test_soft_power_constraint_model_min_max_too_strict(self):
        model, timestamps, data, par, ini = self.create_model()

        data.loc[
            data.index[48] : data.index[144], "load_following.power_soft_max_0"
        ] = 40e3
        data.loc[
            data.index[48] : data.index[144], "load_following.power_soft_max_1"
        ] = 45e3
        data.loc[
            data.index[48] : data.index[144], "load_following.power_soft_min_0"
        ] = 20e3
        data.loc[
            data.index[48] : data.index[144], "load_following.power_soft_min_1"
        ] = 25e3

        result = model.solve(data, par, ini, tee=_plot)
        self.assertEqual(sum(result["optimizer_termination_condition"]), 0)
        self.assertGreaterEqual(
            np.nanmin(result["load_following.power_soft_max_1"] - result["grid.power"]),
            0,
        )

        if _plot:
            model.plot()


class TestCorrectingSoftPowerConstraintModel(TestCase):
    @staticmethod
    def create_model():
        model = MPCModel(
            component_models=[
                CorrectingSoftPowerConstraintModel(
                    "load_following",
                    power_soft_min_index=["0", "1"],
                    power_soft_max_index=["0", "1"],
                ),
                GridModel("grid"),
                BatteryModel("battery"),
                PowerDemandModel("demand"),
            ],
            flow_connections=[
                ("grid.power", "demand.power", "battery.power"),
                ("load_following.power", "demand.power", "battery.power"),
            ],
            objective_variables=[
                "grid.operational_cost",
                "battery.operational_cost",
            ],
            constraint_violation_variables=["load_following.constraint_violation"],
        )
        since = 1537437600
        timestamps = np.append(
            [since, since + 300],
            np.arange(since + 900, since + 3 * 24 * 3600, 900),
        )
        index = pd.to_datetime(timestamps, unit="s")
        data = pd.DataFrame(
            data={
                "grid.consumption_price": 0.2,
                "grid.production_price": 0.2,
                "battery.energy_max": 100 * 3.6e6,
                "battery.charge_power_max": 50e3,
                "battery.discharge_power_max": 50e3,
                "demand.power": mock_demand_power(timestamps, scale=40e3),
                "load_following.power_max_constraint_violation_scale": 0.5,
                "load_following.power_min_constraint_violation_scale": 0.5,
                "load_following.power_soft_max_0": np.nan,
                "load_following.power_soft_max_1": np.nan,
                "load_following.power_soft_min_0": np.nan,
                "load_following.power_soft_min_1": np.nan,
                "load_following.power_past": np.nan,
                "load_following.constraint_indices": [[0, 1], [0, 1]] + [
                    [i] for i in range(2, len(timestamps))
                ],
            },
            index=index,
        )
        par = {}
        ini = {}
        return model, timestamps, data, par, ini

    def test_soft_power_constraint_model_min_max_too_strict_no_past_value(
        self,
    ):
        model, timestamps, data, par, ini = self.create_model()

        data.loc[
            data.index[48] : data.index[144], "load_following.power_soft_max_0"
        ] = 40e3
        data.loc[
            data.index[48] : data.index[144], "load_following.power_soft_max_1"
        ] = 45e3
        data.loc[
            data.index[48] : data.index[144], "load_following.power_soft_min_0"
        ] = 20e3
        data.loc[
            data.index[48] : data.index[144], "load_following.power_soft_min_1"
        ] = 25e3

        result = model.solve(data, par, ini, tee=_plot)
        if _plot:
            model.plot(result)

    def test_soft_power_constraint_model_min_max_too_strict_past_value(self):
        model, timestamps, data, par, ini = self.create_model()

        data.loc[
            data.index[48] : data.index[144], "load_following.power_soft_max_0"
        ] = 40e3
        data.loc[
            data.index[48] : data.index[144], "load_following.power_soft_max_1"
        ] = 45e3
        data.loc[
            data.index[48] : data.index[144], "load_following.power_soft_min_0"
        ] = 20e3
        data.loc[
            data.index[48] : data.index[144], "load_following.power_soft_min_1"
        ] = 25e3
        data.loc[data.index[0], "load_following.power_past"] = 60e3

        result = model.solve(data, par, ini, tee=_plot)
        if _plot:
            model.plot(result)


if __name__ == "__main__":
    _plot = True

    tester = TestSoftPowerConstraintModel()
    tester.setUp()
    # tester.test_soft_power_constraint_model_min_max_too_strict()
    tester.tearDown()

    tester = TestCorrectingSoftPowerConstraintModel()
    tester.setUp()
    tester.test_soft_power_constraint_model_min_max_too_strict_no_past_value()
    # tester.test_soft_power_constraint_model_min_max_too_strict_past_value()
    tester.tearDown()

    plt.show()
