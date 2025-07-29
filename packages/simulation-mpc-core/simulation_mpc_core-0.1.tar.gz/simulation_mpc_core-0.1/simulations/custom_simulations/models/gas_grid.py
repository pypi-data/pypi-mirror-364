import numpy as np
import pandas as pd
import pyomo.environ as pyomo

from imby.simulations.custom_simulations.models.base import ComponentModel


class GasGridModel(ComponentModel):
    """
    Model for gas grid. No gas generation.
    """

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "price",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.price".format(self.name), 37e-03 * np.ones(len(data.index))
            )[i],
            doc="Gas price, (EUR/kWh)",
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

        self.add_variable(
            "flow",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-10e10, 0),
            initialize=0,
            doc="Gas consumption from the gas network/storage, (m3/h)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Gas cost on the gas grid, (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == (
                -self.price[i]
                * self.flow[i]
                / 3600
                * (m.timestamp[i + 1] - m.timestamp[i])
                * self.calorific_value[i]
                if i + 1 < len(m.i)
                else 0
            ),
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("price")] = [pyomo.value(self.price[i]) for i in self.model.i]
        df[self.namespace("flow")] = [pyomo.value(self.flow[i]) for i in self.model.i]
        df[self.namespace("calorific_value")] = [
            pyomo.value(self.calorific_value[i]) for i in self.model.i
        ]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]
        return df


class DistrictNetwork(ComponentModel):
    """
    Heating from District Network

    """

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: data[(self.namespace("heat_max"))][i],
            doc="Maximum heat from district network, (W)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_max[i], 0),
            doc="Heat consumption form distict network, (W)",
        )
        self.add_parameter(
            "price",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.price".format(self.name), 37e-03 * np.ones(len(data.index))
            )[i],
            doc="Heating price, (EUR/kWh)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Cost of heat form district network, (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: (
                self.operational_cost[i]
                == -self.price[i]
                * self.heat[i]
                / 3.6e6
                * (m.timestamp[i + 1] - m.timestamp[i])
                if i + 1 < len(m.i)
                else self.operational_cost[i]
                == -self.price[i]
                * self.heat[i]
                / 3.6e6
                * (m.timestamp[i] - m.timestamp[i - 1])
            ),
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("price")] = [pyomo.value(self.price[i]) for i in self.model.i]
        df[self.namespace("heat")] = [-pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]

        return df


component_models = {GasGridModel, DistrictNetwork}
