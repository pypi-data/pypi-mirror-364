import numpy as np
import pandas as pd
import pyomo.environ as pyomo

from .base import ComponentModel


class BaseChamberModel(ComponentModel):
    """
    Implement a base chamber model without the actual model. This chamber model will be implemented in a child class.

    """

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "heat_loss_temperature",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("heat_loss_temperature")][i],
            doc="Outdoor temperature near chamber, (°C)",
        )
        self.add_parameter(
            "import_products",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("import_products"), np.zeros(len(data.index))
            )[i],
            doc="Internal heat gain - import products in chamber (Q2), (W)",
        )
        self.add_parameter(
            "air_exchange_gain",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("air_exchange_gain"), np.zeros(len(data.index))
            )[i],
            doc="Internal heat gain - ventilation or infiltration (Q3), (W)",
        )
        self.add_parameter(
            "breathing_products",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("breathing_product"), np.zeros(len(data.index))
            )[i],
            doc="Internal gain - breathing of products (Q4), (W)",
        )
        self.add_parameter(
            "ice_evaporator",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("ice_evaporator"), np.zeros(len(data.index))
            )[i],
            doc="Internal gain - ice on evaporator melting (Q5), (W)",
        )
        self.add_parameter(
            "people_lights_fan_gain",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("people_lights_fan_gain"),
                np.zeros(len(data.index)),
            )[i],
            doc=(
                "Internal heat gain - people (Q6), lights (Q7) and evaporators"
                " fan (Q8), in chamber, (W)"
            ),
        )
        self.add_parameter(
            "total_internal_gain",
            self.model.i,
            initialize=lambda m, i: self.import_products[i]
            + self.air_exchange_gain[i]
            + self.breathing_products[i]
            + self.ice_evaporator[i]
            + self.people_lights_fan_gain[i],
            doc=(
                "Total internal heat gain - sum of (Q2) + (Q3) + (Q4) + (Q5) +"
                " (Q6) + (Q7) + (Q8), (W)"
            ),
        )
        self.add_parameter(
            "solar_shading",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("solar_shading"), np.zeros(len(data.index))
            )[i],
            doc="Solar shading coefficient of chamber, (-)",
        )
        self.add_parameter(
            "solar_gain_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("solar_gain_max"), np.zeros(len(data.index))
            )[i],
            doc="Maximum solar heat gain (W)",
        )

        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Heat flow in chamber, (W)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Operational cost in chamber, (EURO)",
        )

    def extend_model_constraints(self, data, par, ini):
        pass

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        return df

    def __str__(self):
        return self.name + "(" + ",".join(self.heat_variables) + ")"


class ChamberModel(ComponentModel):
    """
    Implements the thermal behavior of a single zone building with a 1st order model
    """

    rho_cp = 1000 * 4180

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "evaporating_temperature",
            self.model.i,
            initialize=lambda m: par.get(self.namespace("evaporating_temperature"), 0),
            doc="Evaporating temperature in chember - Te, (C)",
        )

        self.add_parameter(
            "evaporating_capacity",
            self.model.i,
            initialize=lambda m: par.get(self.namespace("evaporating_capacity"), 0),
            doc="Evaporating capacity in chember - Qe, (kW)",
        )

        self.add_parameter(
            "volume",
            initialize=lambda m: par.get(self.namespace("volume"), 0.200),
            doc="Equivalent water volume of the storage (m3)",
        )
        self.add_parameter(
            "effective_volume",
            initialize=lambda m: par.get(self.namespace("effective_volume"), 1),
            doc="Effective volume of chamber, (m3)",
        )

        self.add_parameter(
            "heat_loss_temperature",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("heat_loss_temperature")][i],
            doc="Outdoor temperature near chamber, (°C)",
        )
        self.add_parameter(
            "import_products",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("import_products"), np.zeros(len(data.index))
            )[i],
            doc="Internal heat gain - import products in chamber (Q2), (W)",
        )
        self.add_parameter(
            "air_exchange_gain",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("air_exchange_gain"), np.zeros(len(data.index))
            )[i],
            doc="Internal heat gain - ventilation or infiltration (Q3), (W)",
        )
        self.add_parameter(
            "breathing_products",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("breathing_product"), np.zeros(len(data.index))
            )[i],
            doc="Internal gain - breathing of products (Q4), (W)",
        )
        self.add_parameter(
            "ice_evaporator",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("ice_evaporator"), np.zeros(len(data.index))
            )[i],
            doc="Internal gain - ice on evaporator melting (Q5), (W)",
        )
        self.add_parameter(
            "people_lights_fan_gain",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("people_lights_fan_gain"),
                np.zeros(len(data.index)),
            )[i],
            doc=(
                "Internal heat gain - people (Q6), lights (Q7) and evaporators"
                " fan (Q8), in chamber, (W)"
            ),
        )
        self.add_parameter(
            "total_internal_gain",
            self.model.i,
            initialize=lambda m, i: self.import_products[i]
            + self.air_exchange_gain[i]
            + self.breathing_products[i]
            + self.ice_evaporator[i]
            + self.people_lights_fan_gain[i],
            doc=(
                "Total internal heat gain - sum of (Q2) + (Q3) + (Q4) + (Q5) +"
                " (Q6) + (Q7) + (Q8), (W)"
            ),
        )
        self.add_parameter(
            "solar_shading",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("solar_shading"), np.zeros(len(data.index))
            )[i],
            doc="Solar shading coefficient of chamber, (-)",
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
            "temperature_ini",
            initialize=lambda m: ini.get(
                self.namespace("temperature"), self.temperature_min[0]
            ),
            doc="Initial average temperature (°C)",
        )

        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Operational cost in chamber, (EURO)",
        )
        self.add_variable(
            "temperature",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                self.temperature_min[i],
                self.temperature_max[i],
            ),
            initialize=0,
            doc="Storage tank average temperature (°C)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (-756000, 0),
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
                * self.effective_volume
                * self.volume
                * (self.temperature[i + 1] - self.temperature[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == self.heat[i] + self.heat_loss[i]
                if i + 1 < len(m.i)
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_temperature_ini",
            rule=lambda m: self.temperature[0] == self.temperature_ini,
        )
        self.add_constraint("constraint_heat_ini", rule=lambda m: self.heat[0] <= 0)
        self.add_constraint(
            "constraint_heat_loss",
            self.model.i,
            rule=lambda m, i: self.heat_loss[i]
            == self.heat_loss_UA[i]
            * (self.heat_loss_temperature[i] - self.temperature[i]),
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("heat_loss")] = [
            pyomo.value(self.heat_loss[i]) for i in self.model.i
        ]
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("temperature")] = [
            pyomo.value(self.temperature[i]) for i in self.model.i
        ]
        df[self.namespace("evaporating_temperature")] = [
            pyomo.value(self.evaporating_temperature[i]) for i in self.model.i
        ]

        return df


component_models = {}
