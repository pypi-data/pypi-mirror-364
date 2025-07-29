import logging

import numpy as np
import pyomo.environ as pyomo

from imby.simulations.custom_simulations.models.base import ComponentModel

logger = logging.getLogger(__name__)


class StandardEnergyMarketModel(ComponentModel):
    """
    A model for representing trade on the standard energy markets: Day Ahead and Imbalance.

    The market sign convention is that positive power corresponds to electricity production or sales.
    The model decides on which market to buy or sell energy based on an estimate of the market price, and a positive
    and negative quantile price for the imbalance markets. Furthermore trade on a specific market can
    be restricted by setting minimum and maximum power quantities.

    Imbalance costs are taken into account in a safe way by taking a quantile of the pos and neg price into account and
    consider the maximum cost that is likely to occur.
    E.g.::

        day_ahead_power_committed = -1000 kW # buying energy on the imbalance market
        day_ahead_price = 0.080 EUR / kWh
        imbalance_price_pos_lower_quantile = 0.000 EUR / kWh
        imbalance_price_neg_upper_quantile = 0.100 EUR / kWh

        power = 0 kW
        imbalance_power = 1000 kW  # selling energy on the imbalance market
        cost = 1000 x 0.080 + max(- 1000 x 0.000, 1000 x 0.100) = 80 + max(0,  100) = 180 EUR / h

        power = -2000 kW
        cost = 1000 x 0.080 + max( 1000 x 0.000, - 1000 x 0.100) = 80 + max(0, - 100) = 80 EUR / h

    Notes
    -----

    ``data:``

    day_ahead_power_min : (W)
    day_ahead_power_max : (W)
    day_ahead_power_committed : (W)
    day_ahead_price : (EUR/kWh)
    imbalance_power_min : (W)
    imbalance_power_max : (W)
    imbalance_uncertainty_price_pos : (EUR/kWh)
    imbalance_uncertainty_price_neg : (EUR/kWh)
    imbalance_price_pos_lower_quantile : (EUR/kWh)
        The expected lowest price received for producing more energy than nominated.
    imbalance_price_neg_upper_quantile : (EUR/kWh)
        The expected highest price paid for consuming more energy than nominated.

    ``parameters:``

    ``initial_conditions:``

    ``variables:``

    power : (W)
    day_ahead_power : (W)
    imbalance_power : (W)
    imbalance_worst_case_cost (EUR)
        The cost incurred by imbalance in the worst case ( % quantile) scenario.
    operational_cost

    ``results:``

    power : (W)
    day_ahead_power : (W)
    imbalance_power : (W)
    day_ahead_price : (EUR/kWh)
    imbalance_price : (EUR/kWh)

    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        # day_ahead
        self.add_parameter(
            "day_ahead_power_min",
            self.model.i,
            initialize=lambda m, i: -data.get(
                self.namespace("day_ahead_power_max"), 1e9 * np.ones(len(data))
            )[i],
        )
        self.add_parameter(
            "day_ahead_power_max",
            self.model.i,
            initialize=lambda m, i: -data.get(
                self.namespace("day_ahead_power_min"),
                -1e9 * np.ones(len(data)),
            )[i],
        )
        self.add_variable(
            "day_ahead_power",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                self.day_ahead_power_min[i],
                self.day_ahead_power_max[i],
            ),
            initialize=0.0,
        )
        self.add_parameter(
            "day_ahead_power_committed",
            self.model.i,
            initialize=lambda m, i: -data.get(
                self.namespace("day_ahead_power_committed"),
                np.nan * np.ones(len(data)),
            )[i],
        )
        self.add_parameter(
            "day_ahead_price",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("day_ahead_price")][i],
        )
        self.add_variable(
            "day_ahead_cost", self.model.i, domain=pyomo.Reals, initialize=0.0
        )

        # imbalance
        self.add_parameter(
            "imbalance_power_min",
            self.model.i,
            initialize=lambda m, i: -data.get(
                self.namespace("imbalance_power_max"), 1e6 * np.ones(len(data))
            )[i],
        )
        self.add_parameter(
            "imbalance_power_max",
            self.model.i,
            initialize=lambda m, i: -data.get(
                self.namespace("imbalance_power_min"),
                -1e6 * np.ones(len(data)),
            )[i],
        )
        self.add_variable(
            "imbalance_power",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                self.imbalance_power_min[i],
                self.imbalance_power_max[i],
            ),
            initialize=0.0,
        )
        self.add_parameter(
            "imbalance_price_pos_lower_quantile",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("imbalance_price_pos_lower_quantile"),
                0.0 * np.ones(len(data)),
            )[i],
        )
        self.add_parameter(
            "imbalance_price_neg_upper_quantile",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("imbalance_price_neg_upper_quantile"),
                1.0 * np.ones(len(data)),
            )[i],
        )
        self.add_variable(
            "imbalance_worst_case_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
        )
        self.add_variable("power", self.model.i, domain=pyomo.Reals, initialize=0.0)
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0.0,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        self.add_constraint(
            "constraint_day_ahead_power",
            self.model.i,
            rule=lambda m, i: (
                self.day_ahead_power[i] == self.day_ahead_power_committed[i]
                if not np.isnan(self.day_ahead_power_committed[i])
                else pyomo.Constraint.Skip
            ),
        )

        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i]
            == self.day_ahead_power[i] + self.imbalance_power[i],
        )
        self.add_constraint(
            "constraint_day_ahead_cost",
            self.model.i,
            rule=lambda m, i: self.day_ahead_cost[i]
            == -self.day_ahead_power[i]
            * self.day_ahead_price[i]
            * (m.timestamp[i + 1] - m.timestamp[i] if i + 1 < len(m.i) else 60)
            / 3.6e6,
        )

        self.add_constraint(
            "constraint_imbalance_worst_case_cost_pos",
            self.model.i,
            rule=lambda m, i: self.imbalance_worst_case_cost[i]
            >= self.imbalance_power[i]
            * self.imbalance_price_pos_lower_quantile[i]
            * (m.timestamp[i + 1] - m.timestamp[i] if i + 1 < len(m.i) else 60)
            / 3.6e6,
        )
        self.add_constraint(
            "constraint_imbalance_worst_case_cost_neg",
            self.model.i,
            rule=lambda m, i: self.imbalance_worst_case_cost[i]
            >= -self.imbalance_power[i]
            * self.imbalance_price_neg_upper_quantile[i]
            * (m.timestamp[i + 1] - m.timestamp[i] if i + 1 < len(m.i) else 60)
            / 3.6e6,
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == self.day_ahead_cost[i] + self.imbalance_worst_case_cost[i],
        )

    def get_results(self):
        results = super().get_results()
        results[self.namespace("day_ahead_power")] = [
            -pyomo.value(self.day_ahead_power[i]) for i in self.model.i
        ]
        results[self.namespace("imbalance_power")] = [
            -pyomo.value(self.imbalance_power[i]) for i in self.model.i
        ]
        results[self.namespace("day_ahead_price")] = [
            pyomo.value(self.day_ahead_price[i]) for i in self.model.i
        ]
        results[self.namespace("imbalance_price_pos_lower_quantile")] = [
            pyomo.value(self.imbalance_price_pos_lower_quantile[i])
            for i in self.model.i
        ]
        results[self.namespace("imbalance_price_neg_upper_quantile")] = [
            pyomo.value(self.imbalance_price_neg_upper_quantile[i])
            for i in self.model.i
        ]
        results[self.namespace("day_ahead_cost")] = [
            pyomo.value(self.day_ahead_cost[i]) for i in self.model.i
        ]
        results[self.namespace("imbalance_worst_case_cost")] = [
            pyomo.value(self.imbalance_worst_case_cost[i]) for i in self.model.i
        ]
        results[self.namespace("power")] = [
            -pyomo.value(self.power[i]) for i in self.model.i
        ]
        return results

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)
        if "energy_market" not in config:
            config["energy_market"] = {"plot": []}
        config["energy_market"]["plot"].append(
            {
                "key": self.namespace("day_ahead_power"),
                "kwargs": {
                    "color": color,
                    "drawstyle": "steps-post",
                    "linestyle": "-",
                },
            }
        )
        config["energy_market"]["plot"].append(
            {
                "key": self.namespace("imbalance_power"),
                "kwargs": {
                    "color": color,
                    "drawstyle": "steps-post",
                    "linestyle": "-",
                    "alpha": 0.5,
                },
            }
        )

        if "price" not in config:
            config["price"] = {"plot": []}
        config["price"]["plot"].append(
            {
                "key": self.namespace("day_ahead_price"),
                "kwargs": {
                    "color": color,
                    "drawstyle": "steps-post",
                    "linestyle": "-",
                },
            }
        )
        return config
