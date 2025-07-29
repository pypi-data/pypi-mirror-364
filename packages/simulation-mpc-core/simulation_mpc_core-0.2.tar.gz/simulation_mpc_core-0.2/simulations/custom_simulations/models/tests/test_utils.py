from unittest import TestCase

import matplotlib.pyplot as plt
import numpy as np

from src.imby.simulations.custom_simulations import MPCModel
from src.imby.simulations.custom_simulations.models.demand import PowerDemandModel
from src.imby.simulations.custom_simulations.models.power_grid import GridModel
from src.imby.simulations.custom_simulations.models.utils import (
    TimeOfDayBasedConstrainedValueModel,
    TimeOfDayBasedSoftConstrainedValueModel,
)
from src.imby.simulations.custom_simulations.tests.mocks import mock_demand_power

_plot = False


class TestTimeOfDayBasedConstrainedValueModel(TestCase):
    @staticmethod
    def create_model():
        model = MPCModel(
            component_models=[
                GridModel("grid1"),
                GridModel("grid2"),
                PowerDemandModel("demand"),
                TimeOfDayBasedConstrainedValueModel(
                    "time_constraint",
                    constraint_hour=[18, 20],
                    constraint_min=[0, 0],
                    constraint_max=[100e3, 0],
                ),
            ],
            flow_connections=[
                ("grid1.power", "grid2.power", "demand.power"),
            ],
            potential_connections=[("-grid1.power", "time_constraint.value")],
            objective_variables=[
                "grid1.operational_cost",
                "grid2.operational_cost",
            ],
        )
        since = 1537437600
        timestamps = np.arange(since, since + 3 * 24 * 3600, 900)
        data, par, ini = model.get_data(timestamps)

        data["grid1.consumption_price"] = 0.1
        data["grid1.production_price"] = 0.0
        data["grid2.consumption_price"] = 0.2
        data["grid2.production_price"] = 0.0
        data["grid.consumption_power_max"] = 100e3
        data["grid.production_power_max"] = 100e3
        data["demand.power"] = mock_demand_power(timestamps, scale=40e3)

        return model, timestamps, data, par, ini

    def test_time_of_day_constraint(self):
        model, timestamps, data, par, ini = self.create_model()

        result = model.solve(data, par, ini, tee=_plot)
        self.assertEqual(sum(result["optimizer_termination_condition"]), 0)
        self.assertEqual(result["grid2.power"][24], 0)

        if _plot:
            model.plot()


class TestTimeOfDayBasedSoftConstrainedValueModel(TestCase):
    @staticmethod
    def create_model():
        model = MPCModel(
            component_models=[
                GridModel("grid1"),
                GridModel("grid2"),
                PowerDemandModel("demand"),
                TimeOfDayBasedSoftConstrainedValueModel(
                    "time_constraint",
                    constraint_hour=[18, 20],
                    constraint_min=[0, 0],
                    constraint_max=[100e3, 0],
                ),
            ],
            flow_connections=[
                ("grid1.power", "grid2.power", "demand.power"),
            ],
            potential_connections=[("-grid1.power", "time_constraint.value")],
            objective_variables=[
                "grid1.operational_cost",
                "grid2.operational_cost",
            ],
            constraint_violation_variables=["time_constraint.constraint_violation"],
        )
        since = 1537437600
        timestamps = np.arange(since, since + 3 * 24 * 3600, 900)
        data, par, ini = model.get_data(timestamps)

        data["grid1.consumption_price"] = 0.1
        data["grid1.production_price"] = 0.0
        data["grid2.consumption_price"] = 0.2
        data["grid2.production_price"] = 0.0
        data["grid.consumption_power_max"] = 100e3
        data["grid.production_power_max"] = 100e3
        data["demand.power"] = mock_demand_power(timestamps, scale=40e3)

        return model, timestamps, data, par, ini

    def test_time_of_day_constraint(self):
        model, timestamps, data, par, ini = self.create_model()

        result = model.solve(data, par, ini, tee=_plot)
        self.assertEqual(sum(result["optimizer_termination_condition"]), 0)
        # self.assertEqual(result['grid2.power'][24], 0)

        if _plot:
            print(result)
            model.plot()


if __name__ == "__main__":
    _plot = True

    tester = TestTimeOfDayBasedConstrainedValueModel()
    tester.setUp()
    # tester.test_time_of_day_constraint()
    tester.tearDown()

    tester = TestTimeOfDayBasedSoftConstrainedValueModel()
    tester.setUp()
    # tester.test_time_of_day_constraint()
    tester.tearDown()

    plt.show()
