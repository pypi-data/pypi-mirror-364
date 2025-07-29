import numpy as np
import pyomo.environ as pyomo

from imby.simulations.custom_simulations.models.base import ComponentModel


# The current ChargePointModel combines the ChargePointModel and SoftConstrainedChargePoleModel
class ChargePointModel(ComponentModel):
    """
    Models an EV charge point.

    Notes
    -----

    ``data:``

    connected : (-)
        Connected indicator, 1 if an EV is connected at the beginning of the time step, 0 otherwise.
    charging_power_max : (W)
        Maximum connected EV battery charge power.
    charging_power_min : (W)
        Minimum connected EV battery charge power.
    discharging_power_max : (W)
        Maximum connected EV battery discharge power, 0 if it is not a vehicle to grid charge point.
    discharging_power_min : (W)
        Minimum connected EV battery discharge power, 0 if it is not a vehicle to grid charge point.
    energy_min : (Wh)
        Minimum battery energy of the EV connected to a charging station.
        Set to the initial battery energy at the arrival time and set to the required battery energy at the time of
        departure.
    energy_max : (Wh)
        Maximum battery energy of the EV connected to a charging station, 0 if no EV is connected.
    battery_self_discharge : (W/J) or (1/s)
        Connected EV battery self discharge, must be less than 1/dt for stability.
        The default value is artificially high to create smoother charging profiles.
    charging_efficiency : (-)
        Connected EV battery charging efficiency (-)
    discharging_efficiency : (-)
        Connected EV battery discharging efficiency (-)
    soft_minimum_SOC_car : (-)
        Soft minimum SOC in the car battery
    soft_maximum_SOC_car : (-)
        Soft maximum SOC in the car battery
    SOC_constant_violation_scale : (EUR)
        Scale factor for the energy constraint violation (EUR / kWh)
    battery_capacity_cost_per_cycle : (EUR / kWh / Cycle)
        Cost of the connected EV battery divided by the capacity and the number of cycles.

    ``parameters:``

    ``initial_conditions:``

    energy : (W)
        Initial connected EV battery energy.

    ``variables:``

    charging : (-)
        Charging state of the EV battery.
    discharging: (-)
        Discharging state of the EV battery.
    charging_power : (W)
        Power flow to the charge point.
    discharging_power : (W)
        Power flow from the charge point.
    power : (W)
        Power flow to the charge point (> 0: charging, < 0: discharging).
    energy : (Wh)
        Energy content of the EV battery.
    SOC : (-)
        State of charge of the EV battery.
    min_SOC_slack : (-):
        Difference between SOC and the minimum SOC that was set, outside the bounds
    max_SOC_slack : (-)
        Difference between SOC and the maximum SOC that was set, outside the bounds
    min_energy_slack : (-)
        Difference between energy content and the minimum that was set, outside the bounds
    constraint_violation : (EUR)
        violation contraints
    operational_cost : (EUR)
         Cost assigned to the charge point, related to ev battery degradation.

    ``results:``

    power : (W)
    energy : (W)
    operational_cost : (EUR)

    """

    def extend_model_variables(self, data, par, ini):
        self._states += [self.namespace("energy")]
        # P A R A M E T E R S
        self.add_parameter(
            "connected",
            self.model.i,
            domain=pyomo.Boolean,
            initialize=lambda m, i: data[self.namespace("connected")].iloc[i],
            doc="Information when car is connected (-)",
        )
        self.add_parameter(
            "charging_power_max",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("charging_power_max"),
                11e3 * np.ones(len(data.index)),
            ).iloc[i],
            doc="Maximum charging power (W)",
        )
        self.add_parameter(
            "charging_power_min",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("charging_power_min"), np.zeros(len(data.index))
            )[i],
            doc="Minimum charging power (W)",
        )
        self.add_parameter(
            "discharging_power_max",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("discharging_power_max"),
                np.zeros(len(data.index)),
            ).iloc[i],
            doc="Maximum discharging power (W)",
        )
        self.add_parameter(
            "discharging_power_min",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("discharging_power_min"),
                np.zeros(len(data.index)),
            )[i],
            doc="Minimum discharging power (W)",
        )
        self.add_parameter(
            "energy_min",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("energy_min"), np.zeros(len(data.index))
            ).iloc[i],
            doc="Defined minimum energy in time (Wh)",
        )
        self.add_parameter(
            "energy_max",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data[self.namespace("energy_max")].iloc[i],
            doc="Car battery capacity (Wh)",
        )
        self.add_parameter(
            "energy_ini",
            initialize=lambda m: ini.get(self.namespace("energy"), self.energy_min[0]),
            validate=lambda m, v: (0 <= v) and (v <= self.energy_max[0]),
            doc="Initial battery capacity (Wh)",
        )
        self.add_parameter(
            "battery_self_discharge",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("battery_self_discharge"),
                np.zeros(len(data.index)),
            )[i],
            doc="Self battery discharge (1/Wh)",
        )
        self.add_parameter(
            "charging_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("charging_efficiency"), np.ones(len(data.index))
            )[i],
            doc="EV charging efficiency (-)",
        )
        self.add_parameter(
            "discharging_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("discharging_efficiency"),
                np.ones(len(data.index)),
            )[i],
            doc="EV discharging efficiency (-)",
        )
        self.add_parameter(
            "soft_minimum_SOC_car",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("soft_minimum_SOC_car"),
                np.zeros(len(data.index)),
            )[i],
            doc="Soft minimum SOC in the car battery, (-)",
        )
        self.add_parameter(
            "soft_maximum_SOC_car",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("soft_maximum_SOC_car"),
                np.ones(len(data.index)),
            )[i],
            doc="Soft maximum SOC in the car battery, (-)",
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
        self.add_parameter(
            "battery_capacity_cost_per_cycle",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("battery_capacity_cost_per_cycle"),
                np.zeros(len(data.index)),
            )[i],
            doc="Cost of battery cycle (EUR)",
        )
        # V A R I A B L E S
        self.add_variable(
            "charging",
            self.model.i,
            domain=pyomo.Boolean,
            bounds=lambda m, i: (0, 1),
            initialize=0,
            doc="Charging state (-)",
        )
        self.add_variable(
            "discharging",
            self.model.i,
            domain=pyomo.Boolean,
            bounds=lambda m, i: (0, 1),
            initialize=0,
            doc="Discharging state (-)",
        )
        self.add_variable(
            "charging_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Charging Power (W)",
        )
        self.add_variable(
            "discharging_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Discharging Power (W)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Power (W)",
        )
        self.add_variable(
            "energy",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.energy_max[i]),
            initialize=0,
            doc="Energy in car battery (Wh)",
        )
        self.add_variable(
            "SOC",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, 1),
            initialize=0,
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
            "min_energy_slack",
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
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="The operational costs related to the charging station operation (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_charging",
            self.model.i,
            rule=lambda m, i: self.charging[i] <= self.connected[i],
        )
        self.add_constraint(
            "constraint_discharging",
            self.model.i,
            rule=lambda m, i: self.discharging[i] <= self.connected[i],
        )
        self.add_constraint(
            "constraint_charging_discharging",
            self.model.i,
            rule=lambda m, i: self.charging[i] + self.discharging[i] <= 1,
        )
        self.add_constraint(
            "constraint_charging_power_min",
            self.model.i,
            rule=lambda m, i: self.charging_power[i]
            >= self.charging[i] * self.charging_power_min[i],
        )
        self.add_constraint(
            "constraint_charging_power_max",
            self.model.i,
            rule=lambda m, i: self.charging_power[i]
            <= self.charging[i] * self.charging_power_max[i],
        )
        self.add_constraint(
            "constraint_discharging_power_min",
            self.model.i,
            rule=lambda m, i: self.discharging_power[i]
            >= self.discharging[i] * self.discharging_power_min[i],
        )
        self.add_constraint(
            "constraint_discharging_power_max",
            self.model.i,
            rule=lambda m, i: self.discharging_power[i]
            <= self.discharging[i] * self.discharging_power_max[i],
        )
        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i]
            == self.charging_power[i] - self.discharging_power[i],
        )
        self.add_constraint(
            "constraint_energy",
            self.model.i,
            rule=lambda m, i: (
                3.6e3
                * (self.energy[i + 1] - self.energy[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == self.connected[i]
                * (
                    self.charging_power[i] * self.charging_efficiency[i]
                    - self.discharging_power[i] / self.discharging_efficiency[i]
                    - self.battery_self_discharge[i] * self.energy[i]
                )
                + (1 - self.connected[i])
                * 3.6e3
                * (self.energy_min[i + 1] - self.energy[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                if i + 1 < len(m.i)
                else (self.energy[i] == self.energy[i - 1])
            ),
        )
        self.add_constraint(
            "constraint_energy_ini",
            rule=lambda m: self.energy[0] == self.energy_ini,
        )
        self.add_constraint(
            "constraint_SOC",
            self.model.i,
            rule=lambda m, i: (
                self.SOC[i] == self.energy[i] / self.energy_max[i]
                if self.energy_max[i] != 1
                else pyomo.constraint.skip
            ),
        )
        self.add_constraint(
            "constraint_min_SOC_slack",
            self.model.i,
            rule=lambda m, i: self.min_SOC_slack[i]
            >= self.soft_minimum_SOC_car[i] - self.SOC[i],
        )
        self.add_constraint(
            "constraint_max_SOC_slack",
            self.model.i,
            rule=lambda m, i: self.max_SOC_slack[i]
            >= self.SOC[i] - self.soft_maximum_SOC_car[i],
        )
        self.add_constraint(
            "constraint_energy_min",
            self.model.i,
            rule=lambda m, i: self.min_energy_slack[i]
            >= self.energy_min[i] - self.energy[i],
        )

        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == (
                self.min_SOC_slack[i] + self.max_SOC_slack[i] + self.min_energy_slack[i]
            )
            * self.SOC_constant_violation_scale[i],
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == self.battery_capacity_cost_per_cycle[i]
            * (self.charging_power[i] + self.discharging_power[i]),
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("connected")] = [
            pyomo.value(self.connected[i]) for i in self.model.i
        ]
        df[self.namespace("charging")] = [
            pyomo.value(self.charging[i]) for i in self.model.i
        ]
        df[self.namespace("discharging")] = [
            pyomo.value(self.discharging[i]) for i in self.model.i
        ]
        df[self.namespace("charging_power_max")] = [
            pyomo.value(self.charging_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        df[self.namespace("energy")] = [
            pyomo.value(self.energy[i]) for i in self.model.i
        ]
        df[self.namespace("energy_min")] = [
            pyomo.value(self.energy_min[i]) for i in self.model.i
        ]
        df[self.namespace("energy_max")] = [
            pyomo.value(self.energy_max[i]) for i in self.model.i
        ]

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

        if "energy_ev" not in config:
            config["energy_ev"] = {"plot": []}
        config["energy_ev"]["plot"].append(
            {"key": self.namespace("energy"), "kwargs": {"color": color}}
        )
        return config


class ChargePointModelDeprecated(ComponentModel):
    """
    Models an EV charge point.

    Notes
    -----

    ``data:``

    energy_min : (J)
        Minimum battery energy of the EV connected to a charging station.
        Set to the initial battery energy at the arrival time and set to the required battery energy at the time of
        departure.
    energy_max : (J)
        Maximum battery energy of the EV connected to a charging station, 0 if no EV is connected.
    connected : (-)
        Connected indicator, 1 if an EV is connected at the beginning of the time step, 0 otherwise.
    charge_power_max : (W)
        Maximum connected EV battery charge power.
    discharge_power_max : (W)
        Maximum connected EV battery discharge power, 0 if it is not a vehicle to grid charge point.
    battery_self_discharge : (W/J) or (1/s)
        Connected EV battery self discharge, must be less than 1/dt for stability.
        The default value is artificially high to create smoother charging profiles.
    battery_efficiency : (-)
        Connected EV battery round trip efficiency (-)
    battery_capacity_cost_per_cycle : (EUR / kWh / Cycle)
        Cost of the connected EV battery divided by the capacity and the number of cycles.

    ``parameters:``

    ``initial_conditions:``

    energy : (J)
        Initial connected EV battery energy.

    ``variables:``

    energy : (J)
        Energy content of the EV battery.
    power : (W)
        Power flow to the charge point (> 0: charging, < 0: discharging).
    charge_power : (W)
        Power flow to the charge point.
    discharge_power : (W)
        Power flow from the charge point.
    operational_cost : (EUR)
         Cost assigned to the charge point, related to ev battery degradation.

    ``results:``

    power : (W)
    energy : (J)
    operational_cost : (EUR)

    """

    def extend_model_variables(self, data, par, ini):
        #  self._states += ['energy']
        self._states += [self.namespace("energy")]

        self.add_parameter(
            "energy_ini_array",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("energy_ini_array"), np.zeros(len(data.index))
            )[i],
        )
        self.add_parameter(
            "energy_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("energy_min"), np.zeros(len(data.index))
            )[i],
        )
        self.add_parameter(
            "energy_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("energy_max")][i],
        )
        self.add_parameter(
            "connected",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("connected")][i],
        )
        self.add_parameter(
            "charge_power_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("charge_power_max")][i],
        )
        self.add_parameter(
            "discharge_power_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("discharge_power_max")][i],
        )
        self.add_parameter(
            "battery_self_discharge",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("battery_self_discharge"),
                1e-6 * np.ones(len(data.index)),
            )[i],
        )
        self.add_parameter(
            "charge_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("charge_efficiency"), np.ones(len(data.index))
            )[i],
            doc="EV charge efficiency (-)",
        )
        self.add_parameter(
            "discharge_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("discharge_efficiency"),
                np.ones(len(data.index)),
            )[i],
            doc="EV discharge efficiency (-)",
        )
        self.add_parameter(
            "battery_capacity_cost_per_cycle",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("battery_capacity_cost_per_cycle"),
                np.zeros(len(data.index)),
            )[i],
        )
        self.add_parameter(
            "energy_ini",
            initialize=lambda m: ini.get(self.namespace("energy"), 0),
        )

        self.add_variable(
            "energy",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (self.energy_min[i], self.energy_max[i]),
            initialize=0,
            doc="Connected EV battery energy (J)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Charge pole power +: charging, -: discharging (W)",
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
            "operational_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="The operational costs related to the charging station operation (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_energy",
            self.model.i,
            rule=lambda m, i: (
                (self.energy[i + 1] - self.energy[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == self.connected[i]
                * (
                    self.charge_power[i] * self.charge_efficiency[i]
                    - self.discharge_power[i] / self.discharge_efficiency[i]
                    - self.battery_self_discharge[i] * self.energy[i]
                )
                + (1 - self.connected[i])  # connected
                * (self.energy_min[i + 1] - self.energy[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                # + (self.connected[i+1] - self.connected[i]) *
                #    (self.energy_ini-self.energy[i] )
                # )  # not connected
                if i + 1 < len(m.i)
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_energy_ini",
            rule=lambda m: self.energy[0] == self.energy_ini,
        )
        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i]
            == self.connected[i] * (self.charge_power[i] - self.discharge_power[i]),  #
        )
        self.add_constraint(
            "constraint_charge_power_connected",
            self.model.i,
            rule=lambda m, i: (
                self.charge_power[i] <= self.charge_power_max[i] * self.connected[i]
                if i + 1 < len(self.model.i)
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_discharge_power_connected",
            self.model.i,
            rule=lambda m, i: (
                self.discharge_power[i]
                <= self.discharge_power_max[i] * self.connected[i]
                if i + 1 < len(self.model.i)
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == self.battery_capacity_cost_per_cycle[i]
            * (self.charge_power[i] + self.discharge_power[i]),
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        df[self.namespace("energy")] = [
            pyomo.value(self.energy[i]) for i in self.model.i
        ]
        df[self.namespace("energy_min")] = [
            pyomo.value(self.energy_min[i]) for i in self.model.i
        ]
        df[self.namespace("energy_max")] = [
            pyomo.value(self.energy_max[i]) for i in self.model.i
        ]
        df[self.namespace("connected")] = [
            pyomo.value(self.connected[i]) for i in self.model.i
        ]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]
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

        if "energy_ev" not in config:
            config["energy_ev"] = {"plot": []}
        config["energy_ev"]["plot"].append(
            {"key": self.namespace("energy"), "kwargs": {"color": color}}
        )
        return config


class SoftConstrainedChargePointModel(ChargePointModelDeprecated):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        self.add_parameter(
            "soft_minimum_SOC_car",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("soft_minimum_SOC_car"),
                0 * np.ones(len(data.index)),
            )[i],
            doc="Soft minimum SOC in the car battery, (-)",
        )
        self.add_parameter(
            "soft_maximum_SOC_car",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("soft_maximum_SOC_car"),
                1 * np.ones(len(data.index)),
            )[i],
            doc="Soft maximum SOC in the car battery, (-)",
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
            "SOC",
            self.model.i,
            initialize=lambda m, i: 0.5 * np.ones(len(data.index))[i],
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
            >= self.soft_minimum_SOC_car[i] - self.SOC[i],
        )
        self.add_constraint(
            "constraint_max_SOC_slack",
            self.model.i,
            rule=lambda m, i: self.max_SOC_slack[i]
            >= self.SOC[i] - self.soft_maximum_SOC_car[i],
        )
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == (self.min_SOC_slack[i] + self.max_SOC_slack[i])
            * self.SOC_constant_violation_scale[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("soft_minimum_SOC_car")] = [
            pyomo.value(self.soft_minimum_SOC_car[i]) for i in self.model.i
        ]
        df[self.namespace("soft_maximum_SOC_car")] = [
            pyomo.value(self.soft_maximum_SOC_car[i]) for i in self.model.i
        ]
        df[self.namespace("constraint_violation")] = [
            pyomo.value(self.constraint_violation[i]) for i in self.model.i
        ]
        df[self.namespace("SOC")] = [pyomo.value(self.SOC[i]) for i in self.model.i]
        df[self.namespace("energy")] = [
            pyomo.value(self.energy[i]) for i in self.model.i
        ]
        df[self.namespace("energy_max")] = [
            pyomo.value(self.energy_max[i]) for i in self.model.i
        ]

        return df


class EVChargingLimit(ComponentModel):
    def __init__(self, *args, ev_names=["EV_1_power", "EV_2_power"], **kwargs):
        super().__init__(*args, **kwargs)
        self.ev_names = ev_names

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "maximum_power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=lambda m, i: data[self.namespace("maximum_power")].iloc[i],
            doc="Maximum limit of power (W)",
        )
        for j in self.ev_names:
            self.add_variable(
                j,
                self.model.i,
                domain=pyomo.NonNegativeReals,
                initialize=0,
                doc="Charging power of every charger (W)",
            )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_ev_power_limit",
            self.model.i,
            rule=lambda m, i: sum(getattr(self, j)[i] for j in self.ev_names)
            <= self.maximum_power[i],
        )

class EVShuttleModel(ComponentModel):
    """
    Models an EV charge point but taking into consideration km driven.

    Notes
    -----

    ``data:``

    connected : (-)
        Connected indicator, 1 if an EV is connected at the beginning of the time step, 0 otherwise.
    charging_power_max : (W)
        Maximum connected EV battery charge power.
    charging_power_min : (W)
        Minimum connected EV battery charge power.
    discharging_power_max : (W)
        Maximum connected EV battery discharge power, 0 if it is not a vehicle to grid charge point.
    discharging_power_min : (W)
        Minimum connected EV battery discharge power, 0 if it is not a vehicle to grid charge point.
    energy_min : (Wh)
        Minimum battery energy of the EV connected to a charging station.
        Set to the initial battery energy at the arrival time and set to the required battery energy at the time of
        departure.
    energy_max : (Wh)
        Maximum battery energy of the EV connected to a charging station, 0 if no EV is connected.
    battery_self_discharge : (W/J) or (1/s)
        Connected EV battery self discharge, must be less than 1/dt for stability.
        The default value is artificially high to create smoother charging profiles.
    charging_efficiency : (-)
        Connected EV battery charging efficiency (-)
    discharging_efficiency : (-)
        Connected EV battery discharging efficiency (-)
    soft_minimum_SOC_car : (-)
        Soft minimum SOC in the car battery
    soft_maximum_SOC_car : (-)
        Soft maximum SOC in the car battery
    SOC_constant_violation_scale : (EUR)
        Scale factor for the energy constraint violation (EUR / kWh)
    battery_capacity_cost_per_cycle : (EUR / kWh / Cycle)
        Cost of the connected EV battery divided by the capacity and the number of cycles.

    ``parameters:``

    ``initial_conditions:``

    energy : (W)
        Initial connected EV battery energy.

    ``variables:``

    charging : (-)
        Charging state of the EV battery.
    discharging: (-)
        Discharging state of the EV battery.
    charging_power : (W)
        Power flow to the charge point.
    discharging_power : (W)
        Power flow from the charge point.
    power : (W)
        Power flow to the charge point (> 0: charging, < 0: discharging).
    energy : (Wh)
        Energy content of the EV battery.
    SOC : (-)
        State of charge of the EV battery.
    min_SOC_slack : (-):
        Difference between SOC and the minimum SOC that was set, outside the bounds
    max_SOC_slack : (-)
        Difference between SOC and the maximum SOC that was set, outside the bounds
    min_energy_slack : (-)
        Difference between energy content and the minimum that was set, outside the bounds
    constraint_violation : (EUR)
        violation contraints
    operational_cost : (EUR)
         Cost assigned to the charge point, related to ev battery degradation.

    ``results:``

    power : (W)
    energy : (W)
    operational_cost : (EUR)

    """

    def extend_model_variables(self, data, par, ini):
        self._states += [self.namespace("energy")]
        # P A R A M E T E R S
        self.add_parameter(
            "connected",
            self.model.i,
            domain=pyomo.Boolean,
            initialize=lambda m, i: data[self.namespace("connected")].iloc[i],
            doc="Information when car is connected (-)",
        )
        self.add_parameter(
            "charging_power_max",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("charging_power_max"),
                11e3 * np.ones(len(data.index)),
            ).iloc[i],
            doc="Maximum charging power (W)",
        )
        self.add_parameter(
            "charging_power_min",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("charging_power_min"), np.zeros(len(data.index))
            )[i],
            doc="Minimum charging power (W)",
        )
        self.add_parameter(
            "discharging_power_max",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("discharging_power_max"),
                np.zeros(len(data.index)),
            ).iloc[i],
            doc="Maximum discharging power (W)",
        )
        self.add_parameter(
            "discharging_power_min",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("discharging_power_min"),
                np.zeros(len(data.index)),
            )[i],
            doc="Minimum discharging power (W)",
        )
        self.add_parameter(
            "energy_min",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("energy_min"), np.zeros(len(data.index))
            ).iloc[i],
            doc="Defined minimum energy in time (Wh)",
        )
        self.add_parameter(
            "energy_max",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data[self.namespace("energy_max")].iloc[i],
            doc="Car battery capacity (Wh)",
        )
        self.add_parameter(
            "energy_ini",
            initialize=lambda m: ini.get(self.namespace("energy"), self.energy_min[0]),
            validate=lambda m, v: (0 <= v) and (v <= self.energy_max[0]),
            doc="Initial battery capacity (Wh)",
        )
        self.add_parameter(
            "energy_per_km",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data[self.namespace("energy_per_km")].iloc[i],
            doc="Energy spend by vehicle per km (Wh/km)",
        )
        self.add_parameter(
            "distance",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data[self.namespace("distance")].iloc[i],
            doc="Distance traveled by the vehicle (km)",
        )
        self.add_parameter(
            "battery_self_discharge",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("battery_self_discharge"),
                np.zeros(len(data.index)),
            )[i],
            doc="Self battery discharge (1/Wh)",
        )
        self.add_parameter(
            "charging_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("charging_efficiency"), np.ones(len(data.index))
            )[i],
            doc="EV charging efficiency (-)",
        )
        self.add_parameter(
            "discharging_efficiency",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("discharging_efficiency"),
                np.ones(len(data.index)),
            )[i],
            doc="EV discharging efficiency (-)",
        )
        self.add_parameter(
            "soft_minimum_SOC_car",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("soft_minimum_SOC_car"),
                np.zeros(len(data.index)),
            )[i],
            doc="Soft minimum SOC in the car battery, (-)",
        )
        self.add_parameter(
            "soft_maximum_SOC_car",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("soft_maximum_SOC_car"),
                np.ones(len(data.index)),
            )[i],
            doc="Soft maximum SOC in the car battery, (-)",
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
        self.add_parameter(
            "battery_capacity_cost_per_cycle",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i: data.get(
                self.namespace("battery_capacity_cost_per_cycle"),
                np.zeros(len(data.index)),
            )[i],
            doc="Cost of battery cycle (EUR)",
        )
        # V A R I A B L E S
        self.add_variable(
            "charging",
            self.model.i,
            domain=pyomo.Boolean,
            bounds=lambda m, i: (0, 1),
            initialize=0,
            doc="Charging state (-)",
        )
        self.add_variable(
            "discharging",
            self.model.i,
            domain=pyomo.Boolean,
            bounds=lambda m, i: (0, 1),
            initialize=0,
            doc="Discharging state (-)",
        )
        self.add_variable(
            "charging_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Charging Power (W)",
        )
        self.add_variable(
            "discharging_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="Discharging Power (W)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Power (W)",
        )
        self.add_variable(
            "energy",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.energy_max[i]),
            initialize=0,
            doc="Energy in car battery (Wh)",
        )
        self.add_variable(
            "SOC",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, 1),
            initialize=0,
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
            "min_energy_slack",
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
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="The operational costs related to the charging station operation (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_charging",
            self.model.i,
            rule=lambda m, i: self.charging[i] <= self.connected[i],
        )
        self.add_constraint(
            "constraint_discharging",
            self.model.i,
            rule=lambda m, i: self.discharging[i] <= self.connected[i],
        )
        self.add_constraint(
            "constraint_charging_discharging",
            self.model.i,
            rule=lambda m, i: self.charging[i] + self.discharging[i] <= 1,
        )
        self.add_constraint(
            "constraint_charging_power_min",
            self.model.i,
            rule=lambda m, i: self.charging_power[i]
            >= self.charging[i] * self.charging_power_min[i],
        )
        self.add_constraint(
            "constraint_charging_power_max",
            self.model.i,
            rule=lambda m, i: self.charging_power[i]
            <= self.charging[i] * self.charging_power_max[i],
        )
        self.add_constraint(
            "constraint_discharging_power_min",
            self.model.i,
            rule=lambda m, i: self.discharging_power[i]
            >= self.discharging[i] * self.discharging_power_min[i],
        )
        self.add_constraint(
            "constraint_discharging_power_max",
            self.model.i,
            rule=lambda m, i: self.discharging_power[i]
            <= self.discharging[i] * self.discharging_power_max[i],
        )
        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i]
            == self.charging_power[i] - self.discharging_power[i],
        )
        self.add_constraint(
            "constraint_energy",
            self.model.i,
            rule=lambda m, i: (
                3.6e3
                * (self.energy[i + 1] - self.energy[i])
                / (m.timestamp[i + 1] - m.timestamp[i])
                == self.connected[i]
                * (
                    self.charging_power[i] * self.charging_efficiency[i]
                    - self.discharging_power[i] / self.discharging_efficiency[i]
                    - self.battery_self_discharge[i] * self.energy[i]
                )
                - (1 - self.connected[i])
                * 3.6e3 * self.energy_per_km[i] * self.distance[i] / (m.timestamp[i + 1] - m.timestamp[i])
                if i + 1 < len(m.i)
                else (self.energy[i] == self.energy[i - 1])
            ),
        )
        self.add_constraint(
            "constraint_energy_ini",
            rule=lambda m: self.energy[0] == self.energy_ini,
        )
        self.add_constraint(
            "constraint_SOC",
            self.model.i,
            rule=lambda m, i: (
                self.SOC[i] == self.energy[i] / self.energy_max[i]
                if self.energy_max[i] != 1
                else pyomo.constraint.skip
            ),
        )
        self.add_constraint(
            "constraint_min_SOC_slack",
            self.model.i,
            rule=lambda m, i: self.min_SOC_slack[i]
            >= self.soft_minimum_SOC_car[i] - self.SOC[i],
        )
        self.add_constraint(
            "constraint_max_SOC_slack",
            self.model.i,
            rule=lambda m, i: self.max_SOC_slack[i]
            >= self.SOC[i] - self.soft_maximum_SOC_car[i],
        )
        self.add_constraint(
            "constraint_energy_min",
            self.model.i,
            rule=lambda m, i: self.min_energy_slack[i]
            >= self.energy_min[i] - self.energy[i],
        )

        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            == (
                self.min_SOC_slack[i] + self.max_SOC_slack[i] + self.min_energy_slack[i]
            )
            * self.SOC_constant_violation_scale[i],
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == self.battery_capacity_cost_per_cycle[i]
            * (self.charging_power[i] + self.discharging_power[i]),
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("connected")] = [
            pyomo.value(self.connected[i]) for i in self.model.i
        ]
        df[self.namespace("charging")] = [
            pyomo.value(self.charging[i]) for i in self.model.i
        ]
        df[self.namespace("discharging")] = [
            pyomo.value(self.discharging[i]) for i in self.model.i
        ]
        df[self.namespace("charging_power_max")] = [
            pyomo.value(self.charging_power_max[i]) for i in self.model.i
        ]
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        df[self.namespace("energy")] = [
            pyomo.value(self.energy[i]) for i in self.model.i
        ]
        df[self.namespace("energy_min")] = [
            pyomo.value(self.energy_min[i]) for i in self.model.i
        ]
        df[self.namespace("energy_max")] = [
            pyomo.value(self.energy_max[i]) for i in self.model.i
        ]
        df[self.namespace("SOC")] = [
            pyomo.value(self.SOC[i]) for i in self.model.i
        ]

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

        if "energy_ev" not in config:
            config["energy_ev"] = {"plot": []}
        config["energy_ev"]["plot"].append(
            {"key": self.namespace("energy"), "kwargs": {"color": color}}
        )
        return config


component_models = {
    "ChargePointModel": ChargePointModel,
    "ChargePointModelDeprecated": ChargePointModelDeprecated,
    "EVChargingLimit": EVChargingLimit,
}
