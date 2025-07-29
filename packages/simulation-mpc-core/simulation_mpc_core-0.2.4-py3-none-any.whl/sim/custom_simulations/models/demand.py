import numpy as np
import pandas as pd
import pyomo.environ as pyomo

from .base import ComponentModel


class PowerDemandModel(ComponentModel):
    """
    Implements inflexible electricity consumption from a set of systems

    """

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=lambda m, i: data[(self.namespace("power"))].iloc[i],
            doc="Inflexible electricity demand power (W)",
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        return df

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)

        if "power" not in config:
            config["power"] = {"plot": []}

        config["power"]["plot"].append(
            {
                "key": self.namespace("power"),
                "kwargs": {"color": color, "drawstyle": "steps-post"},
            }
        )
        return config


class ProbabilityPowerDemandModel(ComponentModel):
    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "min_confidence_interval",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("min_confidence_interval"),
                0 * np.ones(len(self.model.i)),
            )[i],
            doc="Minimum confidence interval, (W)",
        )
        self.add_parameter(
            "max_confidence_interval",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("max_confidence_interval"),
                0 * np.ones(len(self.model.i)),
            )[i],
            doc="Maximum confidence interval, (W)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="The power, (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_minimum_confidence_interval",
            self.model.i,
            rule=lambda m, i: self.power[i] >= self.min_confidence_interval[i],
        )
        self.add_constraint(
            "constraint_maximum_confidence_interval",
            self.model.i,
            rule=lambda m, i: self.power[i] <= self.max_confidence_interval[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        return df


class HeatDemandModel(ComponentModel):
    """
    Implements inflexible heat consumption from a set of systems

    """

    def extend_model_variables(self, data, par, ini):
        # super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "heat",
            self.model.i,
            initialize=lambda m, i: data[(self.namespace("heat"))][i],
            doc="Inflexible heat demand power (W)",
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        return df

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)

        if "heat" not in config:
            config["heat"] = {"plot": []}

        config["heat"]["plot"].append(
            {
                "key": self.namespace("heat"),
                "kwargs": {"color": color, "drawstyle": "steps-post"},
            }
        )
        return config


class HeatVariableModel(ComponentModel):
    """
    Heat variable in the model

    """

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "heat_exchanger_size",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_exchanger_size"),
                500e3 * np.ones(len(self.model.i)),
            )[i],
            doc="Heat exchanger size, (W)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (0, self.heat_exchanger_size[i]),
            doc="Variable Heat (W)",
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        return df


class ThermalNetwork(ComponentModel):
    """
    Thermal network between three buildings in Cordium sysyem

    """

    def extend_model_variables(self, data, par, ini):
        # super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "p1_supply_temperature_setpoint",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("p1_supply_temperature_setpoint"),
                70e3 * np.ones(len(self.model.i)),
            )[i],
            doc="Temperature supply setpoint - Phase 1, (C)",
        )
        self.add_parameter(
            "p2_supply_temperature_setpoint",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("p2_supply_temperature_setpoint"),
                70e3 * np.ones(len(self.model.i)),
            )[i],
            doc="Temperature supply setpoint - Phase 2, (C)",
        )
        self.add_parameter(
            "p3_supply_temperature_setpoint",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("p3_supply_temperature_setpoint"),
                70e3 * np.ones(len(self.model.i)),
            )[i],
            doc="Temperature supply setpoint - Phase 3, (C)",
        )
        self.add_parameter(
            "heat_exchanger_size",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_exchanger_size"),
                10e3 * np.ones(len(self.model.i)),
            )[i],
            doc="Heat exchanger size, (W)",
        )
        self.add_parameter(
            "heat_limit",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_limit"), 0 * np.ones(len(self.model.i))
            )[i],
            doc="Minimal heat limit, (W)",
        )
        self.add_parameter(
            "p3_thermal_net_inflow",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("p3_thermal_net_inflow"),
                np.ones(len(self.model.i)),
            )[i],
            doc="Possible inflow heat in phase 3, (-)",
        )
        self.add_parameter(
            "p3_thermal_net_outflow",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("p3_thermal_net_outflow"),
                np.ones(len(self.model.i)),
            )[i],
            doc="Possible outflow heat in phase 3, (-)",
        )
        self.add_variable(
            "heat_1",
            self.model.i,
            bounds=lambda m, i: (
                -self.heat_exchanger_size[i],
                self.heat_exchanger_size[i],
            ),
            domain=pyomo.Reals,
            doc="Heat exchanger between boiler room 1 and thermal network",
        )
        self.add_variable(
            "heat_2",
            self.model.i,
            bounds=lambda m, i: (
                -self.heat_exchanger_size[i],
                self.heat_exchanger_size[i],
            ),
            domain=pyomo.Reals,
            doc="Heat exchanger between the boiler room 2 and the the thermal network",
        )
        self.add_variable(
            "heat_3",
            self.model.i,
            bounds=lambda m, i: (
                -self.p3_thermal_net_inflow[i] * self.heat_exchanger_size[i],
                self.p3_thermal_net_outflow[i] * self.heat_exchanger_size[i],
            ),
            domain=pyomo.Reals,
            doc=(
                "Heat exchanger between the boiler room 3 and the thermal"
                " network with additional constraints"
            ),
        )

    """
    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            'constraint_heat_flow',
            self.model.i,
            rule=lambda m, i: self.heat_1[i] == 0,
            doc='Thermal net heat flow'
        )
    """

    def get_results(self):
        df = super().get_results()
        df[self.namespace("heat_1")] = [
            pyomo.value(self.heat_1[i]) for i in self.model.i
        ]
        df[self.namespace("heat_2")] = [
            pyomo.value(self.heat_2[i]) for i in self.model.i
        ]
        df[self.namespace("heat_3")] = [
            pyomo.value(self.heat_3[i]) for i in self.model.i
        ]
        df[self.namespace("p1_supply_temperature_setpoint")] = [
            pyomo.value(self.p1_supply_temperature_setpoint[i]) for i in self.model.i
        ]
        df[self.namespace("p2_supply_temperature_setpoint")] = [
            pyomo.value(self.p2_supply_temperature_setpoint[i]) for i in self.model.i
        ]
        df[self.namespace("p3_supply_temperature_setpoint")] = [
            pyomo.value(self.p3_supply_temperature_setpoint[i]) for i in self.model.i
        ]
        df[self.namespace("heat_limit")] = [
            pyomo.value(self.heat_limit[i]) for i in self.model.i
        ]

        return df

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)

        if "heat" not in config:
            config["heat"] = {"plot": []}

        config["heat"]["plot"].append(
            {
                "key": self.namespace("heat"),
                "kwargs": {"color": color, "drawstyle": "steps-post"},
            }
        )
        return config


component_models = {
    "PowerDemandModel": PowerDemandModel,
    "HeatDemandModel": HeatDemandModel,
}
