from unittest import TestCase
from unittest.mock import patch

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyomo.environ as pyomo

from src.imby.sim.custom_simulations import MPCModel
from imby.sim.custom_simulations.models.base import ComponentModel, Reals
from src.imby.sim.custom_simulations.models.heat_base import (
    HysteresisControllerModel,
    OnOffComponentModelBase,
)
from src.imby.sim.custom_simulations.models.battery import BatteryModel
from src.imby.sim.custom_simulations.models.demand import PowerDemandModel


class PowerGenerationModel(ComponentModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "power_max",
            self.model.i,
            initialize=lambda m, i: data[(self.namespace("power_max"))][i],
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=Reals,
            bounds=lambda m, i: (-self.power_max[i], 0),
        )
        self.add_parameter(
            "price",
            self.model.i,
            initialize=lambda m, i: data[(self.namespace("price"))][i],
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=Reals,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == -self.price[i] * self.power[i],
        )

    def get_results(self):
        results = super().get_results()
        results[self.namespace("power")] = [
            pyomo.value(self.power[i]) for i in self.model.i
        ]
        return results


class OnOffPowerGenerationModel(OnOffComponentModelBase):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "power_max",
            self.model.i,
            initialize=lambda m, i: data[(self.namespace("power_max"))][i],
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=Reals,
            bounds=lambda m, i: (-self.power_max[i], 0),
        )
        self.add_parameter(
            "price",
            self.model.i,
            initialize=lambda m, i: data[(self.namespace("price"))][i],
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=Reals,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_power_on",
            self.model.i,
            rule=lambda m, i: self.power[i] == -self.on[i] * self.power_max[i],
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == -self.price[i] * self.power[i],
        )


model = MPCModel(
    component_models=[
        OnOffPowerGenerationModel("generation", on_commitment_time=900),
        PowerDemandModel("demand"),
        BatteryModel("battery"),
    ],
    flow_connections=[("demand.power", "generation.power", "battery.power")],
    objective_variables=["generation.operational_cost"],
)


class TestOnOffComponentModel(TestCase):
    @patch(
        "src.imby.simulations.custom_simulations.models.heat_base.get_result",
        new=lambda x: pd.DataFrame(
            data={
                "generation.on": [0, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                "timestamp": [
                    1528090200,
                    1528091100,
                    1528092000,
                    1528092900,
                    1528093800,
                    1528094700,
                    1528095600,
                    1528096500,
                    1528097400,
                    1528098300,
                ],
            }
        ),
    )
    def test_get_on_commitment(self):
        component = model.component_models[0]
        on_committed = component.get_on_commitment(
            [
                1528091100,
                1528092000,
                1528092900,
                1528093800,
                1528094700,
                1528095600,
                1528096500,
                1528097400,
                1528098300,
                1528099200,
            ]
        )
        self.assertEqual(1, on_committed[0])
        self.assertTrue(np.isnan(on_committed[1]))

    def test_on_off(self):
        timestamps = 1528090200 + 900 * np.arange(24 * 4)
        on_committed = np.nan * np.ones(len(timestamps))
        on_committed[0] = 1

        data = pd.DataFrame(
            data={
                "demand.power": 5e3,
                "generation.power_max": 10e3,
                "generation.price": 1,
                "generation.on_committed": on_committed,
                "battery.charge_power_max": 10e3,
                "battery.discharge_power_max": 10e3,
                "battery.energy_max": 40 * 3.6e6,
            },
            index=pd.to_datetime(timestamps, unit="s"),
        )
        par = {
            "generation.minimum_on_time": 3600,
            "generation.minimum_off_time": 3600,
        }
        ini = {"battery.energy": 20 * 3.6e6, "generation.on": 0}

        model.solve(data, par, ini)


class TestHysteresisControllerModel(TestCase):
    def check_hysteresis(self):
        model = MPCModel(
            component_models=[
                PowerGenerationModel("generation"),
                HysteresisControllerModel("controller", large_number=40 * 3.6e6),
                PowerDemandModel("demand"),
                BatteryModel("battery"),
            ],
            flow_connections=[("demand.power", "generation.power", "battery.power")],
            potential_connections=[
                ("controller.state", "battery.energy"),
                ("generation.power", "controller.control"),
            ],
            objective_variables=["generation.operational_cost"],
        )

        timestamps = 1528090200 + 900 * np.arange(24 * 4)

        data = pd.DataFrame(
            data={
                "demand.power": 5e3,
                "generation.power_max": 10e3,
                "generation.price": 1,
                "battery.charge_power_max": 10e3,
                "battery.discharge_power_max": 10e3,
                "battery.energy_max": 40 * 3.6e6,
                "controller.control_on": -8e3,
                "controller.control_off": 0,
                "controller.switch_on_state": 15 * 3.6e6,
                "controller.switch_off_state": 20 * 3.6e6,
            },
            index=pd.to_datetime(timestamps, unit="s"),
        )
        par = {
            "generation.minimum_on_time": 0,
            "generation.minimum_off_time": 0,
        }
        ini = {"battery.energy": 22 * 3.6e6, "generation.on": 0}

        result = model.solve(data, par, ini, tee=True)
        fig, (ax1, ax2) = plt.subplots(2, 1)
        ax1.plot(result.index, result["battery.energy"] / 3.6e6)
        ax1.plot(result.index, result["controller.state"] / 3.6e6, "--")

        ax2.plot(result.index, result["generation.power"])
        ax2.plot(result.index, result["controller.control"], "--")
        ax2.plot(result.index, 1000 * result["controller.on"])

        plt.show()
