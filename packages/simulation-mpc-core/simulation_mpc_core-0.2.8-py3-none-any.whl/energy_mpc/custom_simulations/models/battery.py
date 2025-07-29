import numpy as np
import pandas as pd
import pyomo.environ as pyomo

from ..conf import ConstraintViolationMultiplier
from .base import ComponentModel


class BaseBatteryModel(ComponentModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [self.namespace("energy")]

        self.add_parameter(
            "energy_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("energy_min"), 0 * np.ones(len(data))
            )[i],
            doc="Minimum battery energy (kWh)",
        )
        self.add_parameter(
            "energy_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("energy_max")][i],
            doc="Maximum battery energy (kWh)",
        )
        self.add_parameter(
            "charge_power_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("charge_power_max")][i],
            doc="Maximum battery charge power (W)",
        )
        self.add_parameter(
            "discharge_power_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("discharge_power_max")][i],
            doc="Maximum battery discharge power (W)",
        )
        self.add_parameter(
            "self_discharge",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("self_discharge"), np.zeros(len(data.index))
            )[i],
            doc=(
                "Battery self discharge, must be less than 1/dt for stability (W/J) or"
                " (1/s)"
            ),
        )
        self.add_parameter(
            "charge_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("charge_efficiency"), np.ones(len(data.index))
            )[i],
            doc="Battery charge efficiency (-)",
        )
        self.add_parameter(
            "discharge_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("discharge_efficiency"), np.ones(len(data.index))
            )[i],
            doc="Battery discharge efficiency (-)",
        )
        self.add_parameter(
            "capacity_cost_per_cycle",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("capacity_cost_per_cycle"), 0 * np.ones(len(data.index))
            )[i],
            doc=(
                "Cost of the battery divided by the capacity and the number of cycles"
                " (EUR / kWh / Cycle)"
            ),
        )
        self.add_parameter(
            "energy_ini",
            initialize=lambda m: min(
                self.energy_max[0] - 1e-3,
                max(self.energy_min[0] + 1e-3, ini.get(self.namespace("energy"), 0)),
            ),
            doc="Initial battery energy (kWh)",
        )

        self.add_variable(
            "energy",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (self.energy_min[i], self.energy_max[i]),
            initialize=0,
            doc="Battery energy (kWh)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Battery power +: charging, -: discharging (W)",
        )
        self.add_variable(
            "charge_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.charge_power_max[i]),
            initialize=0,
        )
        self.add_variable(
            "discharge_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.discharge_power_max[i]),
            initialize=0,
        )
        self.add_variable(
            "charging",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_energy",
            self.model.i,
            rule=lambda m, i: (
                (self.energy[i + 1] - self.energy[i])
                * 3.6e6
                / (m.timestamp[i + 1] - m.timestamp[i])
                == +self.charge_power[i] * self.charge_efficiency[i]
                - self.discharge_power[i] * (1 + 1 - self.discharge_efficiency[i])
                - self.self_discharge[i] * self.energy[i]
                if i + 1 < len(m.i)
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_energy_ini", rule=lambda m: self.energy[0] == self.energy_ini
        )
        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i]
            == self.charge_power[i] - self.discharge_power[i],
        )
        self.add_constraint(
            "constraint_charging",
            self.model.i,
            rule=lambda m, i: self.charge_power[i]
            <= self.charging[i] * self.charge_power_max[i],
        )
        self.add_constraint(
            "constraint_discharging",
            self.model.i,
            rule=lambda m, i: self.discharge_power[i]
            <= (1 - self.charging[i]) * self.discharge_power_max[i],
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: (
                self.operational_cost[i]
                == +0.5
                * self.capacity_cost_per_cycle[i]
                * (self.charge_power[i] + self.discharge_power[i])
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                if i + 1 < len(m.i)
                else self.operational_cost[i] == 0
            ),
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        df[self.namespace("energy")] = [
            pyomo.value(self.energy[i]) for i in self.model.i
        ]
        df[self.namespace("charge_power_max")] = [
            pyomo.value(self.charge_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("discharge_power_max")] = [
            pyomo.value(self.discharge_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("energy_max")] = [
            pyomo.value(self.energy_max[i]) for i in self.model.i
        ]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
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
            self.namespace(
                "capacity_cost_per_cycle"
            ): 0.03,  # EUR / kWh / cycle  (600 EUR/kWh, 20000 cycles)
            self.namespace("capacity_cost_per_year"): 25.0,  # EUR / kWh / year
        }
        if cost_data is not None:
            for key in local_cost_data:
                if key in cost_data:
                    local_cost_data[key] = cost_data[key]

        energy_transfers = result[self.namespace("energy")].diff().abs().sum()
        energy_max = data[self.namespace("energy_max")].max()
        years = (result.index[-1] - result.index[0]).total_seconds() / (365 * 24 * 3600)

        cost = {}
        cost[self.namespace("capacity")] = max(
            float(
                energy_transfers
                * local_cost_data[self.namespace("capacity_cost_per_cycle")]
            ),
            float(
                energy_max
                * local_cost_data[self.namespace("capacity_cost_per_year")]
                * years
            ),
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
        if "energy" not in config:
            config["energy"] = {"plot": []}
        config["energy"]["plot"].append(
            {"key": self.namespace("energy"), "kwargs": {"color": color}}
        )

        self.add_plot_to(
            config, "cost", "operational_cost", color=color, drawstyle="steps-post"
        )
        return config


class BatteryModel(ComponentModel):
    """
    Models an electrical battery

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [self.namespace("energy")]

        self.add_parameter(
            "energy_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("energy_max")][i],
            doc="Maximum battery energy (Wh)",
        )
        self.add_parameter(
            "charge_power_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("charge_power_max")][i],
            doc="Maximum battery charge power (W)",
        )
        self.add_parameter(
            "discharge_power_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("discharge_power_max")][i],
            doc="Maximum battery discharge power (W)",
        )
        self.add_parameter(
            "self_discharge",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("self_discharge"), 0 * np.ones(len(data.index))
            )[i],
            doc=(
                "Battery self discharge, must be less than 1/dt for stability (W/J) or"
                " (1/s)"
            ),
        )
        self.add_parameter(
            "charge_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("charge_efficiency"), np.ones(len(data.index))
            )[i],
            doc="Battery charge efficiency (-)",
        )
        self.add_parameter(
            "discharge_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("discharge_efficiency"), np.ones(len(data.index))
            )[i],
            doc="Battery discharge efficiency (-)",
        )
        self.add_parameter(
            "capacity_cost_per_cycle",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("capacity_cost_per_cycle"), 0 * np.ones(len(data.index))
            )[i],
            doc=(
                "Cost of the battery divided by the capacity and the number of cycles"
                " (EUR / kWh / Cycle)"
            ),
        )
        self.add_parameter(
            "energy_ini",
            initialize=lambda m: min(
                self.energy_max[0], max(0, ini.get(self.namespace("energy"), 0))
            ),
            doc="Initial battery energy (Wh)",
        )
        self.add_parameter(
            "minimum_SOC_battery",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("minimum_SOC_battery"), 0 * np.ones(len(data.index))
            )[i],
            doc="Minimum SOC in the battery, (-)",
        )
        self.add_parameter(
            "maximum_SOC_battery",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("maximum_SOC_battery"), 1 * np.ones(len(data.index))
            )[i],
            doc="Maximum SOC in the battery, (-)",
        )
        self.add_parameter(
            "FCR_delta_energy",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("FCR_delta_energy"), 0 * np.ones(len(data.index))
            )[i],
            doc="Energy difference influenced by FCR service, (Wh)",
        )
        self.add_parameter(
            "average_power_FCR",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("average_power_FCR"), 0 * np.ones(len(data.index))
            )[i],
            doc="Energy difference influenced by FCR service, (-)",
        )
        self.add_parameter(
            "energy_N_FCR",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("energy_N (kWh)"), 0 * np.ones(len(data.index))
            )[i],
            doc="Negative energy during FCR service, (kWh)",
        )
        self.add_parameter(
            "energy_P_FCR",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("energy_P (kWh)"), 0 * np.ones(len(data.index))
            )[i],
            doc="Positive energy during FCR service, (kWh)",
        )
        self.add_parameter(
            "fcr_reserved",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("fcr_reserved"), 0 * np.ones(len(data.index))
            )[i],
            doc="Reserved FCR power in battery, (kW)",
        )
        self.add_variable(
            "energy",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (
                self.minimum_SOC_battery[i] * self.energy_max[i],
                self.maximum_SOC_battery[i] * self.energy_max[i],
            ),
            initialize=0,
            doc="Battery energy (Wh)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Battery power +: charging, -: discharging (W)",
        )
        self.add_variable(
            "charge_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.charge_power_max[i]),
            initialize=0,
        )
        self.add_variable(
            "discharge_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.discharge_power_max[i]),
            initialize=0,
        )
        self.add_variable(
            "charging",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_energy",
            self.model.i,
            rule=lambda m, i: (
                3.6e3
                * (self.energy[i + 1] - self.energy[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == (
                    -self.average_power_FCR[i]
                    + self.charge_power[i] * self.charge_efficiency[i]
                    - self.discharge_power[i] / self.discharge_efficiency[i]
                    - self.self_discharge[i] * self.energy[i] * 3.6e3
                )
                if i + 1 < len(m.i)
                else self.energy[i] == self.energy[i - 1]
            ),
        )
        self.add_constraint(
            "constraint_energy_ini", rule=lambda m: self.energy[0] == self.energy_ini
        )
        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i]
            == self.charge_power[i] - self.discharge_power[i],
        )
        self.add_constraint(
            "constraint_charging",
            self.model.i,
            rule=lambda m, i: self.charge_power[i]
            <= self.charging[i] * self.charge_power_max[i],
        )
        self.add_constraint(
            "constraint_discharging",
            self.model.i,
            rule=lambda m, i: self.discharge_power[i]
            <= (1 - self.charging[i]) * self.discharge_power_max[i],
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: (
                self.operational_cost[i]
                == +0.5
                * self.capacity_cost_per_cycle[i]
                * (self.charge_power[i] + self.discharge_power[i])
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                if i + 1 < len(m.i)
                else self.operational_cost[i] == 0
            ),
        )

    def get_results(self):
        df = pd.DataFrame()
        # df = super().get_results()

        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        df[self.namespace("energy")] = [
            pyomo.value(self.energy[i]) for i in self.model.i
        ]
        df[self.namespace("minimum_SOC_battery")] = [
            pyomo.value(self.minimum_SOC_battery[i]) for i in self.model.i
        ]
        df[self.namespace("maximum_SOC_battery")] = [
            pyomo.value(self.maximum_SOC_battery[i]) for i in self.model.i
        ]
        df[self.namespace("charge_power_max")] = [
            pyomo.value(self.charge_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("discharge_power_max")] = [
            pyomo.value(self.discharge_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("energy_max")] = [
            pyomo.value(self.energy_max[i]) for i in self.model.i
        ]
        df[self.namespace("energy_N_FCR")] = [
            pyomo.value(self.energy_N_FCR[i]) for i in self.model.i
        ]
        df[self.namespace("energy_P_FCR")] = [
            pyomo.value(self.energy_P_FCR[i]) for i in self.model.i
        ]
        df[self.namespace("fcr_reserved")] = [
            pyomo.value(self.fcr_reserved[i]) for i in self.model.i
        ]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
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
            self.namespace(
                "capacity_cost_per_cycle"
            ): 0.03,  # EUR / kWh / cycle  (600 EUR/kWh, 20000 cycles)
            self.namespace("capacity_cost_per_year"): 25.0,  # EUR / kWh / year
        }
        if cost_data is not None:
            for key in local_cost_data:
                if key in cost_data:
                    local_cost_data[key] = cost_data[key]

        energy_transfers = result[self.namespace("energy")].diff().abs().sum() / 3.6e6
        energy_max = data[self.namespace("energy_max")].max() / 3.6e6
        years = (result.index[-1] - result.index[0]).total_seconds() / (365 * 24 * 3600)

        cost = {}
        cost[self.namespace("capacity")] = max(
            float(
                energy_transfers
                * local_cost_data[self.namespace("capacity_cost_per_cycle")]
            ),
            float(
                energy_max
                * local_cost_data[self.namespace("capacity_cost_per_year")]
                * years
            ),
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
        if "energy" not in config:
            config["energy"] = {"plot": []}
        config["energy"]["plot"].append(
            {"key": self.namespace("energy"), "kwargs": {"color": color}}
        )
        return config


class FCRReserveBatteryModel(BatteryModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [self.namespace("energy")]
        self.add_parameter(
            "FCR_minimum_SOC_battery",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("FCR_minimum_SOC_battery"), 0 * np.ones(len(data.index))
            )[i],
            doc="FCR Minimum SOC in the battery, (-)",
        )
        self.add_parameter(
            "FCR_maximum_SOC_battery",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("FCR_maximum_SOC_battery"), 1 * np.ones(len(data.index))
            )[i],
            doc="FCR Maximum SOC in the battery, (-)",
        )
        self.add_parameter(
            "energy_soft_min",
            self.model.i,
            initialize=lambda m, i: self.FCR_minimum_SOC_battery[i]
            * self.energy_max[i],
            doc="Minimum soft battery energy (J)",
        )
        self.add_parameter(
            "energy_soft_max",
            self.model.i,
            initialize=lambda m, i: self.FCR_maximum_SOC_battery[i]
            * self.energy_max[i],
            doc="Maximum soft battery energy (J)",
        )
        self.add_parameter(
            "energy_constraint_violation_scale",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("energy_constraint_violation_scale"),
                100 * np.ones(len(data.index)),
            )[i],
            doc="Scale factor for the energy constraint violation (EUR / kWh)",
        )
        self.add_variable(
            "energy_min_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "energy_max_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "SOC",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, 1),
            initialize=0,
            doc="State of charges, (-)",
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
            "constraint_energy_min_slack",
            self.model.i,
            rule=lambda m, i: self.energy_min_slack[i]
            >= self.energy_soft_min[i] - self.energy[i],
        )
        self.add_constraint(
            "constraint_energy_max_slack",
            self.model.i,
            rule=lambda m, i: self.energy_max_slack[i]
            >= self.energy[i] - self.energy_soft_max[i],
        )
        self.add_constraint(
            "constraint_SOC",
            self.model.i,
            rule=lambda m, i: self.SOC[i] == self.energy[i] / self.energy_max[i],
        )
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == (self.energy_min_slack[i] + self.energy_max_slack[i])
            / 3.6e6
            * self.energy_constraint_violation_scale[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("FCR_minimum_SOC_battery")] = [
            pyomo.value(self.FCR_minimum_SOC_battery[i]) for i in self.model.i
        ]
        df[self.namespace("FCR_maximum_SOC_battery")] = [
            pyomo.value(self.FCR_maximum_SOC_battery[i]) for i in self.model.i
        ]
        df[self.namespace("SOC")] = [pyomo.value(self.SOC[i]) for i in self.model.i]
        df[self.namespace("constraint_violation")] = [
            pyomo.value(self.constraint_violation[i]) for i in self.model.i
        ]

        return df


class SoftSOCBatteryModel(BatteryModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "soft_minimum_SOC_battery",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("soft_minimum_SOC_battery"), 0 * np.ones(len(data.index))
            )[i],
            doc="Soft minimum SOC in the battery, (-)",
        )
        self.add_parameter(
            "soft_maximum_SOC_battery",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("soft_maximum_SOC_battery"), 1 * np.ones(len(data.index))
            )[i],
            doc="Soft maximum SOC in the battery, (-)",
        )
        self.add_variable(
            "SOC",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, 1),
            initialize=0,
            doc="State of charges, (-)",
        )
        self.add_parameter(
            "SOC_constant_violation_scale",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("SOC_constant_violation_scale"),
                1e9 * np.ones(len(data.index)),
            )[i],
            doc="Scale factor for the energy constraint violation (EUR / kWh)",
        )
        self.add_variable(
            "min_SOC_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "max_SOC_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "constraint_violation",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_SOC",
            self.model.i,
            rule=lambda m, i: self.SOC[i] == self.energy[i] / self.energy_max[i],
        )
        self.add_constraint(
            "constraint_min_SOC_slack",
            self.model.i,
            rule=lambda m, i: self.min_SOC_slack[i]
            >= self.soft_minimum_SOC_battery[i] - self.SOC[i],
        )
        self.add_constraint(
            "constraint_max_SOC_slack",
            self.model.i,
            rule=lambda m, i: self.max_SOC_slack[i]
            >= self.SOC[i] - self.soft_maximum_SOC_battery[i],
        )
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == (self.min_SOC_slack[i] + self.max_SOC_slack[i])
            / 3.6e6
            * self.SOC_constant_violation_scale[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("soft_minimum_SOC_battery")] = [
            pyomo.value(self.soft_minimum_SOC_battery[i]) for i in self.model.i
        ]
        df[self.namespace("soft_maximum_SOC_battery")] = [
            pyomo.value(self.soft_maximum_SOC_battery[i]) for i in self.model.i
        ]
        df[self.namespace("SOC")] = [pyomo.value(self.SOC[i]) for i in self.model.i]
        df[self.namespace("constraint_violation")] = [
            pyomo.value(self.constraint_violation[i]) for i in self.model.i
        ]

        return df


"""
class FCRControlModel(SoftEnergyBatteryModel):
    
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [self.namespace('energy')]
        
        self.add_parameter(
            'target_min_SOC_battery',
            self.model.i,
            initialize=lambda m, i: data.get(self.namespace('target_min_SOC_battery'), 0.3)[i],
            doc='Targeted minimum SOC during FCR simulation, (-)'
        )
        self.add_parameter(
            'target_max_SOC_battery',
            self.model.i,
            initialize=lambda m, i: data.get(self.namespace('target_max_SOC_battery'), 0.7)[i],
            doc='Targeted maximum SOC during FCR simulation, (-)'
        )
        self.add_parameter(
            'target_energy_min',
            self.model.i,
            initialize=lambda m, i: self.target_min_SOC_battery[i] * self.energy_max[i],
            doc='Minimum battery energy during FCR simulation, (J)'
        )
        self.add_parameter(
            'target_energy_max',
            self.model.i,
            initialize=lambda m, i: self.target_max_SOC_battery[i] * self.energy_max[i],
            doc='Maximum battery energy during FCR simulation, (J)'
        )
        # Variables
        self.add_variable(
            'FCR_power',
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc='Battery power influenced by FCR  +: charging, -: discharging (W)'
        )
        self.add_variable(
            'average_power_FCR',
            self.model.i,
            initialize=0,
            doc='Energy difference influenced by FCR service, (-)'
        )
        self.add_variable(
            'target_energy_min_slack',
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            'target_energy_max_slack',
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            'recharge_power',
            self.model.i,
            domain=pyomo.Reals,
            bounds = lambda m, i: (-(self.discharge_power_max[i]-self.fcr_reserved[i]), self.charge_power_max[
            i]-self.fcr_reserved[i]),
            doc='Recharge power, (W)'
        ) 
        
    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        
        self.model.del_component(self.model_namespace('constraint_power'))
        self.add_constraint(
            'constraint_FCR_power',
            self.model.i,
            rule=lambda m, i:
                self.FCR_power[i] == self.average_power_FCR[i] + self.recharge_power[i],  
        )
        self.add_constraint(
            'constraint_average_power_FCR',
            self.model.i,
            rule=lambda m, i:
                self.average_power_FCR[i] == self.FCR_delta_energy[i]*3.6e3 / (m.timestamp[i+1] - m.timestamp[i])  
                if i+1 < len(m.i) else 
                self.average_power_FCR[i] == 0 ,
                doc='Average power influenced by FCR service, (W)'
        )    
        self.add_constraint(
            'constraint_target_energy_min_slack',
            self.model.i,
            rule=lambda m, i: self.target_energy_min_slack[i+1] >= (self.target_energy_min[i] - self.energy[i]) 
                              if i+1 < len(m.i) else self.target_energy_min_slack[i] == 0,
        )
        self.add_constraint(
            'constraint_target_energy_max_slack',
            self.model.i,
            rule=lambda m, i: self.target_energy_max_slack[i+1] >= (self.energy[i] - self.target_energy_max[i])
                              if i+1 < len(m.i) else self.target_energy_min_slack[i] == 0,
        )
        self.add_constraint(
            'constraint_recharge_power',
            self.model.i,
            rule=lambda m, i: self.recharge_power[i] == (1e6 * self.target_energy_min_slack[i] -
                                                         1e6 * self.target_energy_max_slack[i])/ (m.timestamp[i+1] - 
                                                         m.timestamp[i])
                                                         if i+1 < len(m.i) else self.recharge_power[i] == 0,
            doc='Re-charge power to keep SoC in defined boundaries, (W)',
        )
        
        self.model.del_component(self.model_namespace('constraint_energy'))
        self.add_constraint(
            'constraint_energy',
            self.model.i,
            rule=lambda m, i:
                (self.energy[i+1] - self.energy[i])/ (m.timestamp[i+1] - m.timestamp[i]) == self.FCR_power[i]
                + self.charge_power[i]*self.charge_efficiency[i]
                - self.discharge_power[i]*(1+1-self.discharge_efficiency[i])
                - self.self_discharge[i]*self.energy[i]
                if i+1 < len(m.i) else self.energy[i] == self.energy[i-1],
            doc='Energy in battery during FCR service, (J)',
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace('energy')] = [pyomo.value(self.energy[i]) for i in self.model.i]
        df[self.namespace('target_energy_min_slack')] = [pyomo.value(self.target_energy_min_slack[i]) for i in 
        self.model.i]
        df[self.namespace('target_energy_max_slack')] = [pyomo.value(self.target_energy_max_slack[i]) for i in 
        self.model.i]
        df[self.namespace('average_power_FCR')] = [pyomo.value(self.average_power_FCR[i]) for i in self.model.i]
        df[self.namespace('recharge_power')] = [pyomo.value(self.recharge_power[i]) for i in self.model.i]
        df[self.namespace('target_energy_min')] = [pyomo.value(self.target_energy_min[i]) for i in self.model.i]
        df[self.namespace('target_energy_max')] = [pyomo.value(self.target_energy_max[i]) for i in self.model.i]

        return df
"""


class SoftConstrainedBatteryModel(BatteryModel):
    def __init__(
        self,
        *args,
        energy_max=10,
        charge_power_max=10 * 1e3,
        discharge_power_max=None,
        self_discharge=1e-6,
        charge_efficiency=0.90,
        discharge_efficiency=0.90,
        efficiency=None,
        capacity_cost_per_cycle=0,
        reference_objective=None,
        power_constraint_violation_multiplier=ConstraintViolationMultiplier.REQUEST,
        energy_constraint_violation_multiplier=ConstraintViolationMultiplier.PHYSICS,
        **kwargs,
    ):
        """
        Parameters
        ----------
        energy_max: number
            Maximum energy content (kWh)
        charge_power_max: number
            Maximum charge power (W)
        discharge_power_max: number
            Maximum discharge power (W)

        """
        super().__init__(*args, **kwargs)
        self._energy_max = energy_max
        self._charge_power_max = charge_power_max
        self._discharge_power_max = (
            charge_power_max if discharge_power_max is None else discharge_power_max
        )
        self._self_discharge = self_discharge
        self._charge_efficiency = (
            charge_efficiency if efficiency is None else efficiency
        )
        self._discharge_efficiency = (
            discharge_efficiency if efficiency is None else efficiency
        )
        self._capacity_cost_per_cycle = capacity_cost_per_cycle
        self._energy_constraint_violation_multiplier = (
            energy_constraint_violation_multiplier
        )
        self._power_constraint_violation_multiplier = (
            power_constraint_violation_multiplier
        )
        self.reference_objective = reference_objective

    def get_data(self, timestamps):
        data, par, ini = super().get_data(timestamps)

        if self.reference_objective is not None:
            reference_objective = self.reference_objective
        else:
            if hasattr(self.manager, "reference_objective"):
                reference_objective = self.manager.reference_objective
            else:
                reference_objective = 0.1

        energy_constraint_violation_scale = (
            reference_objective * self._energy_constraint_violation_multiplier
        )
        power_constraint_violation_scale = (
            reference_objective * self._power_constraint_violation_multiplier
        )

        data[self.namespace("energy_constraint_violation_scale")] = (
            energy_constraint_violation_scale
        )
        data[self.namespace("power_constraint_violation_scale")] = (
            power_constraint_violation_scale
        )
        data[self.namespace("energy_max")] = self._energy_max * 3.6e6
        data[self.namespace("charge_power_max")] = self._charge_power_max
        data[self.namespace("discharge_power_max")] = self._discharge_power_max
        data[self.namespace("self_discharge")] = self._self_discharge
        data[self.namespace("charge_efficiency")] = self._charge_efficiency
        data[self.namespace("discharge_efficiency")] = self._discharge_efficiency
        data[self.namespace("capacity_cost_per_cycle")] = self._capacity_cost_per_cycle
        data[self.namespace("energy_soft_min")] = 0
        data[self.namespace("energy_soft_max")] = self._energy_max * 3.6e6
        data[self.namespace("power_soft_min")] = -self._discharge_power_max
        data[self.namespace("power_soft_max")] = self._charge_power_max

        ini[self.namespace("energy")] = 0

        return data, par, ini

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self.add_parameter(
            "energy_soft_min",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("energy_soft_min")][i],
            doc="Minimum battery energy (J)",
        )
        self.add_parameter(
            "energy_soft_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("energy_soft_max")][i],
            doc="Maximum battery energy (J)",
        )
        self.add_parameter(
            "power_soft_min",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("power_soft_min")][i],
            doc="An external request to keep the power above a certain value (W)",
        )
        self.add_parameter(
            "power_soft_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("power_soft_max")][i],
            doc="An external request to keep the power below a certain value (W)",
        )
        self.add_parameter(
            "energy_constraint_violation_scale",
            self.model.i,
            initialize=lambda m, i: data[
                self.namespace("energy_constraint_violation_scale")
            ][i],
            doc="Scale factor for the energy constraint violation (EUR / kWh)",
        )
        self.add_parameter(
            "power_constraint_violation_scale",
            self.model.i,
            initialize=lambda m, i: data[
                self.namespace("power_constraint_violation_scale")
            ][i],
            doc="Scale factor for the power constraint violation (EUR / kW h)",
        )
        self.add_variable(
            "energy_min_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "energy_max_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "power_max_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "power_min_slack",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "power_constraint_violation",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )
        self.add_variable(
            "energy_constraint_violation",
            self.model.i,
            domain=pyomo.Reals,
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
            "constraint_energy_min_slack",
            self.model.i,
            rule=lambda m, i: self.energy_min_slack[i]
            >= self.energy_soft_min[i] - self.energy[i],
        )
        self.add_constraint(
            "constraint_energy_max_slack",
            self.model.i,
            rule=lambda m, i: self.energy_max_slack[i]
            >= self.energy[i] - self.energy_soft_max[i],
        )
        self.add_constraint(
            "constraint_power_min_slack",
            self.model.i,
            rule=lambda m, i: self.power_min_slack[i]
            >= self.power_soft_min[i] - self.power[i],
        )
        self.add_constraint(
            "constraint_power_max_slack",
            self.model.i,
            rule=lambda m, i: self.power_max_slack[i]
            >= self.power[i] - self.power_soft_max[i],
        )
        self.add_constraint(
            "constraint_energy_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.energy_constraint_violation[i]
            == (self.energy_min_slack[i] + self.energy_max_slack[i])
            / 3.6e6
            * self.energy_constraint_violation_scale[i],
            # if i > 0 else self.energy_constraint_violation[i] == 0
        )
        self.add_constraint(
            "constraint_power_constraint_violation",
            self.model.i,
            rule=lambda m, i: (
                self.power_constraint_violation[i]
                == (self.power_min_slack[i] + self.power_max_slack[i])
                / 1e3
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3600
                * self.power_constraint_violation_scale[i]
                if i + 1 < len(m.i)
                else self.power_constraint_violation[i] == 0
            ),
        )

        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == self.energy_constraint_violation[i] + self.power_constraint_violation[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("energy_soft_min")] = [
            pyomo.value(self.energy_soft_min[i]) for i in self.model.i
        ]
        df[self.namespace("energy_soft_max")] = [
            pyomo.value(self.energy_soft_max[i]) for i in self.model.i
        ]
        df[self.namespace("energy_constraint_violation_scale")] = [
            pyomo.value(self.energy_constraint_violation_scale[i]) for i in self.model.i
        ]
        df[self.namespace("power_constraint_violation_scale")] = [
            pyomo.value(self.power_constraint_violation_scale[i]) for i in self.model.i
        ]
        df[self.namespace("energy_constraint_violation")] = [
            pyomo.value(self.energy_constraint_violation[i]) for i in self.model.i
        ]
        df[self.namespace("power_constraint_violation")] = [
            pyomo.value(self.power_constraint_violation[i]) for i in self.model.i
        ]
        df[self.namespace("constraint_violation")] = [
            pyomo.value(self.constraint_violation[i]) for i in self.model.i
        ]

        return df


class InverterModel(ComponentModel):
    """
    Inverter efficiency (%)
    Inverter stand by consumption (W)
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self.add_parameter(
            "efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("inverter_efficiency") / 100,
                100 * np.ones(len(data.index) / 100),
            )[i],
            doc="Inverter efficiency, (%)",
        )
        self.add_parameter(
            "standby_consumption",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("standby_consumption"), 100 * np.ones(len(data.index))
            )[i],
            doc="Inverter standby consumption, (W)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Nonnegativereals,
            initialize=0,
            doc="Inverter consumption, (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        self.add_constraint(
            "constraint_consumption_cost",
            self.model.i,
            rule=lambda m, i: self.power[i] == self.standby_consumption[i],
        )


class WaterTowerModel(ComponentModel):
    """
    Basic model for water tower

    """

    def __init__(
        self,
        *args,
        radius=17.845,
        height_min=30,
        height_max=40,
        number_pumps=4,
        number_turbines=2,
        min_pump_flow=0.0278,
        max_pump_flow=0.3055,
        nominal_pump_power=155.1e3,
        nominal_pump_flow=0.287,
        max_pump_power=159.08e3,
        min_turbine_flow=0.246,
        max_turbine_flow=1.40,
        nominal_turbine_power=296.2e3,
        nominal_turbine_flow=1.40,
        max_turbine_power=296.2e3,
        eta_pump=0.801 * 0.959,
        eta_turbine=0.9,
        **kwargs,
    ):
        """
        Option 1: Q=2.78 m3/s and P=866 kWe
        Option 2: Q=2.00 m3/s and P=500 kWe
        Option 3: Q=0.246-1.4 m3/s and P=45-296.2 kWe
        radius: 17.845, 25.24, 30.91, 35.69, 39.90
        """
        super().__init__(*args, **kwargs)
        N_pumps = 4
        self.pump_index = range(N_pumps)
        self.turbine_index = range(number_turbines)
        pumps_flows = np.zeros(N_pumps)
        pumps_powers = np.zeros(N_pumps)
        turbines_flows = np.zeros(number_turbines)
        turbines_powers = np.zeros(number_turbines)

        min_pump_power = min_pump_flow * (nominal_pump_power / nominal_pump_flow)
        for i in range(N_pumps):
            pumps_flows[i] = min_pump_flow + (i + 1) * (max_pump_flow - min_pump_flow)
            pumps_powers[i] = min_pump_power + (i + 1) * (
                max_pump_power - min_pump_power
            )
        for i in range(number_turbines):
            turbines_flows[i] = (i + 1) * max_turbine_flow
            turbines_powers[i] = (i + 1) * max_turbine_power

        rho = 1e3
        gravity = 9.81

        # water tower geometry
        self.raduis = radius
        self.height_max = height_max
        self.height_min = height_min
        self.area = radius * radius * 3.14
        self.volume = self.area * (self.height_max - self.height_min)

        # pumps and turbines in water tower
        self.min_pump_flow = min_pump_flow
        self.max_pump_flow = max_pump_flow

        self.min_turbine_flow = min_turbine_flow
        self.max_turbine_flow = max_turbine_flow

        self.number_pumps = number_pumps
        self.number_turbines = number_turbines

        self.nominal_pump_flow = nominal_pump_flow
        self.nominal_pump_power = nominal_pump_power
        self.nominal_turbine_flow = nominal_turbine_flow
        self.nominal_turbine_power = nominal_turbine_power

        self.pump_flow_levels = pumps_flows
        self.turbine_flow_levels = turbines_flows

        self.pump_power_levels = pumps_powers
        self.turbine_power_levels = turbines_powers

        self.K_pump = rho * gravity * eta_pump
        self.eta_turbine = eta_turbine
        print("Pump and Turbines Characteristics")
        print(pumps_flows)
        print(pumps_powers)
        print(turbines_flows)
        print(turbines_powers)

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [self.namespace("height")]

        # Levels - flows and powers
        self.add_parameter(
            "pump_flow_levels_par",
            self.model.i,
            self.pump_index,
            initialize=lambda m, i, j: self.pump_flow_levels[j],
            domain=pyomo.NonNegativeReals,
            doc="Pump water flow levels, (m3/s)",
        )
        self.add_parameter(
            "turbine_flow_levels_par",
            self.model.i,
            self.turbine_index,
            initialize=lambda m, i, j: self.turbine_flow_levels[j],
            domain=pyomo.NonNegativeReals,
            doc="Turbine water flow levels, (m3/s)",
        )
        self.add_parameter(
            "pump_power_levels_par",
            self.model.i,
            self.pump_index,
            initialize=lambda m, i, j: self.pump_power_levels[j],
            domain=pyomo.NonNegativeReals,
            doc="Pump power levels, (W)",
        )
        self.add_parameter(
            "turbine_power_levels_par",
            self.model.i,
            self.turbine_index,
            initialize=lambda m, i, j: self.turbine_power_levels[j],
            domain=pyomo.NonNegativeReals,
            doc="Turbine power levels, (W)",
        )
        # FLOW max/min
        self.add_parameter(
            "pump_flow_max",
            self.model.i,
            initialize=lambda m, i: (self.number_pumps * self.max_pump_flow)
            * np.ones(len(data.index))[i],
            doc="Maximum the total pump power, (W)",
        )
        self.add_parameter(
            "pump_flow_min",
            self.model.i,
            initialize=lambda m, i: self.min_pump_flow * np.ones(len(data.index))[i],
            doc="Minimum the total pump power, (W)",
        )

        self.add_parameter(
            "turbine_flow_max",
            self.model.i,
            initialize=lambda m, i: (self.number_turbines * self.max_turbine_flow)
            * np.ones(len(data.index))[i],
            doc="Maximum the total turbine power, (W)",
        )
        self.add_parameter(
            "turbine_flow_min",
            self.model.i,
            initialize=lambda m, i: self.min_turbine_flow * np.ones(len(data.index))[i],
            doc="Minimum the total turbine power, (W)",
        )

        self.add_parameter(
            "height_ini",
            initialize=lambda m: ini.get(self.namespace("height")),
            doc="Initial height water, (m)",
        )
        """
        self.add_parameter(
            'start_up_cost',
            self.model.i,
            initialize=lambda m, i: data.get(self.namespace('start_up_cost'), np.zeros(len(data.index)))[i],
            doc='Time dependent start up cost (W)'
        )
        """
        """
        self.add_parameter(
            'pump_flow_binary_ini',
            initialize=lambda m: ini.get(self.namespace('pump_flow_binary'), 0),
            doc='Time dependent start up cost (W)'
        )
        """
        # variables
        """
        self.add_variable(
            'pump_flow_binary',
            self.model.i, self.pump_index,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc='Binary variables indicating pump flow level: [1], [2], [3] and [4]'
        )
        """
        """
        self.add_variable(
            'turbine_flow_binary',
            self.model.i, self.turbine_index,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc='Binary variables indicating turbine flow level: [1], [2], [3]'
        )
        """
        """
        self.add_variable(
            'pump_power_add_vars',
            self.model.i, self.pump_index,
            domain=pyomo.NonNegativeReals,
            initialize=0.,
            doc='Pump power levels, (W)'
        )  
        self.add_variable(
            'turbine_power_add_vars',
            self.model.i, self.turbine_index,
            domain=pyomo.NonNegativeReals,
            initialize=0.,
            doc='Turbine power levels, (W)'
        )  
        """
        self.add_variable(
            "pump_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Pump water flow, (m3/s)",
        )
        self.add_variable(
            "turbine_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Turbine water flow, (m3/s)",
        )
        self.add_variable(
            "pump_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "turbine_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
        )
        self.add_variable(
            "height",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (self.height_min, self.height_max),
            initialize=0,
            doc="Water height in water tower, (m)",
        )
        self.add_variable(
            "SOC",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, 1),
            initialize=0,
            doc="State of charges, (-)",
        )
        self.add_variable(
            "charging",
            self.model.i,
            initialize=0,
            domain=pyomo.Binary,
        )
        self.add_variable(
            "discharging",
            self.model.i,
            initialize=0,
            domain=pyomo.Binary,
        )
        """
        self.add_variable(
            'operational_cost_pump',
            self.model.i, self.pump_index,
            domain=pyomo.Reals,
        )
        self.add_variable(
            'operational_cost',
            self.model.i,
            domain=pyomo.Reals,
        )
        """

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        # P U M P S

        # modulating
        self.add_constraint(
            "constraint_pump_flow_max_modulating",
            self.model.i,
            rule=lambda m, i: self.pump_flow[i]
            <= self.charging[i] * self.pump_flow_max[i],
            doc="Pump power, (W)",
        )
        self.add_constraint(
            "constraint_pump_flow_min_modulating",
            self.model.i,
            rule=lambda m, i: self.pump_flow[i]
            >= self.charging[i] * self.pump_flow_min[i],
            doc="Pump power, (W)",
        )
        self.add_constraint(
            "constraint_pump_power_modulating",
            self.model.i,
            rule=lambda m, i: self.pump_power[i]
            == self.nominal_pump_power * (self.pump_flow[i] / self.nominal_pump_flow),
            doc="water modulating flow, [m3/s]",
        )

        # T U R B I N E S
        # discrete
        """
        self.add_constraint(
            'constraint_turbine_flow_binary_and_discharging',
            self.model.i,
            rule=lambda m, i: self.discharging[i] == sum(self.turbine_flow_binary[i,j] for j in self.turbine_index),
            doc = 'Constraint of turbine flow binary variable, can be one on the selected flow levels, [1,2,3]'
        )
        self.add_constraint(
            'constraint_turbine_flow_rate',
            self.model.i,
            rule=lambda m, i: self.turbine_flow[i] == sum(self.turbine_flow_binary[i,
            j] * self.turbine_flow_levels_par[i,j] for j in self.turbine_index),
            doc = 'water flow in pumps, [m3/s]'
        )  
        """
        # modulating
        self.add_constraint(
            "constraint_turbine_flow_max_modulating",
            self.model.i,
            rule=lambda m, i: self.turbine_flow[i]
            <= self.discharging[i] * self.turbine_flow_max[i],
            doc="Maximum turbine flow constraint",
        )
        self.add_constraint(
            "constraint_turbine_flow_min_modulating",
            self.model.i,
            rule=lambda m, i: self.turbine_flow[i]
            >= self.discharging[i] * self.turbine_flow_min[i],
            doc="Minimum turbine flow constraint",
        )

        # turbine power constraints

        # turbine power total
        """
        self.add_constraint(
            'constraint_turbine_power_tot',
            self.model.i,
            rule=lambda m, i: self.turbine_power[i] == sum(self.turbine_flow_binary[i,
            j] * self.turbine_power_levels_par[i,j] for j in self.turbine_index),
            doc = 'Total turbine power, (W)'
        )  
        """
        self.add_constraint(
            "constraint_turbine_power_modulating",
            self.model.i,
            rule=lambda m, i: self.turbine_power[i]
            == self.nominal_turbine_power
            * (self.turbine_flow[i] / self.nominal_turbine_flow),
            doc="Turbine modulating power",
        )

        # system constraints
        self.add_constraint(
            "water_height_ini", rule=lambda m: self.height[0] == self.height_ini
        )
        self.add_constraint(
            "constraint_height",
            self.model.i,
            rule=lambda m, i: (
                self.area
                * (self.height[i + 1] - self.height[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == +self.pump_flow[i] - self.turbine_flow[i]
                if i + 1 < len(m.i)
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_SOC",
            self.model.i,
            rule=lambda m, i: self.SOC[i]
            == self.area * (self.height[i] - self.height_min) / self.volume,
        )

        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i]
            == self.pump_power[i] - self.turbine_power[i],
        )

        self.add_constraint(
            "constraint_link_charging_discharging",
            self.model.i,
            rule=lambda m, i: self.charging[i] + self.discharging[i] <= 1,
            doc="charging and discharging constraint",
        )

        """
        self.add_constraint(
            'constraint_operational_cost_pump',
            self.model.i,self.pump_index,
            rule=lambda m, i,j:
                self.operational_cost_pump[i,j] >=
                (self.start_up_cost[i]*(self.pump_flow_binary[i,j] - self.pump_flow_binary[i-1,j]) if i-1 > 0 else
                 self.start_up_cost[i]*(self.pump_flow_binary[i,j] - self.pump_flow_binary_ini))
        )
        self.add_constraint(
            'constraint_operational_cost',
            self.model.i,
            rule=lambda m, i:
                self.operational_cost[i] >= sum(self.operational_cost_pump[i,j] for j in self.pump_index),
        )
        """

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("charging")] = [
            pyomo.value(self.charging[i]) for i in self.model.i
        ]
        df[self.namespace("discharging")] = [
            pyomo.value(self.discharging[i]) for i in self.model.i
        ]
        df[self.namespace("pump_flow")] = [
            pyomo.value(self.pump_flow[i]) for i in self.model.i
        ]
        df[self.namespace("turbine_flow")] = [
            pyomo.value(self.turbine_flow[i]) for i in self.model.i
        ]
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        df[self.namespace("pump_power")] = [
            pyomo.value(self.pump_power[i]) for i in self.model.i
        ]
        df[self.namespace("turbine_power")] = [
            pyomo.value(self.turbine_power[i]) for i in self.model.i
        ]
        df[self.namespace("height")] = [
            pyomo.value(self.height[i]) for i in self.model.i
        ]
        df[self.namespace("SOC")] = [pyomo.value(self.SOC[i]) for i in self.model.i]

        return df


class ChargeBoxModel(ComponentModel):
    """
    Model for charge box

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self._states += [self.namespace("energy")]

        self.add_parameter(
            "energy_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("energy_max")][i],
            doc="Maximum battery energy (J)",
        )
        self.add_parameter(
            "charge_power_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("charge_power_max")][i],
            doc="Maximum battery charge power (W)",
        )
        self.add_parameter(
            "discharge_power_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("discharge_power_max")][i],
            doc="Maximum battery discharge power (W)",
        )
        self.add_parameter(
            "charge_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("charge_efficiency"), np.ones(len(data.index))
            )[i],
            doc="Battery charge efficiency (-)",
        )
        self.add_parameter(
            "discharge_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("discharge_efficiency"), np.ones(len(data.index))
            )[i],
            doc="Battery discharge efficiency (-)",
        )
        self.add_parameter(
            "energy_ini",
            initialize=lambda m: min(
                self.energy_max[0], max(0, ini.get(self.namespace("energy"), 0))
            ),
            doc="Initial battery energy (J)",
        )
        self.add_parameter(
            "minimum_SOC_battery",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("minimum_SOC_battery"), 0 * np.ones(len(data.index))
            )[i],
            doc="Minimum SOC in the battery, (-)",
        )
        self.add_parameter(
            "maximum_SOC_battery",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("maximum_SOC_battery"), 1 * np.ones(len(data.index))
            )[i],
            doc="Maximum SOC in the battery, (-)",
        )
        self.add_variable(
            "energy",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (
                self.minimum_SOC_battery[i] * self.energy_max[i],
                self.maximum_SOC_battery[i] * self.energy_max[i],
            ),
            initialize=0,
            doc="Battery energy (J)",
        )
        self.add_variable(
            "charge_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.charge_power_max[i]),
            initialize=0,
        )
        self.add_variable(
            "discharge_power",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.discharge_power_max[i], 0),
            initialize=0,
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_energy",
            self.model.i,
            rule=lambda m, i: (
                (self.energy[i + 1] - self.energy[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == +self.charge_power[i] * self.charge_efficiency[i]
                + self.discharge_power[i] / self.discharge_efficiency[i]
                if i + 1 < len(m.i)
                else self.energy[i] == self.energy[i - 1]
            ),
        )
        self.add_constraint(
            "constraint_energy_ini", rule=lambda m: self.energy[0] == self.energy_ini
        )

    def get_results(self):
        df = pd.DataFrame()
        # df = super().get_results()

        df[self.namespace("energy")] = [
            pyomo.value(self.energy[i]) for i in self.model.i
        ]
        df[self.namespace("charge_power")] = [
            pyomo.value(self.charge_power[i]) for i in self.model.i
        ]
        df[self.namespace("discharge_power")] = [
            pyomo.value(self.discharge_power[i]) for i in self.model.i
        ]
        df[self.namespace("minimum_SOC_battery")] = [
            pyomo.value(self.minimum_SOC_battery[i]) for i in self.model.i
        ]
        df[self.namespace("maximum_SOC_battery")] = [
            pyomo.value(self.maximum_SOC_battery[i]) for i in self.model.i
        ]
        df[self.namespace("charge_power_max")] = [
            pyomo.value(self.charge_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("discharge_power_max")] = [
            pyomo.value(self.discharge_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("energy_max")] = [
            pyomo.value(self.energy_max[i]) for i in self.model.i
        ]

        return df


component_models = {
    "BatteryModel": BatteryModel,
    "SoftConstrainedBatteryModel": SoftConstrainedBatteryModel,
    "InverterModel": InverterModel,
    "ChargeBoxModel": ChargeBoxModel,
}
