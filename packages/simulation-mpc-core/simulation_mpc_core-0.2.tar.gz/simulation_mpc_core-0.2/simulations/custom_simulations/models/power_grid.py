import numpy as np
import pandas as pd
import pyomo.environ as pyomo
from pandas import DataFrame

from .base import ComponentModel


class GridModel(ComponentModel):
    """
    Models a connection to an electricity grid with limited power and a separate price for production and consumption.

    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "consumption_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("consumption_price"),
                0.15 * np.ones(len(self.model.i)),
            )[i],
            doc="The price of grid electricity consumption (EUR/kWh)",
        )
        self.add_parameter(
            "production_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("production_price"),
                0.10 * np.ones(len(self.model.i)),
            )[i],
            doc="The price of grid electricity production (EUR/kWh)",
        )
        self.add_parameter(
            "capacity_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("capacity_price"),
                0 * np.ones(len(self.model.i)),
            )[i],
            doc="The capacity price of grid capacity (EUR/kWh)",
        )
        self.add_parameter(
            "fcr_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("fcr_price"), 0 * np.ones(len(self.model.i))
            )[i],
            doc="The FCR price (EUR/MWh/h)",
        )
        self.add_parameter(
            "generation_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("generation_price"),
                0 * np.ones(len(self.model.i)),
            )[i],
            doc="The generation price of local production (EUR/kWh)",
        )
        self.add_parameter(
            "consumption_power_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("consumption_power_max"),
                10e6 * np.ones(len(self.model.i)),
            )[i],
            doc="Maximum consumption power from the grid (W)",
        )
        self.add_parameter(
            "production_power_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("production_power_max"),
                10e6 * np.ones(len(self.model.i)),
            )[i],
            doc="Maximum production power to the grid (W)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                -self.consumption_power_max[i],
                self.production_power_max[i],
            ),
            initialize=0,
            doc="Total grid power, +: production, -: consumption (W)",
        )
        self.add_variable(
            "consumption_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.consumption_power_max[i]),
            initialize=0,
            doc="The consumption power from the grid (W)",
        )
        self.add_variable(
            "production_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.production_power_max[i]),
            initialize=0,
            doc="The production power to the grid (W)",
        )
        self.add_variable(
            "production",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            doc="Production (1) or consumption (0) mode (-)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="The operational costs (EUR)",
        )
        self.add_variable(
            "maximum_capacity",
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The maximum power in the domain (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_production_consumption_power",
            self.model.i,
            rule=lambda m, i: self.production_power[i] - self.consumption_power[i]
            == self.power[i],
        )
        self.add_constraint(
            "constraint_production",
            self.model.i,
            rule=lambda m, i: self.production_power[i]
            <= self.production[i] * self.production_power_max[i],
        )
        self.add_constraint(
            "constraint_consumption",
            self.model.i,
            rule=lambda m, i: self.consumption_power[i]
            <= (1 - self.production[i]) * self.consumption_power_max[i],
        )
        """
        self.add_constraint(
            'constraint_maximum_capacity_production',
            self.model.i,
            rule=lambda m, i: 
            (self.maximum_capacity >= self.production_power[i]) # if self.production[i] == 0 else maximum_capacity >= self.production_power[i])
        )
        """
        """
        self.add_constraint(
            'constraint_maximum_capacity_consumption',
            self.model.i,
            rule=lambda m, i: 
            self.maximum_capacity >= self.consumption_power[i]
        )
        """
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == +(
                self.consumption_power[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                * self.consumption_price[i]
                if i + 1 < len(m.i)
                else 0
            )
            - (
                self.production_power[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                * self.production_price[i]
                if i + 1 < len(m.i)
                else 0
            ),
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]
        df[self.namespace("consumption_price")] = [
            pyomo.value(self.consumption_price[i]) for i in self.model.i
        ]
        df[self.namespace("production_price")] = [
            pyomo.value(self.production_price[i]) for i in self.model.i
        ]
        df[self.namespace("capacity_price")] = [
            pyomo.value(self.capacity_price[i]) for i in self.model.i
        ]
        df[self.namespace("fcr_price")] = [
            pyomo.value(self.fcr_price[i]) for i in self.model.i
        ]
        df[self.namespace("generation_price")] = [
            pyomo.value(self.generation_price[i]) for i in self.model.i
        ]
        df[self.namespace("consumption_power")] = [
            pyomo.value(self.consumption_power[i]) for i in self.model.i
        ]
        df[self.namespace("production_power")] = [
            pyomo.value(self.production_power[i]) for i in self.model.i
        ]
        df[self.namespace("consumption_power_max")] = [
            pyomo.value(self.consumption_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("production_power_max")] = [
            pyomo.value(self.production_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]

        return df

    def compute_cost(
        self,
        result: DataFrame,
        data: DataFrame,
        parameters: dict,
        cost_data: dict = None,
    ):
        local_cost_data = {
            self.namespace("consumption_price"): data[
                self.namespace("production_price")
            ],  # EUR / kWh
            self.namespace("production_price"): data[
                self.namespace("consumption_price")
            ],  # EUR / kWh
        }
        if cost_data is not None:
            for key in local_cost_data:
                if key in cost_data:
                    local_cost_data[key] = cost_data[key]

        cost = {}
        cost[self.namespace("production")] = np.trapz(
            np.minimum(0, result[self.namespace("power")])
            * local_cost_data[self.namespace("production_price")]
            / 3.6e6,
            x=result.index,
        )
        cost[self.namespace("consumption")] = np.trapz(
            np.maximum(0, result[self.namespace("power")])
            * local_cost_data[self.namespace("consumption_price")]
            / 3.6e6,
            x=result.index,
        )

        return cost

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)

        if "price" not in config:
            config["price"] = {"plot": []}
        config["price"]["plot"].append(
            {
                "key": self.namespace("consumption_price"),
                "kwargs": {"color": color, "drawstyle": "steps-post"},
            }
        )
        config["price"]["plot"].append(
            {
                "key": self.namespace("production_price"),
                "kwargs": {
                    "color": color,
                    "drawstyle": "steps-post",
                    "alpha": 0.5,
                },
            }
        )

        if "power" not in config:
            config["power"] = {"plot": []}
        config["power"]["plot"].append(
            {
                "key": self.namespace("power"),
                "kwargs": {"color": color, "drawstyle": "steps-post"},
            }
        )
        return config


class MaxGridModel(ComponentModel):
    """
    Models a connection to an electricity grid with limited power and a separate price for production and consumption.

    """

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "raw_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("raw_price"), np.ones(len(self.model.i))
            ).iloc[i],
            doc="The raw commodity price, usually national DAM, without any other price included (EUR/kWh)",
        )
        self.add_parameter(
            "consumption_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("consumption_price"), np.ones(len(self.model.i))
            ).iloc[i],
            doc="The price of grid electricity consumption (EUR/kWh)",
        )
        self.add_parameter(
            "production_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("production_price"),
                0 * np.ones(len(self.model.i)),
            ).iloc[i],
            doc="The price of grid electricity production (EUR/kWh)",
        )
        self.add_parameter(
            "capacity_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("capacity_price"),
                0 * np.ones(len(self.model.i)),
            ).iloc[i],
            doc="The capacity price of grid capacity (EUR/kW)",
        )
        self.add_parameter(
            "fcr_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("fcr_price"),
                pd.Series(0, index=data.index)
            ).iloc[i],
            doc="The FCR price (EUR/MWh/h)",
        )
        self.add_parameter(
            "generation_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("generation_price"),
                pd.Series(0, index=data.index),
            ).iloc[i],
            doc="The generation price of local production (EUR/kWh)",
        )
        self.add_parameter(
            "consumption_power_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("consumption_power_max"),
                10e9 * np.ones(len(self.model.i)),
            ).iloc[i],
            doc="Maximum consumption power from the grid (W)",
        )
        self.add_parameter(
            "production_power_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("production_power_max"),
                10e9 * np.ones(len(self.model.i)),
            ).iloc[i],
            doc="Maximum production power to the grid (W)",
        )
        self.add_parameter(
            "binary_capacity_consumption",
            self.model.i,
            domain=pyomo.Binary,
            initialize=lambda m, i: data.get(
                self.namespace("binary_capacity_consumption"),
                np.ones(len(self.model.i)),
            )[i],
            doc="Capacity consumption (1) or (0) mode (-)",
        )
        self.add_parameter(
            "binary_capacity_production",
            self.model.i,
            domain=pyomo.Binary,
            initialize=lambda m, i: data.get(
                self.namespace("binary_capacity_production"),
                np.zeros(len(self.model.i)),
            )[i],
            doc="Capacity production (1) or (0) mode (-)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                -self.consumption_power_max[i],
                self.production_power_max[i],
            ),
            initialize=0,
            doc="Total grid power, +: production, -: consumption (W)",
        )
        self.add_variable(
            "consumption_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.consumption_power_max[i]),
            initialize=0,
            doc="The consumption power from the grid (W)",
        )
        self.add_variable(
            "production_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.production_power_max[i]),
            initialize=0,
            doc="The production power to the grid (W)",
        )
        self.add_variable(
            "production",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            doc="Production (1) or consumption (0) mode (-)",
        )
        self.add_variable(
            "maximum_capacity",
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The maximum power in the domain (W)",
        )
        self.add_parameter(
            "targeted_capacity",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("targeted_capacity"),
                0 * np.ones(len(self.model.i)),
            )[i],
            doc="Targeted capacity in horizon window, (W)",
        )
        self.add_variable(
            "peak_enlargement",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Capacity increase in optimisation window (W)",
        )
        self.add_variable(
            "maximum_peak_enlargement",
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The maximum peak increase in horizon window, (W)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="The operational costs (EUR)",
        )
        self.add_parameter(
            "constant_violation_scale",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("constant_violation_scale"),
                1e12 * np.ones(len(data.index)),
            )[i],
            doc="Scale factor for the maximum capacity violation",
        )
        self.add_variable(
            "constraint_violation",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_production_consumption_power",
            self.model.i,
            rule=lambda m, i: self.production_power[i] - self.consumption_power[i]
            == self.power[i],
        )
        self.add_constraint(
            "constraint_production",
            self.model.i,
            rule=lambda m, i: self.production_power[i]
            <= self.production[i] * self.production_power_max[i],
        )
        self.add_constraint(
            "constraint_consumption",
            self.model.i,
            rule=lambda m, i: self.consumption_power[i]
            <= (1 - self.production[i]) * self.consumption_power_max[i],
        )

        self.add_constraint(
            "constraint_peak_enlargement",
            self.model.i,
            rule=lambda m, i: self.peak_enlargement[i]
            >= self.maximum_capacity - self.targeted_capacity[i],
        )
        self.add_constraint(
            "constraint_maximum_capacity_consumption",
            self.model.i,
            rule=lambda m, i: self.maximum_capacity
            >= self.consumption_power[i] * self.binary_capacity_consumption[i],
        )
        self.add_constraint(
            "constraint_maximum_capacity_production",
            self.model.i,
            rule=lambda m, i: self.maximum_capacity
            >= self.production_power[i] * self.binary_capacity_production[i],
        )
        self.add_constraint(
            "constraint_maximum_peak_enlargement",
            self.model.i,
            rule=lambda m, i: self.maximum_peak_enlargement >= self.peak_enlargement[i],
        )
        self.add_constraint(
            "constraint_operational_cost_max",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == +(
                self.consumption_power[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                * self.consumption_price[i]
                if i + 1 < len(m.i)
                else self.consumption_power[i]
                * (m.timestamp[i] - m.timestamp[i - 1])
                / 3.6e6
                * self.consumption_price[i]
            )
            - (
                self.production_power[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                * self.production_price[i]
                if i + 1 < len(m.i)
                else self.production_power[i]
                * (m.timestamp[i] - m.timestamp[i - 1])
                / 3.6e6
                * self.production_price[i]
            )
            + self.maximum_peak_enlargement
            / (len(self.model.i) * 1e3)
            * self.capacity_price[i],
        )
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == self.maximum_peak_enlargement * self.constant_violation_scale[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]
        df[self.namespace("raw_price")] = [
            pyomo.value(self.raw_price[i]) for i in self.model.i
        ]
        df[self.namespace("consumption_price")] = [
            pyomo.value(self.consumption_price[i]) for i in self.model.i
        ]
        df[self.namespace("production_price")] = [
            pyomo.value(self.production_price[i]) for i in self.model.i
        ]
        df[self.namespace("capacity_price")] = [
            pyomo.value(self.capacity_price[i]) for i in self.model.i
        ]
        df[self.namespace("fcr_price")] = [
            pyomo.value(self.fcr_price[i]) for i in self.model.i
        ]
        df[self.namespace("generation_price")] = [
            pyomo.value(self.generation_price[i]) for i in self.model.i
        ]
        df[self.namespace("consumption_power")] = [
            pyomo.value(self.consumption_power[i]) for i in self.model.i
        ]
        df[self.namespace("production_power")] = [
            pyomo.value(self.production_power[i]) for i in self.model.i
        ]
        df[self.namespace("consumption_power_max")] = [
            pyomo.value(self.consumption_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("production_power_max")] = [
            pyomo.value(self.production_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]
        df[self.namespace("maximum_capacity")] = pyomo.value(self.maximum_capacity)
        df[self.namespace("maximum_peak_enlargement")] = pyomo.value(
            self.maximum_peak_enlargement
        )
        df[self.namespace("peak_enlargement")] = [
            pyomo.value(self.peak_enlargement[i]) for i in self.model.i
        ]
        df[self.namespace("targeted_capacity")] = [
            pyomo.value(self.targeted_capacity[i]) for i in self.model.i
        ]

        return df


class OwnerMaxGridModel(ComponentModel):
    """
    Models a connection to an electricity grid with limited power and a separate price for production and consumption.
    Difference with MaxGridModel is only in the sharing operational cost factor, which means that owner can share
    energy with tenant and receive income from it
    """

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "consumption_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("consumption_price"), np.ones(len(self.model.i))
            )[i],
            doc="The price of grid electricity consumption (EUR/kWh)",
        )
        self.add_parameter(
            "production_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("production_price"), 0 * np.ones(len(self.model.i))
            )[i],
            doc="The price of grid electricity production (EUR/kWh)",
        )
        self.add_parameter(
            "capacity_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("capacity_price"), 0 * np.ones(len(self.model.i))
            )[i],
            doc="The capacity price of grid capacity (EUR/kW)",
        )
        self.add_parameter(
            "fcr_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("fcr_price"), 0 * np.ones(len(self.model.i))
            )[i],
            doc="The FCR price (EUR/MWh/h)",
        )
        self.add_parameter(
            "generation_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("generation_price"), 0 * np.ones(len(self.model.i))
            )[i],
            doc="The generation price of local production (EUR/kWh)",
        )
        self.add_parameter(
            "consumption_power_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("consumption_power_max"),
                10e7 * np.ones(len(self.model.i)),
            )[i],
            doc="Maximum consumption power from the grid (W)",
        )
        self.add_parameter(
            "production_power_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("production_power_max"),
                10e7 * np.ones(len(self.model.i)),
            )[i],
            doc="Maximum production power to the grid (W)",
        )
        self.add_parameter(
            "binary_capacity_consumption",
            self.model.i,
            domain=pyomo.Binary,
            initialize=lambda m, i: data.get(
                self.namespace("binary_capacity_consumption"),
                np.ones(len(self.model.i)),
            )[i],
            doc="Capacity consumption (1) or (0) mode (-)",
        )
        self.add_parameter(
            "binary_capacity_production",
            self.model.i,
            domain=pyomo.Binary,
            initialize=lambda m, i: data.get(
                self.namespace("binary_capacity_production"),
                np.zeros(len(self.model.i)),
            )[i],
            doc="Capacity production (1) or (0) mode (-)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                -self.consumption_power_max[i],
                self.production_power_max[i],
            ),
            initialize=0,
            doc="Total grid power, +: production, -: consumption (W)",
        )
        self.add_variable(
            "consumption_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.consumption_power_max[i]),
            initialize=0,
            doc="The consumption power from the grid (W)",
        )
        self.add_variable(
            "production_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.production_power_max[i]),
            initialize=0,
            doc="The production power to the grid (W)",
        )
        self.add_variable(
            "production",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            doc="Production (1) or consumption (0) mode (-)",
        )
        self.add_variable(
            "maximum_capacity",
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The maximum power in the domain (W)",
        )
        self.add_parameter(
            "targeted_capacity",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("targeted_capacity"), 0 * np.ones(len(self.model.i))
            )[i],
            doc="Targeted capacity in horizon window, (W)",
        )
        self.add_variable(
            "peak_enlargement",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Capacity increase in optimisation window (W)",
        )
        self.add_variable(
            "maximum_peak_enlargement",
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The maximum peak increase in horizon window, (W)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="The operational costs (EUR)",
        )
        self.add_variable(
            "sharing_operational_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="The sharing operational costs (EUR)",
        )
        self.add_parameter(
            "constant_violation_scale",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("constant_violation_scale"),
                1e12 * np.ones(len(data.index)),
            )[i],
            doc="Scale factor for the maximum capacity violation",
        )
        self.add_variable(
            "constraint_violation",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_production_consumption_power",
            self.model.i,
            rule=lambda m, i: self.production_power[i] - self.consumption_power[i]
            == self.power[i],
        )
        self.add_constraint(
            "constraint_production",
            self.model.i,
            rule=lambda m, i: self.production_power[i]
            <= self.production[i] * self.production_power_max[i],
        )
        self.add_constraint(
            "constraint_consumption",
            self.model.i,
            rule=lambda m, i: self.consumption_power[i]
            <= (1 - self.production[i]) * self.consumption_power_max[i],
        )

        self.add_constraint(
            "constraint_peak_enlargement",
            self.model.i,
            rule=lambda m, i: self.peak_enlargement[i]
            >= self.maximum_capacity - self.targeted_capacity[i],
        )
        self.add_constraint(
            "constraint_maximum_capacity_consumption",
            self.model.i,
            rule=lambda m, i: self.maximum_capacity
            >= self.consumption_power[i] * self.binary_capacity_consumption[i],
        )
        self.add_constraint(
            "constraint_maximum_capacity_production",
            self.model.i,
            rule=lambda m, i: self.maximum_capacity
            >= self.production_power[i] * self.binary_capacity_production[i],
        )
        self.add_constraint(
            "constraint_maximum_peak_enlargement",
            self.model.i,
            rule=lambda m, i: self.maximum_peak_enlargement >= self.peak_enlargement[i],
        )
        self.add_constraint(
            "constraint_operational_cost_max",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == +(
                self.consumption_power[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                * self.consumption_price[i]
                if i + 1 < len(m.i)
                else self.consumption_power[i]
                * (m.timestamp[i] - m.timestamp[i - 1])
                / 3.6e6
                * self.consumption_price[i]
            )
            + self.sharing_operational_cost[i]
            - (
                self.production_power[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                * self.production_price[i]
                if i + 1 < len(m.i)
                else self.production_power[i]
                * (m.timestamp[i] - m.timestamp[i - 1])
                / 3.6e6
                * self.production_price[i]
            )
            + self.maximum_peak_enlargement
            / (len(self.model.i) * 1e3)
            * self.capacity_price[i],
        )
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == self.maximum_peak_enlargement * self.constant_violation_scale[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]
        df[self.namespace("consumption_price")] = [
            pyomo.value(self.consumption_price[i]) for i in self.model.i
        ]
        df[self.namespace("production_price")] = [
            pyomo.value(self.production_price[i]) for i in self.model.i
        ]
        df[self.namespace("capacity_price")] = [
            pyomo.value(self.capacity_price[i]) for i in self.model.i
        ]
        df[self.namespace("fcr_price")] = [
            pyomo.value(self.fcr_price[i]) for i in self.model.i
        ]
        df[self.namespace("generation_price")] = [
            pyomo.value(self.generation_price[i]) for i in self.model.i
        ]
        df[self.namespace("consumption_power")] = [
            pyomo.value(self.consumption_power[i]) for i in self.model.i
        ]
        df[self.namespace("production_power")] = [
            pyomo.value(self.production_power[i]) for i in self.model.i
        ]
        df[self.namespace("consumption_power_max")] = [
            pyomo.value(self.consumption_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("production_power_max")] = [
            pyomo.value(self.production_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]
        df[self.namespace("maximum_capacity")] = pyomo.value(self.maximum_capacity)
        df[self.namespace("maximum_peak_enlargement")] = pyomo.value(
            self.maximum_peak_enlargement
        )
        df[self.namespace("peak_enlargement")] = [
            pyomo.value(self.peak_enlargement[i]) for i in self.model.i
        ]
        df[self.namespace("targeted_capacity")] = [
            pyomo.value(self.targeted_capacity[i]) for i in self.model.i
        ]

        return df


class GridSharingModel(ComponentModel):
    """
    The model presents a connection point for sharing between owner and tenant. Owner can only sell energy to the
    tenant, that's how "owner_power" is created, tenant can only buy energy from the tenant, that's how
    "tenant_power" is created. They linked to each other. Also model should contain production_consumption_price or
    sharing price. This variable should have a same unit as in MaxGridModel to calculate resulting operational cost
    properly
    """

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "production_consumption_price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("production_consumption_price"),
                0.130 * np.ones(len(self.model.i)),
            )[i],
            doc="The sharing price between owner and tenant (EUR/kW)",
        )
        self.add_variable(
            "owner_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, 1e9),
            initialize=0,
            doc=(
                "The power from the owner assets (pv, battery, etc.) to sell to"
                " tenant (W)"
            ),
        )
        self.add_variable(
            "tenant_power",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-1e9, 0),
            initialize=0,
            doc="The power comes to tenant from the owner (W)",
        )
        self.add_variable(
            "owner_operational_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )
        self.add_variable(
            "tenant_operational_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_production",
            self.model.i,
            rule=lambda m, i: self.owner_power[i] == -self.tenant_power[i],
        )
        self.add_constraint(
            "constraint_owner_operational_cost",
            self.model.i,
            rule=lambda m, i: self.owner_operational_cost[i]
            == -(
                self.owner_power[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                * self.production_consumption_price[i]
                if i + 1 < len(m.i)
                else self.owner_power[i]
                * (m.timestamp[i] - m.timestamp[i - 1])
                / 3.6e6
                * self.production_consumption_price[i]
            ),
        )
        self.add_constraint(
            "constraint_tenant_operational_cost",
            self.model.i,
            rule=lambda m, i: self.tenant_operational_cost[i]
            == -self.owner_operational_cost[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("owner_power")] = [
            pyomo.value(self.owner_power[i]) for i in self.model.i
        ]
        df[self.namespace("tenant_power")] = [
            -pyomo.value(self.tenant_power[i]) for i in self.model.i
        ]
        df[self.namespace("owner_operational_cost")] = [
            pyomo.value(self.owner_operational_cost[i]) for i in self.model.i
        ]
        df[self.namespace("tenant_operational_cost")] = [
            pyomo.value(self.tenant_operational_cost[i]) for i in self.model.i
        ]
        df[self.namespace("production_consumption_price")] = [
            pyomo.value(self.production_consumption_price[i]) for i in self.model.i
        ]

        return df


class GridModelConnectionCost(MaxGridModel):
    """Optimise Grid capacity

    The cost for the connection is included in the optimisation
    so an optimal connection is selected based on the cost for
    an increased connection (cost = EUR/kW/year)
    """

    _ceil = None
    _priceConnectionPerYearPerkWh = 0

    def __init__(self, *args, cost: float, ceil: int = 5, **kwargs):
        super().__init__(*args, **kwargs)

        self._ceil = ceil
        self._priceConnectionPerYearPerkWh = cost

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        # Overwrite the cost function
        self.add_constraint(
            "constraint_operational_cost_max",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == +(
                self.consumption_power[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                * self.consumption_price[i]
                if i + 1 < len(m.i)
                else self.consumption_power[i]
                * (m.timestamp[i] - m.timestamp[i - 1])
                / 3.6e6
                * self.consumption_price[i]
            )
            - (
                self.production_power[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                * self.production_price[i]
                if i + 1 < len(m.i)
                else self.production_power[i]
                * (m.timestamp[i] - m.timestamp[i - 1])
                / 3.6e6
                * self.production_price[i]
            )
            + self.maximum_peak_enlargement
            / (len(self.consumption_power) * 1e3)
            * self.capacity_price[i]
            + (
                (
                    self.maximum_capacity
                    * self._priceConnectionPerYearPerkWh
                    * (m.timestamp[i + 1] - m.timestamp[i])
                    / (365 * 24 * 3.6e3 * 1e3)
                )
                if i + 1 < len(m.i)
                else (
                    self.maximum_capacity
                    * self._priceConnectionPerYearPerkWh
                    * (m.timestamp[i] - m.timestamp[i - 1])
                    / (365 * 24 * 3.6e3 * 1e3)
                )
            ),
        )


class SoftPowerConstraintBaseModel(GridModel):
    def __init__(
        self, *args, power_soft_min_index=None, power_soft_max_index=None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        if power_soft_min_index is None:
            self.power_soft_min_index = []
        else:
            self.power_soft_min_index = power_soft_min_index
        if power_soft_max_index is None:
            self.power_soft_max_index = []
        else:
            self.power_soft_max_index = power_soft_max_index

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self.add_parameter(
            "power_soft_min",
            self.model.i,
            self.power_soft_min_index,
            initialize=lambda m, i, k: -data[
                self.namespace("power_soft_min_{}".format(k))
            ][i],
            doc="Minimum power (W)",
        )
        self.add_parameter(
            "power_soft_max",
            self.model.i,
            self.power_soft_max_index,
            initialize=lambda m, i, k: -data[
                self.namespace("power_soft_max_{}".format(k))
            ][i],
            doc="Maximum power (W)",
        )
        self.add_variable(
            "power_min_slack",
            self.model.i,
            self.power_soft_min_index,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i, k: 0,
            doc="Consumption power below the soft min (W)",
        )
        self.add_variable(
            "power_max_slack",
            self.model.i,
            self.power_soft_max_index,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i, k: 0,
            doc="Consumption power above the soft max (W)",
        )
        self.add_parameter(
            "power_max_constraint_violation_scale",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("power_max_constraint_violation_scale"),
                1 * np.ones(len(m.i)),
            )[i],
            doc="Scale factor for the power constraint violation (EUR / kWh)",
        )
        self.add_parameter(
            "power_min_constraint_violation_scale",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("power_min_constraint_violation_scale"),
                1 * np.ones(len(m.i)),
            )[i],
            doc="Scale factor for the power constraint violation (EUR / kWh)",
        )
        self.add_variable(
            "power_constraint_violation",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: 0,
            doc="Scaled power constraint violation (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_power_min_slack",
            self.model.i,
            self.power_soft_min_index,
            rule=lambda m, i, k: (
                self.power_min_slack[i, k] >= self.power_soft_min[i, k] - self.power[i]
                if not np.isnan(self.power_soft_min[i, k])
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_power_max_slack",
            self.model.i,
            self.power_soft_max_index,
            rule=lambda m, i, k: (
                self.power_max_slack[i, k] >= self.power[i] - self.power_soft_max[i, k]
                if not np.isnan(self.power_soft_max[i, k])
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_power_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.power_constraint_violation[i]
            == +(
                sum(
                    self.power_min_slack[i, k]
                    * (m.timestamp[i + 1] - m.timestamp[i])
                    / 3.6e6
                    * self.power_min_constraint_violation_scale[i]
                    for k in self.power_soft_min_index
                )
                if i + 1 < len(m.i)
                else 0
            )
            + (
                sum(
                    self.power_max_slack[i, k]
                    * (m.timestamp[i + 1] - m.timestamp[i])
                    / 3.6e6
                    * self.power_max_constraint_violation_scale[i]
                    for k in self.power_soft_max_index
                )
                if i + 1 < len(m.i)
                else 0
            ),
        )

    def get_results(self):
        results = super().get_results()
        for k in self.power_soft_max_index:
            results[self.namespace("power_soft_min_{}".format(k))] = [
                -pyomo.value(self.power_soft_max[i, k]) for i in self.model.i
            ]
        for k in self.power_soft_min_index:
            results[self.namespace("power_soft_max_{}".format(k))] = [
                -pyomo.value(self.power_soft_min[i, k]) for i in self.model.i
            ]
        return results

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)
        if "power" not in config:
            config["power"] = {"plot": []}

        # for i, key in enumerate(self.power_soft_min_index):
        #     config['power']['plot'].append({
        #         'key': self.namespace('power_soft_max_{}'.format(key)),
        #         'kwargs': {'color': color, 'drawstyle': 'steps-post', 'marker': 'v', 'linestyle': '',
        #                    'label': ('' if i > 0 else None), 'alpha': np.exp(-i*0.8)}}
        #     )
        # for i, key in enumerate(self.power_soft_max_index):
        #     config['power']['plot'].append({
        #         'key': self.namespace('power_soft_min_{}'.format(key)),
        #         'kwargs': {'color': color, 'drawstyle': 'steps-post', 'marker': '^', 'linestyle': '',
        #                    'label': ('' if i > 0 else None), 'alpha': np.exp(-i*0.8)}}
        #     )
        # FIXME if the control is not run (extend model variables) there is no power_soft_min_index
        if len(self.power_soft_min_index) > 0:
            config["power"]["plot"].append(
                {
                    "key": self.namespace(
                        "power_soft_max_{}".format(self.power_soft_min_index[0])
                    ),
                    "kwargs": {
                        "color": color,
                        "drawstyle": "steps-post",
                        "label": "",
                        "marker": "v",
                        "linestyle": "",
                        "alpha": 0.3,
                    },
                }
            )
        if len(self.power_soft_max_index) > 0:
            config["power"]["plot"].append(
                {
                    "key": self.namespace(
                        "power_soft_min_{}".format(self.power_soft_max_index[0])
                    ),
                    "kwargs": {
                        "color": color,
                        "drawstyle": "steps-post",
                        "label": "",
                        "marker": "^",
                        "linestyle": "",
                        "alpha": 0.3,
                    },
                }
            )
        return config

    def to_dict(self):
        config = super().to_dict()
        config["parameters"]["power_soft_min_index"] = self.power_soft_min_index
        config["parameters"]["power_soft_max_index"] = self.power_soft_max_index
        return config


class SoftPowerConstraintModel(SoftPowerConstraintBaseModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.model.del_component(self.model_namespace("power"))
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0.0,
            doc="Actual power production (W)",
        )
        self.add_variable(
            "constraint_violation",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0.0,
            doc="Constraint violation (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == self.power_constraint_violation[i],
        )

    def get_results(self):
        results = super().get_results()
        results[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]
        return results

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


class CorrectingSoftPowerConstraintBaseModel(SoftPowerConstraintBaseModel):
    def __init__(self, *args, power_constraint_resolution=900, **kwargs):
        super().__init__(*args, **kwargs)
        self.power_constraint_resolution = power_constraint_resolution

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_variable(
            "power_average",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Average power over the constraint intervals (W)",
        )
        self.add_parameter(
            "power_past",
            self.model.i,
            initialize=lambda m, i: -data[self.namespace("power_past")][i],
            doc="Power already consumed or produced in the past (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        self.add_constraint(
            "contraint_power_average",
            self.model.i,
            rule=lambda m, i: (
                self.power_average[i]
                == sum(
                    self.power[j] * (m.timestamp[j + 1] - m.timestamp[j])
                    for j in data[self.namespace("constraint_indices")][i]
                )
                / (
                    m.timestamp[data[self.namespace("constraint_indices")][i][-1] + 1]
                    - m.timestamp[data[self.namespace("constraint_indices")][i][0]]
                )
                if i + 1 < len(self.model.i)
                else pyomo.Constraint.Skip
            ),
        )
        # FIXME when a set of constraint_indices does not contain power past values powers should be te same
        self.add_constraint(
            "contraint_power_past",
            self.model.i,
            rule=lambda m, i: (
                self.power[i] == self.power_past[i]
                if not np.isnan(self.power_past[i])
                else pyomo.Constraint.Skip
            ),
        )

        self.model.del_component(self.model_namespace("constraint_power_min_slack"))
        self.model.del_component(
            self.model_namespace("constraint_power_min_slack_index")
        )
        self.model.del_component(
            self.model_namespace("constraint_power_min_slack_index_1")
        )
        self.add_constraint(
            "constraint_power_min_slack",
            self.model.i,
            self.power_soft_min_index,
            rule=lambda m, i, k: (
                self.power_min_slack[i, k]
                >= self.power_soft_min[i, k] - self.power_average[i]
                if not np.isnan(self.power_soft_min[i, k])
                else pyomo.Constraint.Skip
            ),
        )
        self.model.del_component(self.model_namespace("constraint_power_max_slack"))
        self.model.del_component(self.model_namespace("constraint_power_max_slack"))
        self.model.del_component(
            self.model_namespace("constraint_power_max_slack_index")
        )
        self.model.del_component(
            self.model_namespace("constraint_power_max_slack_index_1")
        )
        self.add_constraint(
            "constraint_power_max_slack",
            self.model.i,
            self.power_soft_max_index,
            rule=lambda m, i, k: (
                self.power_max_slack[i, k]
                >= self.power_average[i] - self.power_soft_max[i, k]
                if not np.isnan(self.power_soft_max[i, k])
                else pyomo.Constraint.Skip
            ),
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power_past")] = [
            -pyomo.value(self.power_past[i]) for i in self.model.i
        ]
        df[self.namespace("power_average")] = [
            -pyomo.value(self.power_average[i]) for i in self.model.i
        ]
        return df

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)

        if "power" not in config:
            config["power"] = {"plot": []}
        config["power"]["plot"].append(
            {
                "key": self.namespace("power_past"),
                "kwargs": {
                    "color": color,
                    "drawstyle": "steps-post",
                    "marker": "o",
                    "linestyle": "",
                },
            }
        )
        config["power"]["plot"].append(
            {
                "key": self.namespace("power_average"),
                "kwargs": {
                    "color": color,
                    "drawstyle": "steps-post",
                    "marker": "o",
                    "linestyle": "",
                    "alpha": 0.4,
                },
            }
        )
        return config

    def to_dict(self):
        config = super().to_dict()
        config["parameters"][
            "power_constraint_resolution"
        ] = self.power_constraint_resolution
        return config


class CorrectingSoftPowerConstraintModel(
    CorrectingSoftPowerConstraintBaseModel, SoftPowerConstraintModel
):
    pass


class LoadFollowingGridModel(GridModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        power_threshold_index = []
        for key in data.columns:
            s = self.namespace("power_threshold_")
            if s in key:
                power_threshold_index.append(key[len(s) :])

        self.power_threshold_index = power_threshold_index

        self.add_parameter(
            "price_above_threshold",
            self.model.i,
            self.power_threshold_index,
            initialize=lambda m, i, j: data.get(
                self.namespace("price_threshold_{}".format(j)),
                np.zeros(len(data.index)),
            )[i],
            doc=(
                "Time dependent additional price for power higher than the"
                " threshold (EUR/kWh)"
            ),
        )

        self.add_parameter(
            "price_below_threshold",
            self.model.i,
            self.power_threshold_index,
            initialize=lambda m, i, j: data.get(
                self.namespace("price_threshold_{}".format(j)),
                np.zeros(len(data.index)),
            )[i],
            doc=(
                "Time dependent additional price for power lower than the"
                " threshold (EUR/kWh)"
            ),
        )

        self.add_parameter(
            "power_threshold",
            self.model.i,
            self.power_threshold_index,
            initialize=lambda m, i, j: data.get(
                self.namespace("power_threshold_{}".format(j)),
                100 * np.ones(len(data.index)),
            )[i],
            doc="Time dependent power threshold delta (W)",
        )
        self.add_parameter(
            "power_setpoint",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("power_setpoint")][i],
            doc="Time dependent power setpoint (W)",
        )

        self.add_variable(
            "power_above_threshold",
            self.model.i,
            self.power_threshold_index,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The power above a threshold (W)",
        )

        self.add_variable(
            "power_below_threshold",
            self.model.i,
            self.power_threshold_index,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The power below a threshold (W)",
        )
        self.add_variable(
            "constraint_violation",
            self.model.i,
            initialize=0,
            doc="The constraint violation (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        self.add_constraint(
            "constraint_power_above_threshold",
            self.model.i,
            self.power_threshold_index,
            rule=lambda m, i, j: self.power_above_threshold[i, j]
            >= self.consumption_power[i]
            - (self.power_setpoint[i] + self.power_threshold[i, j]),
        )

        self.add_constraint(
            "constraint_power_below_threshold",
            self.model.i,
            self.power_threshold_index,
            rule=lambda m, i, j: self.power_below_threshold[i, j]
            >= (self.power_setpoint[i] - self.power_threshold[i, j])
            - self.consumption_power[i],
        )
        self.add_parameter(
            "constraint_violation_scale",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("constraint_violation_scale")][
                i
            ],
            doc="Scale factor for the constraint violation (EUR / kW h)",
        )

        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == +(
                sum(
                    self.power_above_threshold[i, j]
                    * (m.timestamp[i + 1] - m.timestamp[i])
                    / 3.6e6
                    * self.price_above_threshold[i, j]
                    * self.constraint_violation_scale[i]
                    for j in self.power_threshold_index
                )
                if i + 1 < len(m.i)
                else 0
            )
            + (
                sum(
                    self.power_below_threshold[i, j]
                    * (m.timestamp[i + 1] - m.timestamp[i])
                    / 3.6e6
                    * self.price_below_threshold[i, j]
                    * self.constraint_violation_scale[i]
                    for j in self.power_threshold_index
                )
                if i + 1 < len(m.i)
                else 0
            ),
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power_setpoint")] = [
            pyomo.value(self.power_setpoint[i]) for i in self.model.i
        ]
        df[self.namespace("power_above_threshold_0")] = [
            pyomo.value(self.power_above_threshold[i, "0"]) for i in self.model.i
        ]
        df[self.namespace("power_above_threshold_1")] = [
            pyomo.value(self.power_above_threshold[i, "1"]) for i in self.model.i
        ]
        df[self.namespace("power_above_threshold_2")] = [
            pyomo.value(self.power_above_threshold[i, "2"]) for i in self.model.i
        ]
        df[self.namespace("power_below_threshold_0")] = [
            pyomo.value(self.power_below_threshold[i, "0"]) for i in self.model.i
        ]
        df[self.namespace("power_below_threshold_1")] = [
            pyomo.value(self.power_below_threshold[i, "1"]) for i in self.model.i
        ]
        df[self.namespace("power_below_threshold_2")] = [
            pyomo.value(self.power_below_threshold[i, "2"]) for i in self.model.i
        ]

        return df

class ImbalanceMarketModel(ComponentModel):
    """
    Models the electricity imbalance market

    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "price",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("price"),
                0 * np.ones(len(self.model.i)),
            )[i],
            doc="The price of imbalance market (+consumption and -production) (EUR/kWh)",
        )
        self.add_parameter(
            "consumption_power_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("consumption_power_max"),
                0 * np.ones(len(self.model.i)),
            )[i],
            doc="Maximum consumption power allowed to work on imbalance market (W)",
        )
        self.add_parameter(
            "production_power_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("production_power_max"),
                0 * np.ones(len(self.model.i)),
            )[i],
            doc="Maximum production power allowed to work on imbalance market (W)",
        )
        self.add_parameter(
            "price_predictability_factor",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("price_predictability_factor"),
                np.ones(len(self.model.i)),
            )[i],
            domain=pyomo.Reals,
            doc="The factor that says if we can predict price value or no "
                "from 0 to 1 indicating how certain we are in the forecast",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Total imbalance power, +: production, -: consumption (W)",
        )
        # self.add_variable(
        #     "production",
        #     self.model.i,
        #     domain=pyomo.Binary,
        #     initialize=0,
        #     doc="Production (1) or consumption (0) mode (-)",
        # )
        self.add_variable(
            "cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="The imbalance market operational costs (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_production_power",
            self.model.i,
            rule=lambda m, i: -self.production_power_max[i] <= self.power[i],
        )
        self.add_constraint(
            "constraint_consumption_power",
            self.model.i,
            rule=lambda m, i: -self.power[i] <= self.consumption_power_max[i],
        )
        self.add_constraint(
            "constraint_predictability",
            self.model.i,
            rule=lambda m, i: self.power[i]
                              == self.power[i] * self.price_predictability_factor[i],
        )
        # self.add_constraint(
        #     "constraint_consumption",
        #     self.model.i,
        #     rule=lambda m, i: self.consumption_power[i]
        #                       <= (1 - self.production[i]) * self.consumption_power_max[i],
        # )
        """
        self.add_constraint(
            'constraint_maximum_capacity_production',
            self.model.i,
            rule=lambda m, i: 
            (self.maximum_capacity >= self.production_power[i]) # if self.production[i] == 0 else maximum_capacity >= self.production_power[i])
        )
        """
        """
        self.add_constraint(
            'constraint_maximum_capacity_consumption',
            self.model.i,
            rule=lambda m, i: 
            self.maximum_capacity >= self.consumption_power[i]
        )
        """
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.cost[i]
                              == (
                -self.power[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                * self.price[i]
                if i + 1 < len(m.i)
                else 0
            )
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]
        df[self.namespace("price")] = [
            pyomo.value(self.price[i]) for i in self.model.i
        ]
        df[self.namespace("cost")] = [
            pyomo.value(self.cost[i]) for i in self.model.i
        ]
        df[self.namespace("price_predictability_factor")] = [
            pyomo.value(self.price_predictability_factor[i]) for i in self.model.i
        ]

        return df


component_models = {
    "GridModel": GridModel,
    "MaxGridModel": MaxGridModel,
    "SoftPowerConstraintModel": SoftPowerConstraintModel,
    "CorrectingSoftPowerConstraintModel": CorrectingSoftPowerConstraintModel,
    "LoadFollowingGridModel": LoadFollowingGridModel,
    "GridSharingModel": GridSharingModel,
    "OwnerMaxGridModel": OwnerMaxGridModel,
}
