import numpy as np
import pandas as pd
import pyomo.environ as pyomo

from imby.simulations.custom_simulations.models.base import ComponentModel


class PVModel(ComponentModel):
    """
    Implements pv production of an installations

    """

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "power_max",
            self.model.i,
            initialize=lambda m, i: max(0, data[self.namespace("power_max")][i]),
            doc="Maximum pv power (-)",
        )
        self.add_parameter(
            "power_generation",
            self.model.i,
            initialize=lambda m, i: max(0, data[self.namespace("power_generation")][i]),
            doc="Generated pv power (-)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.power_max[i], 0),
            initialize=0,
            doc="The pv power (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_curtailment_production",
            self.model.i,
            rule=lambda m, i: self.power[i] >= -self.power_generation[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]
        df[self.namespace("power_generation")] = [
            pyomo.value(self.power_generation[i]) for i in self.model.i
        ]
        df[self.namespace("power_max")] = [
            pyomo.value(self.power_max[i]) for i in self.model.i
        ]

        return df

    def compute_cost(
            self,
            result: pd.DataFrame,
            data: pd.DataFrame,
            par: dict,
            cost_data: dict = None,
    ) -> dict:
        local_cost_data = {
            self.namespace("capacity_cost_per_year"): 1.4 / 20.0,  # EUR / Wp / year
        }
        if cost_data is not None:
            for key in local_cost_data:
                if key in cost_data:
                    local_cost_data[key] = cost_data[key]

        years = (result.index[-1] - result.index[0]).total_seconds() / (365 * 24 * 3600)

        cost = {}
        cost[self.namespace("capacity")] = float(
            self._capacity
            * local_cost_data[self.namespace("capacity_cost_per_year")]
            * years
        )
        return cost

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


class NoCurtailingPVModel(ComponentModel):
    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "power_max",
            self.model.i,
            initialize=lambda m, i: max(0, data[self.namespace("power_max")].iloc[i]),
            doc="Maximum pv power (-)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.power_max[i], 0),
            initialize=lambda m, i: -max(0, data[self.namespace("power_max")].iloc[i]),
            doc="The pv power (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_no_curtailing",
            self.model.i,
            rule=lambda m, i: self.power[i] == -self.power_max[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]
        return df


class PreProcessingCurtailPVModel(NoCurtailingPVModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "full_power_max",
            self.model.i,
            initialize=lambda m, i: max(0, data[self.namespace("full_power_max")].iloc[i]),
            doc="Maximum pv power before curtailment (W)",
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("full_power_max")] = [
            pyomo.value(self.full_power_max[i]) for i in self.model.i
        ]
        return df


class ProbabilityPVModel(ComponentModel):
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
            domain=pyomo.NonPositiveReals,
            initialize=0,
            doc="The pv power (W)",
        )
        self.add_variable(
            "power_minimisation",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="The pv power (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_minimum_confidence_interval",
            self.model.i,
            rule=lambda m, i: self.power[i] <= -self.min_confidence_interval[i],
        )
        self.add_constraint(
            "constraint_maximum_confidence_interval",
            self.model.i,
            rule=lambda m, i: self.power[i] >= -self.max_confidence_interval[i],
        )
        self.add_constraint(
            "constraint_minimisation",
            self.model.i,
            rule=lambda m, i: self.power_minimisation[i] == -self.power[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]
        df[self.namespace("min_confidence_interval")] = [
            pyomo.value(self.min_confidence_interval[i]) for i in self.model.i
        ]
        df[self.namespace("max_confidence_interval")] = [
            pyomo.value(self.max_confidence_interval[i]) for i in self.model.i
        ]
        df[self.namespace("power_minimisation")] = [
            pyomo.value(self.power_minimisation[i]) for i in self.model.i
        ]

        return df


class SolarGeneralModel(ComponentModel):
    """
    Input variable:
        - disturbance:
            I - irradiation per PV panels area, (W/m2)
            T_a - ambient temperature, (°C)
    Parameters:
           area - PV panel area (m2)
    """

    def extend_model_variables(self, data, par, ini):
        # parameters
        self.add_parameter(
            "area",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("area"), 10 * np.ones(len(data.index))
            )[i],
            doc="PV panel area, (m2)",
        )
        self.add_parameter(
            "temperature_ambient",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_ambient"), 20 * np.ones(len(data.index))
            )[i],
            doc="Ambient temperature, (°C)",
        )
        self.add_parameter(
            "irradiance",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("irradiance"), np.zeros(len(data.index))
            )[i],
            doc="Irradiance on PV panels, (W/m2)",
        )
        self.add_parameter(
            "total_irradiance",
            self.model.i,
            initialize=lambda m, i: self.area[i] * self.irradiance[i],
            doc="Total irradiance per system, (W)",
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("irradiance")] = [
            pyomo.value(self.irradiance[i]) for i in self.model.i
        ]
        df[self.namespace("total_irradiance")] = [
            pyomo.value(self.total_irradiance[i]) for i in self.model.i
        ]
        return df


class SolarThermalModel(SolarGeneralModel):
    """
    Solar-thermal model:
        - state and output variable: T - outlet temperature
    Input variable:
        - area and weather information from SolarGeneral Model
        - disturbance
            mass_flow - water mass flow throughout solar-thermal
            T_in - input temperature
    Parameters:
        volume - water volume in solar-thermal panels
        power - thermal power of the system (0.7 * area)
        heat_loss_U - heat transfer coefficient
        eta_optical - optical efficiency
    """

    rho = 1000
    c_p = 4180

    parameters = {
        "unglazed": {
            "optical_eta": 0.90,
            "heat_loss_U_(W/m2k)": 20,
            "thermal_capacity_(kJ/m2K)": 5.96,
        },
        "glazed": {
            "optical_eta": 0.826,
            "heat_loss_U_(W/m2k)": 4.4,
            "thermal_capacity_(kJ/m2K)": 5.96,
        },
        "evacuated_tubes": {
            "optical_eta": 0.73,
            "heat_loss_U_(W/m2k)": 1.21,
            "thermal_capacity_(kJ/m2K)": 8.40,
        },
        "PVT_nonisolated": {
            "optical_eta": 0.559,
            "heat_loss_U_(W/m2k)": 15.8,
            "thermal_capacity_(kJ/m2K)": 12.80,
        },
        "PVT_isolated": {
            "optical_eta": 0.472,
            "heat_loss_U_(W/m2k)": 9.1,
            "thermal_capacity_(kJ/m2K)": 12.80,
        },
    }

    def __init__(self, *args, type=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = type

    def extend_model_variables(self, data, par, ini):
        self._states += [self.namespace("temperature")]
        super().extend_model_variables(data, par, ini)
        # parameters
        self.add_parameter(
            "mass_flow",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("mass_flow"), 1 * np.ones(len(data.index))
            )[i],
            domain=pyomo.NonNegativeReals,
            doc="Mass flow through solar-thermal system, (kg/s)",
        )
        self.add_parameter(
            "temperature_max",
            self.model.i,
            initialize=lambda m, i: 100 * np.ones(len(data.index))[i],
            doc="Maximum temperature in solar-thermal system, (°C)",
        )
        self.add_parameter(
            "temperature_min",
            self.model.i,
            initialize=lambda m, i: 0 * np.ones(len(data.index))[i],
            doc="Minimum temperature in solar-thermal system, (°C)",
        )
        self.add_parameter(
            "temperature_input_parameter",
            self.model.i,
            # bounds=lambda m, i: (self.temperature_min[i], self.temperature_max[i]),
            initialize=lambda m, i: data.get(
                self.namespace("temperature_input_parameter"), np.zeros(len(data.index))
            )[i],
            doc="Input temperature parameter, (°C)",
        )
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: 1e6 * np.ones(len(data.index))[i],
            doc="Maximum heat in solar-thermal system, (W)",
        )
        self.add_parameter(
            "thermal_capacity",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("thermal_capacity"),
                self.parameters[self.type]["thermal_capacity_(kJ/m2K)"]
                * np.ones(len(data.index)),
            )[i],
            doc="Thermal capacity of solar panel, (kJ/m2K)",
        )
        self.add_parameter(
            "heat_loss_U",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_loss_U"),
                self.parameters[self.type]["heat_loss_U_(W/m2k)"]
                * np.ones(len(data.index)),
            )[i],
            doc="Heat transfer coefficient, (W/m2k)",
        )
        self.add_parameter(
            "optical_eta",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("optical_eta"),
                self.parameters[self.type]["optical_eta"] * np.ones(len(data.index)),
            )[i],
            doc="Optical efficiency, (-)",
        )
        self.add_parameter(
            "big_number",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: 1e9 * np.ones(len(data.index))[i],
            doc="Big number for negative and positive separation of heat_all, (-)",
        )
        # variables
        self.add_variable(
            "temperature_input",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (self.temperature_min[i], self.temperature_max[i]),
            initialize=lambda m, i: data.get(
                self.namespace("temperature_input"), 10 * np.ones(len(data.index))
            )[i],
            doc="Input temperature in solar-thermal, (°C)",
        )
        self.add_variable(
            "temperature",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (self.temperature_min[i], self.temperature_max[i]),
            initialize=0,
            doc="Solar-thermal output temperature, (°C)",
        )
        self.add_variable(
            "temperature_all",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (self.temperature_min[i], self.temperature_max[i]),
            initialize=0,
            doc="Solar-thermal output temperature in all conditions, (°C)",
        )
        self.add_variable(
            "temperature_average",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (self.temperature_min[i], self.temperature_max[i]),
            initialize=0,
            doc="Average temperature in solar-thermal, (°C)",
        )
        self.add_variable(
            "heat_all",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (-self.heat_max[i], self.heat_max[i]),
            initialize=0,
            doc="Heat in the solar-thermal system, (W)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_max[i], 0),
            initialize=0,
            doc="total heat delivered from solar-thermal system",
        )
        self.add_variable(
            "heat_positive",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.heat_max[i]),
            initialize=0,
            doc="the positive part of heal_all",
        )
        self.add_variable(
            "heat_negative",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.heat_max[i]),
            initialize=0,
            doc="the negative part of heat_all",
        )
        self.add_variable(
            "separation_variable",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc=(
                "boolean variable for separation between positive and negative heat_all"
            ),
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        self.add_constraint(
            "constraint_temperature_all",
            self.model.i,
            rule=lambda m, i: (
                self.area[i]
                * self.thermal_capacity[i]
                * 1e3
                * (self.temperature_all[i + 1] - self.temperature_all[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == self.irradiance[i] * self.area[i] * self.optical_eta[i]
                + self.area[i]
                * self.heat_loss_U[i]
                * (self.temperature_ambient[i] - self.temperature_average[i])
                + self.mass_flow[i]
                * self.c_p
                * (self.temperature_input[i] - self.temperature_all[i])
                if i + 1 < len(m.i)
                else self.area[i]
                     * self.thermal_capacity[i]
                     * 1e3
                     * (self.temperature_all[i] - self.temperature_all[i - 1])
                     / (m.timestamp[i] - m.timestamp[i - 1])
                     == self.irradiance[i] * self.area[i] * self.optical_eta[i]
                     + self.area[i]
                     * self.heat_loss_U[i]
                     * (self.temperature_ambient[i] - self.temperature_average[i])
                     + self.mass_flow[i]
                     * self.c_p
                     * (self.temperature_input[i] - self.temperature_all[i])
            ),
        )
        self.add_constraint(
            "constraint_temperature_average",
            self.model.i,
            rule=lambda m, i: self.temperature_average[i]
                              == (self.temperature_all[i] + self.temperature_input[i]) / 2,
        )
        self.add_constraint(
            "constraint_heat_all",
            self.model.i,
            rule=lambda m, i: self.heat_all[i]
                              == -self.mass_flow[i]
                              * self.c_p
                              * (self.temperature_all[i] - self.temperature_input[i]),
        )
        self.add_constraint(
            "constraint_temperature_input",
            self.model.i,
            rule=lambda m, i: (
                self.temperature_input[i] == self.temperature_input_parameter[i]
                if (self.temperature_input_parameter[i] != 0)
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_heat_negative",
            self.model.i,
            rule=lambda m, i: self.heat_negative[i]
                              <= (1 - self.separation_variable[i]) * self.big_number[i],
        )
        self.add_constraint(
            "constraint_heat_positive",
            self.model.i,
            rule=lambda m, i: self.heat_positive[i]
                              <= self.separation_variable[i] * self.big_number[i],
        )
        self.add_constraint(
            "constraint_heat_positive_negative",
            self.model.i,
            rule=lambda m, i: (self.heat_positive[i] - self.heat_negative[i])
                              == -self.heat_all[i],
        )
        self.add_constraint(
            "constraint_heat_definition",
            self.model.i,
            rule=lambda m, i: self.heat[i] == -self.heat_positive[i],
        )
        self.add_constraint(
            "constraint_outlet_temperature",
            self.model.i,
            rule=lambda m, i: self.heat[i]
                              == -self.mass_flow[i]
                              * self.c_p
                              * (self.temperature[i] - self.temperature_input[i]),
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("temperature_all")] = [
            pyomo.value(self.temperature_all[i]) for i in self.model.i
        ]
        df[self.namespace("temperature")] = [
            pyomo.value(self.temperature[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_input")] = [
            pyomo.value(self.temperature_input[i]) for i in self.model.i
        ]
        df[self.namespace("heat")] = [-pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("heat_all")] = [
            -pyomo.value(self.heat_all[i]) for i in self.model.i
        ]
        df[self.namespace("separation_variable")] = [
            pyomo.value(self.separation_variable[i]) for i in self.model.i
        ]

        return df


class PhysicalPVModel(SolarGeneralModel):
    """
    The physical model for photovoltaic systems
    Output variable:
        - outlet power, (W)
        - efficiency, (-)
    Input variables
        - area and weather information from SolarGeneralModel
    Technological parameters:
        conditions on STC: temperature_panel_STC (°C), eta_STC (-)
        conditions on NOTC: temperature_panel_NOCT (°C), irradiance_NOCT=800 W/m2
        gamma - power temperature correction (-/°C)
        inverter efficiency (-)
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        # parameters
        self.add_parameter(
            "eta_STC",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("eta_STC"), 0.162 * np.ones(len(data.index))
            )[i],
            doc="Efficiency of standard testing conditions (STC), (-)",
        )
        self.add_parameter(
            "temperature_panel_STC",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_panel_STC"), 25 * np.ones(len(data.index))
            )[i],
            doc="Temperature of panels on STC, (°C)",
        )
        self.add_parameter(
            "temperature_panel_NOCT",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_panel_NOCT"), 44 * np.ones(len(data.index))
            )[i],
            doc=(
                "Temperature of panels on normal operating testing conditions (NOCT),"
                " (°C)"
            ),
        )
        self.add_parameter(
            "irradiance_NOCT",
            self.model.i,
            initialize=lambda m, i: 800 * np.ones(len(data.index))[i],
            doc="Irradiance on NOCT, (W/m2)",
        )
        self.add_parameter(
            "gamma",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("gamma"), 0.004 * np.ones(len(data.index))
            )[i],
            doc="Power temperature coefficient, (-/°C)",
        )
        self.add_parameter(
            "efficiency_inverter",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("efficiency_inverter"), 0.93 * np.ones(len(data.index))
            )[i],
            doc="Inverter efficiency, (-)",
        )
        # variables
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            initialize=0,
            doc="Power generation in PV system, (-)",
        )
        self.add_variable(
            "eta",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Efficiency of the PV system, (-)",
        )
        self.add_variable(
            "temperature_panel",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="PV panel temperature, (°C)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i]
                              == -self.eta[i] * self.efficiency_inverter[i] * self.total_irradiance[i],
        )
        self.add_constraint(
            "constraint_eta",
            self.model.i,
            rule=lambda m, i: self.eta[i]
                              == self.eta_STC[i]
                              * (
                                      1
                                      - self.gamma[i]
                                      * (self.temperature_panel[i] - self.temperature_panel_STC[i])
                              ),
        )
        """
        self.add_constraint(
            'constraint_temperature_panel',
            self.model.i,
            rule=lambda m, i:
            self.temperature_panel[i] == self.temperature_panel_NOCT[i] +
            (self.temperature_panel_NOCT[i] - self.temperature_panel_STC[i]) *
            self.irradiance[i]/self.irradiance_NOCT[i] if self.temperature_ambient[i] > 20
            else self.temperature_panel[i] == self.temperature_panel_NOCT[i]
        )
        """
        self.add_constraint(
            "constraint_temperature_panel",
            self.model.i,
            rule=lambda m, i: self.temperature_panel[i]
                              == self.temperature_ambient[i]
                              + (self.temperature_panel_NOCT[i] - 20)
                              * self.irradiance[i]
                              / self.irradiance_NOCT[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]
        df[self.namespace("eta")] = [pyomo.value(self.eta[i]) for i in self.model.i]
        df[self.namespace("temperature_panel")] = [
            pyomo.value(self.temperature_panel[i]) for i in self.model.i
        ]
        return df


class PhysicalPVTModel(SolarThermalModel, PhysicalPVModel):
    """
    Hybrid solar panel systems
    the same like PVTModel, but temperature panels equation is corrected
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.model.del_component(self.model_namespace("constraint_temperature_panel"))
        self.add_constraint(
            "constraint_temperature_panel",
            self.model.i,
            rule=lambda m, i: self.temperature_panel[i] == 25.0,
        )


component_models = {
    "PVModel": PVModel,
    "NoCurtailingPVModel": NoCurtailingPVModel,
    "ProbabilityPVModel": ProbabilityPVModel,
    "SolarThermalModel": SolarThermalModel,
    "PhysicalPVModel": PhysicalPVModel,
    "PhysicalPVTModel": PhysicalPVTModel,
}
