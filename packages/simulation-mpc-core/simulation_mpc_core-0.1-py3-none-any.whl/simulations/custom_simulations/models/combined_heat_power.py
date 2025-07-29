import numpy as np
import pandas as pd
import pyomo.environ as pyomo

from src.imby.simulations.custom_simulations.models.heat_base import (
    ComponentModel,
    OnOffComponentModelBase,
)


class CombinedGasPowerModel(OnOffComponentModelBase):
    """
    Model for a combined heat and power generation - CHP
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "thermal_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.thermal_efficiency".format(self.name),
                0.45 * np.ones(len(data.index)),
            )[i],
            doc="Thermal efficiency of the CHP, (-)",
        )
        self.add_parameter(
            "electrical_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.electrical_efficiency".format(self.name),
                0.40 * np.ones(len(data.index)),
            )[i],
            doc="Electrical efficiency of the CHP, (-)",
        )
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: data["{}.heat_max".format(self.name)][i],
            doc="Maximum heat of the CHP, (W)",
        )
        self.add_parameter(
            "heat_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.heat_min".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Minimum heat of the CHP, (W)",
        )
        self.add_parameter(
            "power_max",
            self.model.i,
            initialize=lambda m, i: data["{}.power_max".format(self.name)][i],
            doc="Maximum power of the CHP, (W)",
        )
        self.add_parameter(
            "power_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.power_min".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Minimum power of the CHP, (W)",
        )
        self.add_parameter(
            "start_up_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.start_up_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Operational cost of the CHP, (EUR)",
        )
        self.add_parameter(
            "running_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.running_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Operational cost of the CHP, (EUR)",
        )
        self.add_parameter(
            "calorific_value",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.calorific_value".format(self.name),
                12.03 * np.ones(len(data.index)),
            )[i],
            doc="Calorific value of gas, (kWh/m3)",
        )

        # Variable
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_max[i], 0),
            initialize=0.0,
            doc="Output heat from the CHP, (W)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.power_max[i], 0),
            initialize=0.0,
            doc="Power generation in the CHP, (W)",
        )
        self.add_variable(
            "gas_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="The input gas flow to the CHP, (m3/h)",
        )
        self.model.del_component(self.model_namespace("on"))
        self.add_variable(
            "on",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc=(
                "Binary variable indicating the CHP operation, operate (1) or"
                " not operate (0), (-)"
            ),
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs, (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_thermal_efficiency",
            self.model.i,
            rule=lambda m, i: self.thermal_efficiency[i]
            * self.gas_flow[i]
            * self.calorific_value[i]
            * 1000
            == -self.heat[i],
        )
        self.add_constraint(
            "constraint_electrical_efficiency",
            self.model.i,
            rule=lambda m, i: self.electrical_efficiency[i]
            * self.gas_flow[i]
            * self.calorific_value[i]
            * 1000
            == -self.power[i],
        )
        self.add_constraint(
            "constraint_heat_max",
            self.model.i,
            rule=lambda m, i: -self.heat[i] <= self.heat_max[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_heat_min",
            self.model.i,
            rule=lambda m, i: -self.heat[i] >= self.heat_min[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_power_max",
            self.model.i,
            rule=lambda m, i: -self.power[i] <= self.power_max[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_power_min",
            self.model.i,
            rule=lambda m, i: -self.power[i] >= self.power_min[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            >= (
                self.start_up_cost[i] * (self.on[i] - self.on[i - 1])
                if i > 1
                else self.start_up_cost[i] * (self.on[i] - self.on_ini)
            )
            + (
                self.on[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                * self.running_cost[i]
                / 3600
                if i + 1 < len(m.i)
                else 0
            ),
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("heat")] = [-pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("heat_min")] = [
            pyomo.value(self.heat_min[i]) for i in self.model.i
        ]
        df[self.namespace("heat_max")] = [
            pyomo.value(self.heat_max[i]) for i in self.model.i
        ]
        df[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]
        df[self.namespace("power_min")] = [
            pyomo.value(self.power_min[i]) for i in self.model.i
        ]
        df[self.namespace("power_max")] = [
            pyomo.value(self.power_max[i]) for i in self.model.i
        ]
        df[self.namespace("gas_flow")] = [
            -pyomo.value(self.gas_flow[i]) for i in self.model.i
        ]
        df[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]

        return df


class CombinedGasPowerModel_Ext_Devo(CombinedGasPowerModel):
    """
    Model for a combined heat and power generation - CHP
    CHP in Devo project is used for: heating HT-Buffer and
                                     low-temperature beckup heat

    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_variable(
            "heat_HT",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_max[i], 0),
            initialize=0.0,
            doc="Output heat from the CHP, (W)",
        )
        self.add_variable(
            "heat_LT",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-0.3 * self.heat_max[i], 0),
            initialize=0.0,
            doc="Output heat from the CHP, (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_heat_total",
            self.model.i,
            rule=lambda m, i: self.heat[i] == self.heat_HT[i] + self.heat_LT[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("heat_LT")] = [
            -pyomo.value(self.heat_LT[i]) for i in self.model.i
        ]
        df[self.namespace("heat_HT")] = [
            -pyomo.value(self.heat_HT[i]) for i in self.model.i
        ]
        return df


class CombinedGasPowerModel_Devo_total(ComponentModel):
    """
    Model for a combined heat and power generation - CHP
    CHP in Devo project is used for: heating HT-Buffer and
                                     low-temperature beckup heat

    """

    def __init__(self, *args, minimum_on_time=2, minimum_off_time=1, **kwargs):
        super().__init__(*args, **kwargs)

        self.minimum_on_time = minimum_on_time
        self.minimum_off_time = minimum_off_time

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "minimum_on_time",
            initialize=lambda m: data.get("{}.minimum_on_time".format(self.name), 2),
            doc="Minimum on time, (h)",
        )
        self.add_parameter(
            "minimum_off_time",
            initialize=lambda m: data.get("{}.minimum_off_time".format(self.name), 1),
            doc="Minimum off time, (h)",
        )
        self.add_parameter(
            "thermal_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.thermal_efficiency".format(self.name),
                0.45 * np.ones(len(data.index)),
            )[i],
            doc="Thernal efficiency of the CHP, (-)",
        )
        self.add_parameter(
            "electrical_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.electrical_efficiency".format(self.name),
                0.40 * np.ones(len(data.index)),
            )[i],
            doc="Electrical efficiency of the CHP, (-)",
        )
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: data["{}.heat_max".format(self.name)][i],
            doc="Maximum heat of the CHP, (W)",
        )
        self.add_parameter(
            "heat_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.heat_min".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Minimum heat of the CHP, (W)",
        )
        self.add_parameter(
            "power_max",
            self.model.i,
            initialize=lambda m, i: data["{}.power_max".format(self.name)][i],
            doc="Maximum power of the CHP, (W)",
        )
        self.add_parameter(
            "power_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.power_min".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Minimum power of the CHP, (W)",
        )
        self.add_parameter(
            "start_up_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.start_up_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Operational cost of the CHP, (EUR)",
        )
        self.add_parameter(
            "running_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.running_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Operational cost of the CHP, (EUR)",
        )
        self.add_parameter(
            "on_ini",
            initialize=ini.get("{}.on".format(self.name), 0),
            doc="Initialisation of the CHP, (-)",
        )
        self.add_parameter(
            "gas_calorific_value",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.gas_calorific_value".format(self.name),
                12.03 * np.ones(len(data.index)),
            )[i],
            doc="Calorific value of gas, (kWh/m3)",
        )

        # Variable
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_max[i], 0),
            initialize=0.0,
            doc="Output heat from the CHP, (W)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.power_max[i], 0),
            initialize=0.0,
            doc="Power generation in the CHP, (W)",
        )
        self.add_variable(
            "gas_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="The input gas flow to the CHP, (m3/h)",
        )
        self.add_variable(
            "on",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc=(
                "Binary variable indicating the CHP operation, operate (1) or"
                " not operate (0), (-)"
            ),
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs, (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_thermal_efficiency",
            self.model.i,
            rule=lambda m, i: self.thermal_efficiency[i]
            * self.gas_flow[i]
            * self.gas_calorific_value[i]
            * 1000
            == -self.heat[i],
        )
        self.add_constraint(
            "constraint_electrical_efficiency",
            self.model.i,
            rule=lambda m, i: self.electrical_efficiency[i]
            * self.gas_flow[i]
            * self.gas_calorific_value[i]
            * 1000
            == -self.power[i],
        )
        self.add_constraint(
            "constraint_heat_max",
            self.model.i,
            rule=lambda m, i: -self.heat[i] <= self.heat_max[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_heat_min",
            self.model.i,
            rule=lambda m, i: -self.heat[i] >= self.heat_min[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_power_max",
            self.model.i,
            rule=lambda m, i: -self.power[i] <= self.power_max[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_power_min",
            self.model.i,
            rule=lambda m, i: -self.power[i] >= self.power_min[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            >= (
                self.start_up_cost[i] * (self.on[i] - self.on[i - 1])
                if i > 1
                else self.start_up_cost[i] * (self.on[i] - self.on_ini)
            )
            + (
                self.on[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                * self.running_cost[i]
                / 3600
                if i + 1 < len(m.i)
                else 0
            ),
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("heat")] = [-pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("heat_min")] = [
            pyomo.value(self.heat_min[i]) for i in self.model.i
        ]
        df[self.namespace("heat_max")] = [
            pyomo.value(self.heat_max[i]) for i in self.model.i
        ]
        df[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]
        df[self.namespace("power_min")] = [
            pyomo.value(self.power_min[i]) for i in self.model.i
        ]
        df[self.namespace("power_max")] = [
            pyomo.value(self.power_max[i]) for i in self.model.i
        ]
        df[self.namespace("gas_flow")] = [
            -pyomo.value(self.gas_flow[i]) for i in self.model.i
        ]
        df[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]

        return df


component_models = {
    "CombinedGasPowerModel": CombinedGasPowerModel,
    "CombinedGasPowerModel_Ext_Devo": CombinedGasPowerModel_Ext_Devo,
    "CombinedGasPowerModel_Devo_total": CombinedGasPowerModel_Devo_total,
}
