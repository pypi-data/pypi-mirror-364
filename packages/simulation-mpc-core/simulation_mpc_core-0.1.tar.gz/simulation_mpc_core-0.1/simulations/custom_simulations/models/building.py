import numpy as np
import pandas as pd
import pyomo.environ as pyomo

from imby.simulations.custom_simulations.models.base import ComponentModel


class BaseBuildingModel(ComponentModel):
    """
    Implements a base building model without the actual building model.
    This should be implemented in a child class.
    """

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "outdoor_temperature",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("outdoor_temperature")][i],
            doc="Outdoor temperature near the building (°C)",
        )
        self.add_variable(
            "temperature_supply",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_supply"), np.zeros(len(data.index))
            )[i],
            doc="Air supply temperature that goes to building/zone (°C)",
        )
        self.add_parameter(
            "heat_cool_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_cool_max"),
                500e3 * np.ones(len(data.index)),
            )[i],
            doc="Heat exhanger capacity for heaitng (W)",
        )
        self.add_parameter(
            "internal_gain",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("internal_gain"), np.zeros(len(data.index))
            )[i],
            doc="Internal heat gain (W)",
        )
        self.add_parameter(
            "solar_gain_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("solar_gain_max"), np.zeros(len(data.index))
            )[i],
            doc="Maximum solar heat gain (W)",
        )
        self.add_parameter(
            "solar_shading_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("solar_shading_min"), np.ones(len(data.index))
            )[i],
            doc="Minimum solar shading coefficient, shading closed (-)",
        )
        self.add_parameter(
            "solar_shading_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("solar_shading_max"), np.ones(len(data.index))
            )[i],
            doc="Maximum solar shading coefficient, shading open (-)",
        )

        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.heat_cool_max[i]),
            initialize=0,
            doc="Heating in building (W)",
        )
        self.add_variable(
            "cool",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_cool_max[i], 0),
            initialize=0,
            doc="Cooling in building (W)",
        )
        """self.add_variable(
            'solar_shading',
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (self.solar_shading_min[i], self.solar_shading_max[i]),
            initialize=0,
            doc='Building solar shading 1: shading open, 0: shading closed (-)'
        )"""
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Building operational cost",
        )

    def extend_model_constraints(self, data, par, ini):
        pass

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        # df[self.namespace('solar_shading')] = [pyomo.value(self.solar_shading[i]) for i in self.model.i]
        return df

    def __str__(self):
        return self.name + "(" + ",".join(self.heat_variables) + ")"


class BuildingModel(BaseBuildingModel):
    """
    Implements the thermal behavior of a single zone building with a 1st order model
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self._states += [self.namespace("temperature")]

        self.add_parameter(
            "heat_loss_UA",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("heat_loss_UA")][i],
            doc="UA value for heat transfer to the ambient (W/K)",
        )
        self.add_parameter(
            "heat_loss_UA_ground",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("heat_loss_UA_ground")][i],
            doc="UA value for heat transfer to the ground (W/K)",
        )
        self.add_parameter(
            "C",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("C")][i],
            doc="Overall heat capacity of the building (W/K)",
        )
        self.add_parameter(
            "ground_temperature",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("ground_temperature"), 12 * np.ones(len(data.index))
            )[i],
            doc="Ground temperature under the building (°C)",
        )
        self.add_parameter(
            "temperature_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_min"),
                21 * np.ones(len(data.index)),
            )[i],
            doc="Minimum building temperature at the measurement point (°C)",
        )
        self.add_parameter(
            "temperature_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_max"),
                22 * np.ones(len(data.index)),
            )[i],
            doc="Maximum building temperature at the measurement point (°C)",
        )
        self.add_parameter(
            "temperature_error",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_error"), np.zeros(len(data.index))
            )[i],
            domain=pyomo.Reals,
            doc="Predicted error value",
        )
        self.add_parameter(
            "temperature_ini",
            initialize=lambda m: ini.get(
                self.namespace("temperature"), self.temperature_max[0]
            ),
            doc="Initial building temperature at the measurement point (°C)",
        )
        self.add_variable(
            "temperature",
            self.model.i,
            domain=pyomo.Reals,
            # bounds=lambda m, i: (self.temperature_min[i]-1, self.temperature_max[i]+1),
            initialize=lambda m, i: self.temperature_min[i],
            doc="Building temperature at the measurement point (°C)",
        )
        self.add_variable(
            "temperature_correction",
            self.model.i,
            domain=pyomo.Reals,
            # bounds=lambda m, i: (self.temperature_min[i]-1, self.temperature_max[i]+1),
            initialize=lambda m, i: self.temperature_min[i],
            doc="Building temperature at the measurement point (°C)",
        )
        self.add_parameter(
            "temperature_violation_scale",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_violation_scale"),
                1e6 * np.ones(len(data.index)),
            )[i],
            doc="Scale factor for the temperature constraint violation (EUR / kWh)",
        )
        self.add_variable(
            "temperature_min_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "temperature_max_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_parameter(
            "ventilation_rate",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("ventilation_rate"), np.zeros(len(data.index))
            )[i],
            doc="Frash ventilation rate (m3/s)",
        )
        self.add_parameter(
            "recuperator_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("recuperator_efficiency"),
                np.ones(len(data.index)),
            )[i],
            doc="Recuperator efficiency of ventilation system -)",
        )
        self.add_variable(
            "constraint_violation",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_temperature",
            self.model.i,
            rule=lambda m, i: (
                self.C[i]
                * (self.temperature[i + 1] - self.temperature[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == -self.heat_loss_UA[i]  # 5 times higher
                * (self.temperature[i] - self.outdoor_temperature[i])
                - self.heat_loss_UA_ground[i]
                * (self.temperature[i] - self.ground_temperature[i])
                + self.heat[i]
                + self.cool[i]
                + self.internal_gain[i]
                + self.solar_shading_min[i] * self.solar_gain_max[i]
                - (1 - self.recuperator_efficiency[i])
                * self.ventilation_rate[i]
                * 1.2
                * (self.temperature[i] - self.temperature_supply[i])
                * 1e3
                if i + 1 < len(m.i)
                else (
                    self.C[i]
                    * (self.temperature[i] - self.temperature[i - 1])
                    / (m.timestamp[i] - m.timestamp[i - 1])
                    == -self.heat_loss_UA[i - 1]
                    * (self.temperature[i - 1] - self.outdoor_temperature[i - 1])
                    - self.heat_loss_UA_ground[i]
                    * (self.temperature[i] - self.ground_temperature[i])
                    + self.heat[i - 1]
                    + self.cool[i - 1]
                    + self.internal_gain[i - 1]
                    + self.solar_shading_min[i - 1] * self.solar_gain_max[i - 1]
                    - (1 - self.recuperator_efficiency[i - 1])
                    * self.ventilation_rate[i - 1]
                    * 1.2
                    * (self.temperature[i - 1] - self.temperature_supply[i - 1])
                    * 1e3
                )
            ),
        )
        self.add_constraint(
            "constraint_temperature_ini",
            rule=lambda m: self.temperature[0] == self.temperature_ini,
        )
        self.add_constraint(
            "constraint_temperature_correction",
            self.model.i,
            rule=lambda m, i: self.temperature_correction[i]
            == self.temperature[i] + self.temperature_error[i],
        )
        self.add_constraint(
            "constraint_temperature_min_slack",
            self.model.i,
            rule=lambda m, i: self.temperature_min_slack[i]
            >= self.temperature_min[i] - self.temperature_correction[i],
        )
        self.add_constraint(
            "constraint_temperature_max_slack",
            self.model.i,
            rule=lambda m, i: self.temperature_max_slack[i]
            >= self.temperature_correction[i] - self.temperature_max[i],
        )
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == (self.temperature_min_slack[i] + self.temperature_max_slack[i])
            / 3.6e6
            * self.temperature_violation_scale[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("temperature")] = [
            pyomo.value(self.temperature[i]) for i in self.model.i
        ]
        df[self.namespace("outdoor_temperature")] = [
            pyomo.value(self.outdoor_temperature[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_correction")] = [
            pyomo.value(self.temperature_correction[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_error")] = [
            pyomo.value(self.temperature_error[i]) for i in self.model.i
        ]
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("cool")] = [pyomo.value(self.cool[i]) for i in self.model.i]
        df[self.namespace("temperature_min")] = [
            pyomo.value(self.temperature_min[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_max")] = [
            pyomo.value(self.temperature_max[i]) for i in self.model.i
        ]
        df[self.namespace("ventilation_rate")] = [
            pyomo.value(self.ventilation_rate[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_supply")] = [
            pyomo.value(self.temperature_supply[i]) for i in self.model.i
        ]

        return df


class TwoStateBuildingModel(ComponentModel):
    """
    Implements the thermal behavior of a two-states building model
    State varaibles: walls and
    indoor temperature
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [self.namespace("temperature")]
        self._states += [self.namespace("temperature_wall")]

        self.add_parameter(
            "temperature_outdoor",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("temperature_outdoor")][i],
            doc="Outdoor temperature near the building (°C)",
        )
        self.add_parameter(
            "resistance_outdoor",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("resistance_outdoor")][i],
            doc="Outdoor resistance - between outdoor and wall temperature, (W/K)",
        )
        self.add_parameter(
            "resistance_indoor",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("resistance_indoor")][i],
            doc="Indoor resistance - between wall and indoor temperature, (W/K)",
        )
        self.add_parameter(
            "C",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("C")][i],
            doc="Heat capacity of the indoor air (W/K)",
        )
        self.add_parameter(
            "C_wall",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("C_wall")][i],
            doc="Heat capacity of the building wall (W/K)",
        )
        self.add_parameter(
            "temperature_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_min"), 21 * np.ones(len(data.index))
            )[i],
            doc="Minimum building temperature at the measurement point (°C)",
        )
        self.add_parameter(
            "temperature_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_max"), 22 * np.ones(len(data.index))
            )[i],
            doc="Maximum building temperature at the measurement point (°C)",
        )
        self.add_parameter(
            "temperature_ini",
            initialize=lambda m: ini.get(
                self.namespace("temperature"), self.temperature_max[0]
            ),
            doc="Initial building temperature at the measurement point (°C)",
        )
        self.add_parameter(
            "temperature_ini_wall",
            initialize=lambda m: ini.get(
                self.namespace("temperature_wall"), self.temperature_max[0]
            ),
            doc="Initial building temperature in the wall (°C)",
        )
        self.add_parameter(
            "heat_cool_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_cool_max"), 500e3 * np.ones(len(data.index))
            )[i],
            doc="Heat exhanger capacity for heaitng (W)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.heat_cool_max[i]),
            initialize=0,
            doc="Heating in building (W)",
        )
        self.add_variable(
            "cool",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_cool_max[i], 0),
            initialize=0,
            doc="Cooling in building (W)",
        )
        self.add_variable(
            "temperature",
            self.model.i,
            domain=pyomo.Reals,
            initialize=lambda m, i: self.temperature_min[i],
            doc="Building temperature at the measurement point (°C)",
        )
        self.add_variable(
            "temperature_wall",
            self.model.i,
            domain=pyomo.Reals,
            initialize=lambda m, i: self.temperature_min[i],
            doc="Temperature of the wall (°C)",
        )
        self.add_parameter(
            "temperature_violation_scale",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_violation_scale"),
                1e6 * np.ones(len(data.index)),
            )[i],
            doc="Scale factor for the temperature constraint violation (EUR / kWh)",
        )
        self.add_variable(
            "temperature_min_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "temperature_max_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "constraint_violation",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        self.add_constraint(
            "constraint_temperature",
            self.model.i,
            rule=lambda m, i: (
                self.C[i]
                * (self.temperature[i + 1] - self.temperature[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == -self.resistance_indoor[i]
                * (self.temperature[i] - self.temperature_wall[i])
                + self.heat[i]
                + self.cool[i]
                if i + 1 < len(m.i)
                else (
                    self.C[i]
                    * (self.temperature[i] - self.temperature[i - 1])
                    / (m.timestamp[i] - m.timestamp[i - 1])
                    == -self.resistance_indoor[i - 1]
                    * (self.temperature[i - 1] - self.temperature_wall[i - 1])
                    + self.heat[i - 1]
                    + self.cool[i - 1]
                )
            ),
        )

        self.add_constraint(
            "constraint_temperature_wall",
            self.model.i,
            rule=lambda m, i: (
                self.C_wall[i]
                * (self.temperature_wall[i + 1] - self.temperature_wall[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == -self.resistance_outdoor[i]
                * (self.temperature_wall[i] - self.temperature_outdoor[i])
                - self.resistance_indoor[i]
                * (self.temperature_wall[i] - self.temperature[i])
                if i + 1 < len(m.i)
                else (
                    self.C_wall[i]
                    * (self.temperature_wall[i] - self.temperature_wall[i - 1])
                    / (m.timestamp[i] - m.timestamp[i - 1])
                    == -self.resistance_outdoor[i]
                    * (self.temperature_wall[i - 1] - self.temperature_outdoor[i - 1])
                    - self.resistance_indoor[i - 1]
                    * (self.temperature_wall[i - 1] - self.temperature[i - 1])
                )
            ),
        )
        self.add_constraint(
            "constraint_temperature_ini",
            rule=lambda m: self.temperature[0] == self.temperature_ini,
        )
        self.add_constraint(
            "constraint_temperature_ini_wall",
            rule=lambda m: self.temperature_wall[0] == self.temperature_ini_wall,
        )
        self.add_constraint(
            "constraint_temperature_min_slack",
            self.model.i,
            rule=lambda m, i: self.temperature_min_slack[i]
            >= self.temperature_min[i] - self.temperature[i],
        )
        self.add_constraint(
            "constraint_temperature_max_slack",
            self.model.i,
            rule=lambda m, i: self.temperature_max_slack[i]
            >= self.temperature[i] - self.temperature_max[i],
        )
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == (self.temperature_min_slack[i] + self.temperature_max_slack[i])
            / 3.6e6
            * self.temperature_violation_scale[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("temperature")] = [
            pyomo.value(self.temperature[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_wall")] = [
            pyomo.value(self.temperature_wall[i]) for i in self.model.i
        ]
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("cool")] = [pyomo.value(self.cool[i]) for i in self.model.i]
        df[self.namespace("temperature_min")] = [
            pyomo.value(self.temperature_min[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_max")] = [
            pyomo.value(self.temperature_max[i]) for i in self.model.i
        ]

        return df


class BuildingHeatingOnly(BuildingModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self.model.del_component(self.model_namespace("heat"))

        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Only heating in building (W)",
        )


class BuildingNoCooling(BuildingModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self.model.del_component(self.model_namespace("cool"))
        self.add_variable(
            "cool",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (0e3, 0),
            initialize=0,
            doc="No cooling in building (W)",
        )


class DataBuildingModel(ComponentModel):
    """
    Data-driven building model
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.building_coef = [9.95560222e-01,2.33069969e-03,1.95117589e-06]
        # self.building_coef = [  9.97890921e-01,   2.33069969e-03,   1.95117589e-06]
        self.building_coef = [9.97890921e-01, 2.33069969e-03, 4.87793972e-07]
        # self.building_coef =[  9.81684993e-01   5.49738273e-03   6.00623961e-07]

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self._states += [self.namespace("temperature")]
        self.add_parameter(
            "temperature_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_min"),
                21 * np.ones(len(data.index)),
            )[i],
            doc="Minimum building temperature at the measurement point (°C)",
        )
        self.add_parameter(
            "temperature_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_max"),
                22 * np.ones(len(data.index)),
            )[i],
            doc="Maximum building temperature at the measurement point (°C)",
        )
        self.add_parameter(
            "temperature_ini",
            initialize=lambda m: ini.get(
                self.namespace("temperature"), self.temperature_max[0]
            ),
            doc="Initial building temperature at the measurement point (°C)",
        )
        self.add_parameter(
            "outdoor_temperature",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("outdoor_temperature")][i],
            doc="Outdoor temperature near the building (°C)",
        )
        self.add_variable(
            "temperature",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                self.temperature_min[i],
                self.temperature_max[i],
            ),
            doc="Building temperature at the measurement point (°C)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Building heat flow (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        self.add_constraint(
            "constraint_temperature",
            self.model.i,
            rule=lambda m, i: (
                self.temperature[i + 1]
                == self.building_coef[0] * self.temperature[i]
                + self.building_coef[1]
                * (self.outdoor_temperature[i] - self.temperature[i])
                + self.building_coef[2] * self.heat[i]
                if i + 1 < len(m.i)
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_temperature_ini",
            rule=lambda m: self.temperature[0] == self.temperature_ini,
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("temperature")] = [
            pyomo.value(self.temperature[i]) for i in self.model.i
        ]
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("temperature_min")] = [
            pyomo.value(self.temperature_min[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_max")] = [
            pyomo.value(self.temperature_max[i]) for i in self.model.i
        ]

        return df


class SwecoDataBuildingModel(ComponentModel):
    """
    Linear regression building data model
    """

    def __init__(self, *args, coef=[], inter=[], heating_capacity=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.coef = coef
        self.inter = inter

        self.heating_capacity = heating_capacity * 1e3

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [self.namespace("temperature")]
        self.add_parameter(
            "temperature_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_min"),
                21 * np.ones(len(data.index)),
            )[i],
            doc="Minimum temperature in the building (°C)",
        )
        self.add_parameter(
            "temperature_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_max"),
                22 * np.ones(len(data.index)),
            )[i],
            doc="Maximum temperature in building (°C)",
        )
        self.add_parameter(
            "temperature_ini",
            initialize=lambda m: ini.get(
                self.namespace("temperature"), self.temperature_max[0]
            ),
            doc="Initial temperature in building(°C)",
        )
        self.add_parameter(
            "outdoor_temperature",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("outdoor_temperature")][i],
            doc="Outdoor temperature (°C)",
        )
        self.add_parameter(
            "wind_speed",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("wind_speed")][i],
            doc="Wind speed (m/s)",
        )
        self.add_parameter(
            "wind_bearing",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("wind_bearing")][i],
            doc="Wind bearing (-)",
        )
        self.add_parameter(
            "real_GHI",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("real_GHI")][i],
            doc="Real Global Horizontal Irradiation (W/m2)",
        )
        self.add_parameter(
            "temperature_supply_min",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("temperature_supply_min")][i],
            doc="Minimum temperature of supply air, (°C)",
        )
        self.add_parameter(
            "temperature_supply_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("temperature_supply_max")][i],
            doc="Maximum temperature of supply air (°C)",
        )
        self.add_parameter(
            "temperature_violation_scale",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_violation_scale"),
                1e3 * np.ones(len(data.index)),
            )[i],
            doc="Scale factor for the temperature constraint violation (EUR / kWh)",
        )
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: self.heating_capacity * np.ones(len(data.index))[i],
            doc="Heat exhanger capacity for heaitng (W)",
        )
        self.add_variable(
            "temperature",
            self.model.i,
            domain=pyomo.Reals,
            doc="Indoor temperature in zones (°C)",
        )
        self.add_variable(
            "temperature_supply",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                self.temperature_supply_min[i],
                self.temperature_supply_max[i],
            ),
            doc="Building temperature at the measurement point (°C)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.heat_max[i]),
            doc="Building heat flow (W)",
        )
        self.add_variable(
            "temperature_min_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "temperature_max_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "constraint_violation",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_temperature",
            self.model.i,
            rule=lambda m, i: (
                self.temperature[i + 1]
                == self.inter[0]
                + self.coef[0] * self.outdoor_temperature[i]
                + self.coef[1] * self.heat[i] * 1e-1
                + self.coef[2] * self.real_GHI[i]
                + self.coef[3] * self.temperature_supply[i]
                + self.coef[4] * self.wind_speed[i]
                + self.coef[5] * self.wind_bearing[i]
                + self.coef[6] * self.temperature[i]
                if i + 1 < len(m.i)
                else self.temperature[i]
                == self.inter[0]
                + self.coef[0] * self.outdoor_temperature[i - 1]
                + self.coef[1] * self.heat[i - 1] * 1e-1
                + self.coef[2] * self.real_GHI[i - 1]
                + self.coef[3] * self.temperature_supply[i - 1]
                + self.coef[4] * self.wind_speed[i - 1]
                + self.coef[5] * self.wind_bearing[i - 1]
                + self.coef[6] * self.temperature[i - 1]
            ),
        )
        self.add_constraint(
            "constraint_temperature_ini",
            rule=lambda m: self.temperature[0] == self.temperature_ini,
        )
        self.add_constraint(
            "constraint_temperature_min_slack",
            self.model.i,
            rule=lambda m, i: self.temperature_min_slack[i]
            >= self.temperature_min[i] - self.temperature[i],
        )
        self.add_constraint(
            "constraint_temperature_max_slack",
            self.model.i,
            rule=lambda m, i: self.temperature_max_slack[i]
            >= self.temperature[i] - self.temperature_max[i],
        )
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == (self.temperature_min_slack[i] + self.temperature_max_slack[i])
            * self.temperature_violation_scale[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("temperature")] = [
            pyomo.value(self.temperature[i]) for i in self.model.i
        ]
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("temperature_min")] = [
            pyomo.value(self.temperature_min[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_max")] = [
            pyomo.value(self.temperature_max[i]) for i in self.model.i
        ]
        df[self.namespace("constraint_violation")] = [
            pyomo.value(self.constraint_violation[i]) for i in self.model.i
        ]

        return df


class O14DataBuildingModel(ComponentModel):
    """
    Linear regression building for O-14 model
    regressors are: outdoor temperature
                     heat
                     UV_index
                     temperature_lag1h
    """

    def __init__(
        self,
        *args,
        coef=[],
        inter=[],
        mean=[],
        scale=[],
        heating_capacity=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.coef = coef
        self.inter = inter
        self.mean = mean
        self.scale = scale
        self.heating_capacity = heating_capacity * 1e3

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [self.namespace("temperature")]
        # parameters
        self.add_parameter(
            "temperature_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_min"), 21 * np.ones(len(data.index))
            )[i],
            doc="Minimum temperature in the building (°C)",
        )
        self.add_parameter(
            "temperature_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_max"), 22 * np.ones(len(data.index))
            )[i],
            doc="Maximum temperature in building (°C)",
        )
        self.add_parameter(
            "temperature_ini",
            initialize=lambda m: ini.get(
                self.namespace("temperature"), self.temperature_max[0]
            ),
            doc="Initial temperature in building(°C)",
        )
        self.add_parameter(
            "temperature_outdoor",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("temperature_outdoor")][i],
            doc="Outdoor temperature (°C)",
        )
        self.add_parameter(
            "UV_index",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("UV_index")][i],
            doc="UV index (-)",
        )
        self.add_parameter(
            "ventilation_rate",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("ventilation_rate")][i],
            doc="Ventilation rate in the building (m3/s)",
        )

        self.add_parameter(
            "temperature_violation_scale",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_violation_scale"),
                1e10 * np.ones(len(data.index)),
            )[i],
            doc="Scale factor for the temperature constraint violation (EUR / kWh)",
        )
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: self.heating_capacity * np.ones(len(data.index))[i],
            doc="Heat exchanger capacity for heating (W)",
        )
        # variables
        self.add_variable(
            "temperature",
            self.model.i,
            domain=pyomo.Reals,
            doc="Indoor temperature in zones (°C)",
        )
        self.add_variable(
            "temperature_lag_1h",
            self.model.i,
            domain=pyomo.Reals,
            doc="One hour temperature lag (-)",
        )

        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            bounds=lambda m, i: (-self.heat_max[i], self.heat_max[i]),
            doc="Building heat flow (W)",
        )
        self.add_variable(
            "temperature_min_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "temperature_max_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "constraint_violation",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )
        self.add_variable(
            "temperature_supply",
            self.model.i,
            domain=pyomo.Reals,
            initialize=lambda m, i: data[self.namespace("temperature_supply")][i],
            doc="Temperature supply (-)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        self.add_constraint(
            "constraint_temperature",
            self.model.i,
            rule=lambda m, i: (
                self.temperature[i + 1]
                == self.inter[0]
                + ((self.temperature_supply[i] - self.mean[0]) / self.scale[0])
                * self.coef[0]
                + ((self.temperature_outdoor[i] - self.mean[1]) / self.scale[1])
                * self.coef[1]
                + ((self.UV_index[i] - self.mean[2]) / self.scale[2]) * self.coef[2]
                + ((self.temperature_lag_1h[i] - self.mean[3]) / self.scale[3])
                * self.coef[3]
                if i + 1 < len(m.i)
                else (
                    self.temperature[i]
                    == self.inter[0]
                    + ((self.temperature_supply[i - 1] - self.mean[0]) / self.scale[0])
                    * self.coef[0]
                    + ((self.temperature_outdoor[i - 1] - self.mean[1]) / self.scale[1])
                    * self.coef[1]
                    + ((self.UV_index[i - 1] - self.mean[2]) / self.scale[2])
                    * self.coef[2]
                    + ((self.temperature_lag_1h[i - 1] - self.mean[3]) / self.scale[3])
                    * self.coef[3]
                )
            ),
        )
        self.add_constraint(
            "constraint_heat",
            self.model.i,
            rule=lambda m, i: self.heat[i]
            == self.ventilation_rate[i]
            * 1.2
            * (self.temperature[i] - self.temperature_supply[i]),
        ),

        self.add_constraint(
            "constraint_lag",
            self.model.i,
            rule=lambda m, i: (
                self.temperature_lag_1h[i + 1] == self.temperature[i]
                if i + 1 < len(m.i)
                else (self.temperature_lag_1h[i] == self.temperature[i - 1])
            ),
        ),

        self.add_constraint(
            "constraint_temperature_ini",
            rule=lambda m: self.temperature[0] == self.temperature_ini,
        )
        self.add_constraint(
            "constraint_temperature_min_slack",
            self.model.i,
            rule=lambda m, i: self.temperature_min_slack[i]
            >= self.temperature_min[i] - self.temperature[i],
        )
        self.add_constraint(
            "constraint_temperature_max_slack",
            self.model.i,
            rule=lambda m, i: self.temperature_max_slack[i]
            >= self.temperature[i] - self.temperature_max[i],
        )
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == (self.temperature_min_slack[i] + self.temperature_max_slack[i])
            * self.temperature_violation_scale[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("temperature")] = [
            pyomo.value(self.temperature[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_supply")] = [
            pyomo.value(self.temperature_supply[i]) for i in self.model.i
        ]
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("temperature_min")] = [
            pyomo.value(self.temperature_min[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_max")] = [
            pyomo.value(self.temperature_max[i]) for i in self.model.i
        ]
        df[self.namespace("constraint_violation")] = [
            pyomo.value(self.constraint_violation[i]) for i in self.model.i
        ]

        return df


class BuildingComfortModel(BuildingModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        # self.add_parameter(
        #     'temperature_distribution',
        #     range(len(par.get('temperature_array'))),
        #     initialize=lambda m, j: par.get('temperature_array', [])[j],
        #     doc="List of building temperatures relative to factor distribution ([C])",
        #     within=pyomo.Any
        # )
        # self.add_parameter(
        #     'factor_distribution',
        #     range(len(par.get('factor_array'))),
        #     initialize=lambda m, j: par.get('factor_array', [])[j],
        #     doc="List of factor relative to temperature distribution ([])",
        #     within=pyomo.Any
        # )
        self.add_variable(
            "factor",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            bounds=(0, 1),
            doc="Comfort factor depending on temperature in building/zone",
        )
        self.add_variable(
            "discomfort_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Saved cost for discomfort, (EUR)",
        )

    def temperatue_definition_by_factor(
        self,
        factor_distribution_array,
        temperature_distribution_array,
        temperature_current,
    ):
        if temperature_current < temperature_distribution_array[0]:
            return factor_distribution_array[0]
        elif (
            temperature_current
            > temperature_distribution_array[
                temperature_distribution_array.__len__() - 1
            ]
        ):
            return factor_distribution_array[
                temperature_distribution_array.__len__() - 1
            ]
        for i in range(1, len(temperature_distribution_array)):
            if (
                temperature_current >= temperature_distribution_array[i - 1]
                and temperature_current <= temperature_distribution_array[i]
            ):
                x1 = temperature_distribution_array[i - 1]
                x2 = temperature_distribution_array[i]
                y1 = factor_distribution_array[i - 1]
                y2 = factor_distribution_array[i]
                return ((y2 - y1) / (x2 - x1)) * (temperature_current - x1) + y1

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        # self.add_constraint(
        #     'constraint_factor',
        #     self.model.i,
        #     rule=lambda m, i: self.factor[i] == self.temperatue_definition_by_factor(self.factor_distribution,
        #                                                                              self.temperature_distribution,
        #                                                                              self.temperature[i])
        # )
        self.add_constraint(
            "constraint_factor",
            self.model.i,
            rule=lambda m, i: self.factor[i]
            == 0.1647524 * self.temperature[i] ** 1
            - 0.0058274 * self.temperature[i] ** 2
            + 0.0000623 * self.temperature[i] ** 3
            - 0.4685328,
        )

        self.add_constraint(
            "constraint_discomfort_cost",
            self.model.i,
            rule=lambda m, i: self.discomfort_cost[i] == (1 - self.factor[i]) * 100,
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("discomfort_cost")] = [
            pyomo.value(self.discomfort_cost[i]) for i in self.model.i
        ]
        df[self.namespace("comfort_factor")] = [
            pyomo.value(self.factor[i]) for i in self.model.i
        ]
        return df


class BuildingTuningModel(ComponentModel):
    """
    Tuning physical paramaters:
        UA - heat transfer coefficient and
        C - thermal inertia of the system
        by  available measurements
        indoor, outdoor temperature and gas consumption
    """

    def __init__(self, *args, state=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = state

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "tuning_parameter",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("tuning_parameter"), 1 * np.ones(len(data.index))
            )[i],
            doc="Tuning index, (-)",
        )
        self.add_parameter(
            "area",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("area"), 823 * np.ones(len(data.index))
            )[i],
            doc="Building area, (m2)",
        )
        self.add_parameter(
            "volume",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("volume"), 3292 * np.ones(len(data.index))
            )[i],
            doc="Building volume, (m3)",
        )
        self.add_parameter(
            "Occupancy",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("Occupancy"), np.ones(len(data.index))
            )[i],
            doc="Occupancy profile, (-)",
        )
        self.add_parameter(
            "specific_thermal_capacity_parameter",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("specific_thermal_capacity_parameter"),
                50 * np.ones(len(data.index)),
            )[i],
            doc="Specific thermal capacity parameter, (Wh/m2K)",
        )
        self.add_parameter(
            "UA_parameter",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("UA_parameter"), 3630 * np.ones(len(data.index))
            )[i],
            doc="Total heat transfer parameter, (W/K)",
        )
        self.add_parameter(
            "ACH_parameter",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("ACH_parameter"), 0 * np.ones(len(data.index))
            )[i],
            doc="Air exchange per hour, (1/h)",
        )
        self.add_parameter(
            "temperature_outdoor",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("temperature_outdoor")][i],
            doc="Measured temperature near the building, (°C)",
        )
        self.add_parameter(
            "temperature_indoor",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("temperature_indoor")][i],
            doc="Measured indoor temperature in the building, (°C)",
        )
        self.add_parameter(
            "heat_consumption",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("heat_consumption")][i],
            doc="Measured heat consumption in building, (W)",
        )
        self.add_parameter(
            "temperature_indoor_derivative",
            self.model.i,
            initialize=lambda m, i: data[
                self.namespace("temperature_indoor_derivative")
            ][i],
            doc="Measured indoor temperature derivative, (°C/s)",
        )
        self.add_parameter(
            "big_number",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: 1e20 * np.ones(len(data.index))[i],
            doc="Big number for negative and positive separation of result, (-)",
        )
        self.add_variable(
            "specific_thermal_capacity",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (
                self.specific_thermal_capacity_parameter[i] / self.tuning_parameter[i],
                self.specific_thermal_capacity_parameter[i] * self.tuning_parameter[i],
            ),
            initialize=300,
            doc="Specific thermal inertia in the building, (Wh/Km2)",
        )
        self.add_variable(
            "C",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Thermal inertia of the building, (J)",
        )
        self.add_variable(
            "UA",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (
                self.UA_parameter[i] / self.tuning_parameter[i],
                self.UA_parameter[i] * self.tuning_parameter[i],
            ),
            initialize=0,
            doc="Total heat transfer in the building, (W/K)",
        )
        self.add_variable(
            "ACH",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (
                self.ACH_parameter[i] / self.tuning_parameter[i],
                self.ACH_parameter[i] * self.tuning_parameter[i],
            ),
            initialize=0,
            doc="Air exchange of air in the school, (1/h)",
        )
        self.add_variable(
            "system_efficiency",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0.93, 0.93),
            initialize=1.0,
            doc="Efficiency of the system, (-)",
        )
        self.add_variable(
            "result_difference",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (-self.big_number[i], self.big_number[i]),
            initialize=0,
            doc="Result difference that should be minimised, (-)",
        )
        self.add_variable(
            "result_positive",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.big_number[i]),
            initialize=0,
            doc="the positive part of result_difference. (-)",
        )
        self.add_variable(
            "result_negative",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.big_number[i]),
            initialize=0,
            doc="the negative part of result_difference",
        )
        self.add_variable(
            "separation_variable",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="boolean variable for separation between positive and negative result",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_result_difference",
            self.model.i,
            rule=lambda m, i: (
                self.result_difference[i]
                == self.C[i] * self.temperature_indoor_derivative[i]
                - self.UA[i]
                * (self.temperature_outdoor[i - 1] - self.temperature_indoor[i])
                / 1e3
                - self.ACH[i]
                * self.Occupancy[i]
                * 1.2
                * (self.temperature_outdoor[i - 1] - self.temperature_indoor[i])
                - self.system_efficiency[i] * self.heat_consumption[i]
                if i >= 1
                else self.result_difference[i] == 0
            ),
        )
        self.add_constraint(
            "constraint_thermal_inertia",
            self.model.i,
            rule=lambda m, i: self.C[i]
            == self.area[i]
            * self.specific_thermal_capacity[i]
            / 1e3,  # m2 * Wh/Km2 --> C (Wh/K) ---> C dt/dt (kW)
        )

        self.add_constraint(
            "constraint_result_negative",
            self.model.i,
            rule=lambda m, i: self.result_negative[i]
            <= (1 - self.separation_variable[i]) * self.big_number[i],
        )
        self.add_constraint(
            "constraint_heat_positive",
            self.model.i,
            rule=lambda m, i: self.result_positive[i]
            <= self.separation_variable[i] * self.big_number[i],
        )
        self.add_constraint(
            "constraint_result_positive_negative",
            self.model.i,
            rule=lambda m, i: (self.result_positive[i] - self.result_negative[i])
            == self.result_difference[i],
        )
        self.add_constraint(
            "constraint_fixing_variable_UA",
            self.model.i,
            rule=lambda m, i: (
                self.UA[i + 1] == self.UA[i]
                if i + 1 < len(m.i)
                else self.UA[i] == self.UA[i - 1]
            ),
        )
        self.add_constraint(
            "constraint_fixing_variable_specific_thermal",
            self.model.i,
            rule=lambda m, i: (
                self.specific_thermal_capacity[i + 1]
                == self.specific_thermal_capacity[i]
                if i + 1 < len(m.i)
                else self.specific_thermal_capacity[i]
                == self.specific_thermal_capacity[i - 1]
            ),
        )
        self.add_constraint(
            "constraint_fixing_ACH",
            self.model.i,
            rule=lambda m, i: (
                self.ACH[i + 1] == self.ACH[i]
                if i + 1 < len(m.i)
                else self.ACH[i] == self.ACH[i - 1]
            ),
        )
        self.add_constraint(
            "constraint_fixing_variable_efficiency",
            self.model.i,
            rule=lambda m, i: (
                self.system_efficiency[i + 1] == self.system_efficiency[i]
                if i + 1 < len(m.i)
                else self.system_efficiency[i] == self.system_efficiency[i - 1]
            ),
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("specific_thermal_capacity")] = [
            pyomo.value(self.specific_thermal_capacity[i]) for i in self.model.i
        ]
        df[self.namespace("system_efficiency")] = [
            pyomo.value(self.system_efficiency[i]) for i in self.model.i
        ]
        df[self.namespace("C")] = [pyomo.value(self.C[i]) for i in self.model.i]
        df[self.namespace("UA")] = [pyomo.value(self.UA[i]) for i in self.model.i]
        df[self.namespace("ACH")] = [pyomo.value(self.ACH[i]) for i in self.model.i]
        df[self.namespace("Occupancy")] = [
            pyomo.value(self.Occupancy[i]) for i in self.model.i
        ]
        df[self.namespace("result_difference")] = [
            pyomo.value(self.result_difference[i]) for i in self.model.i
        ]
        df[self.namespace("result_positive")] = [
            pyomo.value(self.result_positive[i]) for i in self.model.i
        ]
        df[self.namespace("result_negative")] = [
            pyomo.value(self.result_negative[i]) for i in self.model.i
        ]
        return df


component_models = {}
