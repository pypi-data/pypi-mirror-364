import numpy as np
import pandas as pd
import pyomo.environ as pyomo

from imby.simulations.custom_simulations.models.base import ComponentModel


class StratifiedStorageTankModel(ComponentModel):
    """
    Models a perfectly stratified hot water storage tank.
    """

    rho_cp = 1000 * 4180

    def extend_model_variables(self, data, par, ini):
        self._states += [self.namespace("temperature")]

        self.add_parameter(
            "temperature_min",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("temperature_min")][i],
            doc="Minimum storage tank temperature (°C)",
        )
        self.add_parameter(
            "temperature_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("temperature_max")][i],
            doc="Maximum storage tank temperature (°C)",
        )
        self.add_parameter(
            "heat_loss_UA",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_loss_UA"), np.zeros(len(data.index))
            )[i],
            doc="UA value for heat losses (W/K)",
        )
        self.add_parameter(
            "volume",
            initialize=lambda m: par.get(self.namespace("volume"), 0.200),
            doc="Equivalent water volume of the storage (m3)",
        )
        self.add_parameter(
            "heat_loss_temperature",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_loss_temperature"),
                np.zeros(len(data.index)),
            )[i],
            doc="Temperature to which heat is lost (°C)",
        )
        self.add_parameter(
            "temperature_ini",
            initialize=lambda m: ini.get(
                self.namespace("temperature"), self.temperature_min[0]
            ),
            doc="Initial average temperature (°C)",
        )

        self.add_variable(
            "temperature",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                self.temperature_min[i],
                self.temperature_max[i],
            ),
            initialize=lambda m, i: (
                ((self.temperature_min[i] + self.temperature_max[i]) / 2)
                if i > 0
                else self.temperature_ini
            ),
            doc="Storage tank average temperature (°C)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Heat flow to the storage tank (W)",
        )
        self.add_variable(
            "heat_loss",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Heat loss to the storage tank (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_temperature",
            self.model.i,
            rule=lambda m, i: (
                self.rho_cp
                * self.volume
                * (self.temperature[i + 1] - self.temperature[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == +self.heat[i] + self.heat_loss[i]
                if i + 1 < len(m.i)
                else self.rho_cp
                * self.volume
                * (self.temperature[i] - self.temperature[i - 1])
                / (m.timestamp[i] - m.timestamp[i - 1])
                == +self.heat[i - 1] + self.heat_loss[i - 1]
            ),
        )
        self.add_constraint(
            "constraint_temperature_ini",
            rule=lambda m: self.temperature[0] == self.temperature_ini,
        )
        self.add_constraint(
            "constraint_heat_loss",
            self.model.i,
            rule=lambda m, i: self.heat_loss[i]
            == self.heat_loss_UA[i]
            * (self.heat_loss_temperature[i] - self.temperature[i]),
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("heat_loss")] = [
            pyomo.value(self.heat_loss[i]) for i in self.model.i
        ]
        df[self.namespace("temperature")] = [
            pyomo.value(self.temperature[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_min")] = [
            pyomo.value(self.temperature_min[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_max")] = [
            pyomo.value(self.temperature_max[i]) for i in self.model.i
        ]
        return df

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)
        if "temperature" not in config:
            config["temperature"] = {"plot": []}
        config["temperature"]["plot"].append(
            {"key": self.namespace("temperature"), "kwargs": {"color": color}}
        )
        config["temperature"]["plot"].append(
            {
                "key": self.namespace("temperature_min"),
                "kwargs": {
                    "color": color,
                    "label": "",
                    "marker": "^",
                    "linestyle": None,
                },
            }
        )
        config["temperature"]["plot"].append(
            {
                "key": self.namespace("temperature_max"),
                "kwargs": {
                    "color": color,
                    "label": "",
                    "marker": "v",
                    "linestyle": None,
                },
            }
        )
        if "heat" not in config:
            config["heat"] = {"plot": []}
        config["heat"]["plot"].append(
            {
                "key": self.namespace("heat"),
                "kwargs": {"color": color, "drawstyle": "steps-post"},
            }
        )
        return config


class DHWStorageTankModelSimple(StratifiedStorageTankModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self.add_parameter(
            "cold_water_temperature",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: 13,
            doc="Temperature of input cold water, (°C)",
        )
        self.model.del_component(self.model_namespace("heat"))
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Heat flow to the storage tank (W)",
        )
        self.add_parameter(
            "flow_dhw",
            self.model.i,
            initialize=lambda m, i: -data[self.namespace("flow_dhw")][i],
            doc="Volume flow consumption in the storage tank, (m3/s)",
        )
        self.add_parameter(
            "heat_out",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            initialize=lambda m, i: self.flow_dhw[i]
            * self.rho_cp
            * (self.temperature_max[i] - self.cold_water_temperature[i]),
            doc="Hot water heat consumption in the storage tank (W).",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.model.del_component(self.model_namespace("constraint_temperature"))
        self.add_constraint(
            "constraint_temperature",
            self.model.i,
            rule=lambda m, i: (
                self.rho_cp
                * self.volume
                * (self.temperature[i + 1] - self.temperature[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == +self.heat[i] + self.heat_loss[i] + self.heat_out[i]
                if i + 1 < len(m.i)
                else self.rho_cp
                * self.volume
                * (self.temperature[i] - self.temperature[i - 1])
                / (m.timestamp[i] - m.timestamp[i - 1])
                == +self.heat[i] + self.heat_loss[i] + self.heat_out[i]
            ),
        )

    def get_results(self):
        results = super().get_results()
        results[self.namespace("cold_water_temperature")] = [
            pyomo.value(self.cold_water_temperature[i]) for i in self.model.i
        ]
        results[self.namespace("heat_out")] = [
            -pyomo.value(self.heat_out[i]) for i in self.model.i
        ]
        results[self.namespace("flow_dhw")] = [
            -pyomo.value(self.flow_dhw[i]) for i in self.model.i
        ]
        results[self.namespace("temperature")] = [
            pyomo.value(self.temperature[i]) for i in self.model.i
        ]

        return results

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)

        if "heat" not in config:
            config["heat"] = {"plot": []}
        config["heat"]["plot"].append(
            {
                "key": self.namespace("heat_dhw"),
                "kwargs": {
                    "color": color,
                    "drawstyle": "steps-post",
                    "linestyle": ":",
                },
            }
        )
        config["heat"]["plot"].append(
            {
                "key": self.namespace("heat_reheat"),
                "kwargs": {
                    "color": color,
                    "drawstyle": "steps-post",
                    "linestyle": "--",
                },
            }
        )
        return config


class DHWStorageTankModel(StratifiedStorageTankModel):
    """
    Models a hot water storage tank which is mixed during charging but is discharged perfectly stratified.
    The storage tank must be charged up to 90% to supply sufficient comfort.
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._temperature_threshold_fraction = 0.9

        self.add_parameter(
            "cold_water_temperature",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: 13,
            doc="Temperature of input cold water, (°C)",
        )
        self.model.del_component(self.model_namespace("heat"))
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Heat flow to the storage tank (W)",
        )
        self.add_parameter(
            "full_threshold_temperature",
            self.model.i,
            initialize=lambda m, i: self.temperature_min[i]
            + self._temperature_threshold_fraction
            * (self.temperature_max[i] - self.temperature_min[i]),
        )
        self.add_parameter(
            "flow_dhw",
            self.model.i,
            initialize=lambda m, i: -data[self.namespace("flow_dhw")][i],
            doc="Volume flow consumption in the storage tank, (m3/s)",
        )
        self.add_parameter(
            "heat_dhw",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            initialize=lambda m, i: self.flow_dhw[i]
            * self.rho_cp
            * (self.temperature_max[i] - self.cold_water_temperature[i]),
            doc="Hot water heat consumption in the storage tank (W).",
        )
        self.add_variable(
            "heat_reheat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Reheat heat (W).",
        )
        self.add_variable(
            "reheat",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
        )
        self.add_variable(
            "is_full",
            self.model.i,
            domain=pyomo.Binary,
            bounds=(0, 1),
            initialize=0,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_heat",
            self.model.i,
            rule=lambda m, i: self.heat[i] == self.heat_dhw[i] + self.heat_reheat[i],
        )

        self.add_constraint(
            "constraint_is_full_1",
            self.model.i,
            rule=lambda m, i: self.temperature[i]
            <= self.full_threshold_temperature[i] + 100 * self.is_full[i],
            doc="turns is_full to 1 if state is above alpha %",
        )
        self.add_constraint(
            "constraint_is_full_2",
            self.model.i,
            rule=lambda m, i: self.temperature[i]
            >= self.full_threshold_temperature[i] - 100 * (1 - self.is_full[i]),
            doc="turns is_full to 0 if state is below alpha %",
        )

        self.add_constraint(
            "constraint_reheat",
            self.model.i,
            rule=lambda m, i: (
                self.reheat[i] >= self.reheat[i - 1] - self.is_full[i]
                if i > 0
                else pyomo.Constraint.Skip
            ),
            doc="keeps reheat 1 until is_full",
        )
        self.add_constraint(
            "constraint_heat_reheat_1",
            self.model.i,
            rule=lambda m, i: self.heat_reheat[i] <= 10e6 * self.reheat[i],
        )
        self.add_constraint(
            "constraint_heat_reheat_2",
            self.model.i,
            rule=lambda m, i: self.heat_reheat[i] >= 100 * self.reheat[i],
        )

    def get_results(self):
        results = super().get_results()
        results[self.namespace("cold_water_temperature")] = [
            pyomo.value(self.cold_water_temperature[i]) for i in self.model.i
        ]
        results[self.namespace("heat_dhw")] = [
            -pyomo.value(self.heat_dhw[i]) for i in self.model.i
        ]
        results[self.namespace("flow_dhw")] = [
            -pyomo.value(self.flow_dhw[i]) for i in self.model.i
        ]
        results[self.namespace("heat_reheat")] = [
            pyomo.value(self.heat_reheat[i]) for i in self.model.i
        ]
        results[self.namespace("temperature")] = [
            pyomo.value(self.temperature[i]) for i in self.model.i
        ]
        results[self.namespace("reheat")] = [
            pyomo.value(self.reheat[i]) for i in self.model.i
        ]

        return results

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)

        if "heat" not in config:
            config["heat"] = {"plot": []}
        config["heat"]["plot"].append(
            {
                "key": self.namespace("heat_dhw"),
                "kwargs": {
                    "color": color,
                    "drawstyle": "steps-post",
                    "linestyle": ":",
                },
            }
        )
        config["heat"]["plot"].append(
            {
                "key": self.namespace("heat_reheat"),
                "kwargs": {
                    "color": color,
                    "drawstyle": "steps-post",
                    "linestyle": "--",
                },
            }
        )
        return config


class BufferModel(StratifiedStorageTankModel):
    """

    Buffer model enables charging (self.heat) and discharching (self.heat_out) of the buffer/tank in the same time.

    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self.add_parameter(
            "heat_out_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.heat_out_max".format(self.name),
                5000e3 * np.ones(len(data.index)),
            )[i],
            doc="Maximum heat flow form the buffer, (W)",
        )
        self.model.del_component(self.model_namespace("heat"))
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Heat to the buffer, (W)",
        )
        self.add_variable(
            "heat_out",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_out_max[i], 0),
            initialize=0.0,
            doc="Outlet heat from buffer, (W)",
        )
        self.add_variable(
            "on",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc=(
                "Binary variable indicating when buffer operate (1) operate"
                " and (0) not operate, (-)"
            ),
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        self.add_constraint(
            "constraint_heat_out",
            self.model.i,
            rule=lambda m, i: -self.heat_out[i] <= self.heat_out_max[i] * self.on[i],
        )
        self.model.del_component(self.model_namespace("constraint_temperature"))
        self.add_constraint(
            "constraint_temperature",
            self.model.i,
            rule=lambda m, i: (
                self.rho_cp
                * self.volume
                * (self.temperature[i + 1] - self.temperature[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == +self.heat[i] + self.heat_loss[i] + self.heat_out[i]
                if i + 1 < len(m.i)
                else self.rho_cp
                * self.volume
                * (self.temperature[i] - self.temperature[i - 1])
                / (m.timestamp[i] - m.timestamp[i - 1])
                == +self.heat[i] + self.heat_loss[i] + self.heat_out[i]
            ),
        )

    def get_results(self):
        df = super().get_results()

        df[self.namespace("heat_out")] = [
            -pyomo.value(self.heat_out[i]) for i in self.model.i
        ]
        df[self.namespace("temperature")] = [
            pyomo.value(self.temperature[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_max")] = [
            pyomo.value(self.temperature_max[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_min")] = [
            pyomo.value(self.temperature_min[i]) for i in self.model.i
        ]

        return df


class FiniteHeatSourceModel(StratifiedStorageTankModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self.add_parameter(
            "average_heat_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("average_heat_min"),
                -1e9 * np.ones(len(data.index)),
            )[i],
            doc="Minimum average heat flow over the entire horizon (W)",
        )
        self.add_parameter(
            "average_heat_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("average_heat_max"),
                1e9 * np.ones(len(data.index)),
            )[i],
            doc="Minimum average heat flow over the entire horizon (W)",
        )
        self.average_horizon = data.get(self.namespace("average_horizon"), 24 * 3600)

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        i_start = 0
        for i in self.model.i:
            if (
                self.model.timestamp[i]
                >= self.model.timestamp[i_start] + self.average_horizon
            ):
                i_end = i
                self.add_constraint(
                    "constraint_average_heat_min_{}".format(i_start),
                    rule=lambda m: sum(self.heat[i] for i in range(i_start, i_end))
                    >= sum(self.average_heat_min[i] for i in range(i_start, i_end)),
                    doc=(
                        "The average heat flow over every 1 day period must be"
                        " large enough"
                    ),
                )
                self.add_constraint(
                    "constraint_average_heat_max_{}".format(i_start),
                    rule=lambda m: sum(self.heat[i] for i in range(i_start, i_end))
                    <= sum(self.average_heat_max[i] for i in range(i_start, i_end)),
                    doc=(
                        "The average heat flow over every 1 day period must be"
                        " small enough"
                    ),
                )
                i_start = i


class Ice_Storage(ComponentModel):
    """
    Ice Storage in Port of Barcelona project
    """

    def extend_model_variables(self, data, par, ini):
        self._states += [self.namespace("ice_stored")]

        self.add_parameter(
            "storage_size",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("storage_size")][i],
            doc="Maximum ice in storage, (t)",
        )
        self.add_parameter(
            "storage_threshold",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("storage_threshold")][i],
            doc="Ice threshold in storage, (t)",
        )
        self.add_parameter(
            "storage_thermal_losses",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("storage_thermal_losses"), np.zeros(len(data.index))
            )[i],
            doc="Thermal losses in storage, (W)",
        )
        self.add_parameter(
            "ice_consumed",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("ice_consumed")][i],
            doc="Ice consumption, (t/h)",
        )
        self.add_parameter(
            "ice_stored_ini",
            initialize=lambda m: ini.get(
                self.namespace("ice_stored"), self.storage_threshold[0]
            ),
            doc="Initial ice in storage, (t)",
        )
        self.add_parameter(
            "specific_generation",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("specific_generation")][i],
            doc="Specific generation, (Wh/t)",
        )
        self.add_variable(
            "ice_stored",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (self.storage_threshold[i], self.storage_size[i]),
            initialize=0,
            doc="Ice stored in storage, (t)",
        )
        self.add_variable(
            "ice_generated",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            doc="Ice generation, (t/h)",
        )
        self.add_variable(
            "refrigeration_capacity",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            doc="Refrigeration capacity for ice generation, (Wh)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_ice_stored",
            self.model.i,
            rule=lambda m, i: (
                (self.ice_stored[i + 1] - self.ice_stored[i])
                == (self.ice_generated[i] - self.ice_consumed[i])
                if i + 1 < len(m.i)
                else (self.ice_stored[i] == self.ice_stored_ini)
            ),
        )
        self.add_constraint(
            "constraint_temperature_ini",
            rule=lambda m: self.ice_stored[0] == self.ice_stored_ini,
        )
        self.add_constraint(
            "constraint_specific_generation",
            self.model.i,
            rule=lambda m, i: self.refrigeration_capacity[i]
            == self.ice_generated[i] * self.specific_generation[i]
            + self.storage_thermal_losses[i],
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("ice_stored")] = [
            pyomo.value(self.ice_stored[i]) for i in self.model.i
        ]
        df[self.namespace("ice_generated")] = [
            pyomo.value(self.ice_generated[i]) for i in self.model.i
        ]
        df[self.namespace("ice_consumed")] = [
            pyomo.value(self.ice_consumed[i]) for i in self.model.i
        ]
        df[self.namespace("refrigeration_capacity")] = [
            pyomo.value(self.refrigeration_capacity[i]) for i in self.model.i
        ]

        return df


class MultiLevelsStratifiedStorageTankModel(ComponentModel):
    """
    Stratified model with more water layers.
    Input is number of water layers in storage, default is 5, n_l=5
    default geometry: r = 1 m, A_cross = r2*PI = 0.785 m2
                      h = 5 m, h_l = h/n_l = 1 m
                      V_l = A_cross * h_l = 0.785 m3
                      A_shell = 2*r*PI*h_l=6.28 m2
    """

    def __init__(self, *args, water_levels=5, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_water_levels = range(water_levels)
        self.water_levels = water_levels
        self.rho_cp = 1000 * 4180
        self.cp = 4180

    def extend_model_variables(self, data, par, ini):
        for j in self.set_water_levels:
            self._states += [self.namespace("temperature_{}".format(j))]

        self.add_parameter(
            "temperature_limit",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.temperature_limit", 500 * np.ones(len(data.index))
            )[i],
            doc="Temperature limit in the multi-levels stratified storage, (°C)",
        )
        self.add_parameter(
            "temperature_input_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.temperature_input_min",
                -self.temperature_limit[i] * np.ones(len(data.index)),
            )[i],
            doc="Minimum input water temperature , (°C)",
        )
        self.add_parameter(
            "temperature_input_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.temperature_input_max",
                self.temperature_limit[i] * np.ones(len(data.index)),
            )[i],
            doc="Maximum input water temperature , (°C)",
        )
        self.add_parameter(
            "temperature_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.temperature_min",
                -self.temperature_limit[i] * np.ones(len(data.index)),
            )[i],
            doc="Minimum water temperature in storage, (°C)",
        )
        self.add_parameter(
            "temperature_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.temperature_max",
                self.temperature_limit[i] * np.ones(len(data.index)),
            )[i],
            doc="Maximum water temperature in storage, (°C)",
        )
        self.add_parameter(
            "volume_l",
            self.set_water_levels,
            initialize=lambda m, j: par.get(
                self.namespace("volume_{}".format(j)), 10 * 0.785
            ),
            doc="Volume in j-th level, (m3)",
        )
        self.add_parameter(
            "shell_area_l",
            self.set_water_levels,
            initialize=lambda m, j: par.get(
                self.namespace("shell_area_{}".format(j)), 10 * 6.28
            ),
            doc="Shell area around j-th level, (m2)",
        )
        self.add_parameter(
            "cross_section_area",
            self.set_water_levels,
            initialize=lambda m, j: par.get(
                self.namespace("cross_section_area_{}".format(j)), 10 * 0.785
            ),
            doc="Area between layers (j)-th and (j-1)-th area, (m2)",
        )
        self.add_parameter(
            "heat_loss_temperature",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_loss_temperature"), np.zeros(len(data.index))
            )[i],
            doc="Surrounded temperature around storage, (°C)",
        )
        self.add_parameter(
            "heat_transfer_coefficient_envelope",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_transfer_coefficient_envelope"),
                np.zeros(len(data.index)),
            )[i],
            doc="heat transfer coefficient from surrounding air to storage, (W/m2K)",
        )
        self.add_parameter(
            "heat_transfer_coefficient_water",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_transfer_coefficient_water"),
                20 * np.ones(len(data.index)),
            )[i],
            doc="heat transfer coefficient between layers, (W/m2K)",
        )
        self.add_parameter(
            "mass_flow",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("mass_flow"), 0.01 * np.ones(len(data.index))
            )[i],
            doc="Water flow in/out storage, (kg/s)",
        )
        self.add_parameter(
            "temperature_ini",
            self.set_water_levels,
            initialize=lambda m, j: ini.get(
                self.namespace("temperature_{}".format(j)),
                (self.temperature_max[0] + self.temperature_min[0]) / 2,
            ),
            doc="Initial temperature per levels, (°C)",
        )
        self.add_variable(
            "temperature_output",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (self.temperature_min[i], self.temperature_max[i]),
            initialize=0,
            doc="output water temperature , (°C)",
        )
        self.add_variable(
            "temperature_input",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (
                self.temperature_input_min[i],
                self.temperature_input_max[i],
            ),
            initialize=0,
            doc="input water temperature , (°C)",
        )
        for j in self.set_water_levels:
            self.add_variable(
                "temperature_{}".format(j),
                self.model.i,
                domain=pyomo.Reals,
                bounds=lambda m, i: (self.temperature_min[i], self.temperature_max[i]),
                initialize=0,
                doc="State temperature in every level, (°C)",
            )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Heat flow to the storage tank (W)",
        )
        self.add_variable(
            "heat_loss",
            self.model.i,
            self.set_water_levels,
            domain=pyomo.Reals,
            initialize=0,
            doc="Heat loss to the storage tank (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        self.add_constraint(
            "constraint_temperature_output",
            self.model.i,
            rule=lambda m, i: self.temperature_output[i] == self.temperature_0[i],
        )
        self.add_constraint(
            "constraint_heat",
            self.model.i,
            rule=lambda m, i: self.heat[i]
            == self.cp
            * self.mass_flow[i]
            * (self.temperature_input[i] - self.temperature_output[i]),
        )
        self.add_constraint(
            "constraint_temperature_lowest_level",
            self.model.i,
            rule=lambda m, i: (
                self.rho_cp
                * self.volume_l[self.set_water_levels[0]]
                * (
                    getattr(self, f"temperature_{self.set_water_levels[0]}")[i + 1]
                    - getattr(self, f"temperature_{self.set_water_levels[0]}")[i]
                )
                / (m.timestamp[i + 1] - m.timestamp[i])
                == self.cp
                * self.mass_flow[i]
                * (
                    getattr(self, f"temperature_{self.set_water_levels[1]}")[i]
                    - getattr(self, f"temperature_{self.set_water_levels[0]}")[i]
                )
                + self.cross_section_area[self.set_water_levels[0]]
                * self.heat_transfer_coefficient_water[i]
                * (
                    getattr(self, f"temperature_{self.set_water_levels[1]}")[i]
                    - getattr(self, f"temperature_{self.set_water_levels[0]}")[i]
                )
                + self.cross_section_area[self.set_water_levels[0]]
                * self.heat_transfer_coefficient_envelope[i]
                * (
                    self.heat_loss_temperature[i]
                    - getattr(self, f"temperature_{self.set_water_levels[0]}")[i]
                )
                + self.heat_loss[i, 0]
                if (i + 1 < len(m.i))
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_temperature_highest_layer",
            self.model.i,
            rule=lambda m, i: (
                self.rho_cp
                * self.volume_l[self.set_water_levels[-1]]
                * (
                    getattr(self, f"temperature_{self.set_water_levels[-1]}")[i + 1]
                    - getattr(self, f"temperature_{self.set_water_levels[-1]}")[i]
                )
                / (m.timestamp[i + 1] - m.timestamp[i])
                == self.cp
                * self.mass_flow[i]
                * (
                    self.temperature_input[i]
                    - getattr(self, f"temperature_{self.set_water_levels[-1]}")[i]
                )
                + self.cross_section_area[self.set_water_levels[-1]]
                * self.heat_transfer_coefficient_water[i]
                * (
                    getattr(self, f"temperature_{self.set_water_levels[-2]}")[i]
                    - getattr(self, f"temperature_{self.set_water_levels[-1]}")[i]
                )
                + self.cross_section_area[self.set_water_levels[-1]]
                * self.heat_transfer_coefficient_envelope[i]
                * (
                    self.heat_loss_temperature[i]
                    - getattr(self, f"temperature_{self.set_water_levels[-1]}")[i]
                )
                + self.heat_loss[i, self.set_water_levels[-1]]
                if (i + 1 < len(m.i))
                else pyomo.Constraint.Skip
            ),
        )
        for lvl in self.set_water_levels[
            1:-1
        ]:  # without last 2 because we have lowest and highest levels separately
            self.add_constraint(
                f"constraint_temperature_middle_levels_{lvl}",
                self.model.i,
                rule=lambda m, i: (
                    self.rho_cp
                    * self.volume_l[lvl]
                    * (
                        getattr(self, f"temperature_{lvl}")[i + 1]
                        - getattr(self, f"temperature_{lvl}")[i]
                    )
                    / (m.timestamp[i + 1] - m.timestamp[i])
                    == self.cp
                    * self.mass_flow[i]
                    * (
                        getattr(self, f"temperature_{lvl+1}")[i]
                        - getattr(self, f"temperature_{lvl-1}")[i]
                    )
                    + self.cross_section_area[lvl + 1]
                    * self.heat_transfer_coefficient_water[i]
                    * (
                        getattr(self, f"temperature_{lvl+1}")[i]
                        - getattr(self, f"temperature_{lvl}")[i]
                    )
                    + self.cross_section_area[lvl]
                    * self.heat_transfer_coefficient_water[i]
                    * (
                        getattr(self, f"temperature_{lvl-1}")[i]
                        - getattr(self, f"temperature_{lvl}")[i]
                    )
                    + self.heat_loss[i, lvl]
                    if (i + 1 < len(m.i))
                    else pyomo.Constraint.Skip
                ),
            )

        for lvl in self.set_water_levels:
            self.add_constraint(
                f"constraint_heat_loss_{lvl}",
                self.model.i,
                rule=lambda m, i: self.heat_loss[i, lvl]
                == self.heat_transfer_coefficient_envelope[i]
                * self.shell_area_l[lvl]
                * (
                    self.heat_loss_temperature[i]
                    - getattr(self, f"temperature_{lvl}")[i]
                ),
            )
            self.add_constraint(
                f"constraint_temperature_ini_{lvl}",
                rule=lambda m: getattr(self, f"temperature_{lvl}")[0]
                == self.temperature_ini[lvl],
            )

    def get_results(self):
        df = pd.DataFrame()
        for lvl in self.set_water_levels:
            df[self.namespace(f"temperature_{lvl}")] = [
                pyomo.value(getattr(self, f"temperature_{lvl}")[i])
                for i in self.model.i
            ]
        df[self.namespace("heat")] = [-pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("temperature_input")] = [
            pyomo.value(self.temperature_input[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_output")] = [
            pyomo.value(self.temperature_output[i]) for i in self.model.i
        ]
        return df


component_models = {
    "StratifiedStorageTankModel": StratifiedStorageTankModel,
    "DHWStorageTankModelSimple": DHWStorageTankModelSimple,
    "DHWStorageTankModel": DHWStorageTankModel,
    "BufferModel": BufferModel,
    "FiniteHeatSourceModel": FiniteHeatSourceModel,
    "MultiLevelsStratifiedStorageTankModel": MultiLevelsStratifiedStorageTankModel,
}
