import numpy as np
import pandas as pd
import pyomo.environ as pyomo
# from colorama import initialise

# from scipy import interpolate

from .heat_base import (
    ComponentModel,
    OnOffComponentModelBase,
)


class HeatPumpBaseModel(ComponentModel):
    """
    Heat pump base model for electrical and gas driven heat pumps
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "on_ini",
            initialize=lambda m: ini.get(self.namespace("on"), 0),
            doc="",
        )
        self.add_parameter(
            "COP",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("COP"), 3 * np.ones(len(data.index))
            )[i],
            doc="Time dependent heat pump COP (-)",
        )
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("heat_max")][i],
            doc="Time dependent maximum heat output (W)",
        )
        self.add_parameter(
            "heat_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("heat_min"), np.zeros(len(data.index))
            )[i],
            doc="Time dependent minimum heat output (W)",
        )
        self.add_parameter(
            "start_up_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("start_up_cost"), np.zeros(len(data.index))
            )[i],
            doc="Time dependent start up cost (W)",
        )
        self.add_parameter(
            "running_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("running_cost"), np.zeros(len(data.index))
            )[i],
            doc="Running cost (EUR)",
        )
        self.add_variable(
            "condenser_heat",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_max[i], 0),
            initialize=0.0,
            doc="Heat flow from the heat pump (W)",
        )
        self.add_variable(
            "evaporator_heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.heat_max[i]),
            initialize=0.0,
            doc="Heat flow from the low temperature source to the heat pump (W)",
        )
        self.add_variable(
            "on",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Binary variable indicating heat pump operation (1) or not (0)",
        )
        self.add_variable(
            "off",
            self.model.i,
            domain=pyomo.Binary,
            initialize=1,
            bounds=(0, 1),
            doc="Binary variable indicating heat pump operation (1) or not (0)",
        )
        self.add_variable(
            "operational_cost_start_up",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the heat pump start ups (EUR)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the heat pump operation (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_condenser_heat_max",
            self.model.i,
            rule=lambda m, i: -self.condenser_heat[i] <= self.heat_max[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_condenser_heat_min",
            self.model.i,
            rule=lambda m, i: -self.condenser_heat[i] >= self.heat_min[i] * self.on[i],
        )
        self.add_constraint(
            "constraint_evaporator_heat",
            self.model.i,
            rule=lambda m, i: self.evaporator_heat[i]
            == -self.condenser_heat[i] * (1.0 - 1.0 / self.COP[i]),
        )
        self.add_constraint(
            "constraint_off",
            self.model.i,
            rule=lambda m, i: self.off[i] == 1 - self.on[i],
        )
        self.add_constraint(
            "constraint_operational_cost_start_up",
            self.model.i,
            rule=lambda m, i: self.operational_cost_start_up[i]
            >= (
                self.start_up_cost[i] * (self.on[i] - self.on[i - 1])
                if i - 1 > 0
                else self.start_up_cost[i] * (self.on[i] - self.on_ini)
            ),
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == self.operational_cost_start_up[i]
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
        df[self.namespace("condenser_heat")] = [
            -pyomo.value(self.condenser_heat[i]) for i in self.model.i
        ]
        df[self.namespace("evaporator_heat")] = [
            pyomo.value(self.evaporator_heat[i]) for i in self.model.i
        ]
        df[self.namespace("heat_min")] = [
            pyomo.value(self.heat_min[i]) for i in self.model.i
        ]
        df[self.namespace("heat_max")] = [
            pyomo.value(self.heat_max[i]) for i in self.model.i
        ]
        df[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]
        return df

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)
        if "heat" not in config:
            config["heat"] = {"plot": []}
        config["heat"]["plot"].append(
            {
                "key": self.namespace("condenser_heat"),
                "kwargs": {"color": color, "drawstyle": "steps-post"},
            }
        )
        return config


class WIPBiDirectionalHeatPumpBaseModel(ComponentModel):
    """
    Bi-Directional that works both in heating and in cooling

    FIXME: During testing we were not able to get the model working, therefor, a 'WIP' state has been added
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "on_ini",
            initialize=lambda m: ini.get(self.namespace("on"), 0),
            doc="",
        )
        self.add_parameter(
            "capacity_heating",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("capacity_heating")][i],
            doc="Capacity in heating (W)",
        )
        self.add_parameter(
            "minimum_heating",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("minimum_heating"), np.zeros(len(data.index))
            )[i],
            doc="Minimum heating (W)",
        )
        self.add_parameter(
            "COP",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("COP"), 3 * np.ones(len(data.index))
            )[i],
            doc="Time dependent heat pump COP (-)",
        )
        self.add_parameter(
            "capacity_cooling",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("capacity_cooling")][i],
            doc="Capacity in cooling (W)",
        )
        self.add_parameter(
            "minimum_cooling",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("minimum_cooling"), np.zeros(len(data.index))
            )[i],
            doc="Minimum cooling (W)",
        )
        self.add_parameter(
            "EER",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("EER"), 3 * np.ones(len(data.index))
            )[i],
            doc="Time dependent heat pump EER (-)",
        )
        # Some parameters related to cost
        self.add_parameter(
            "start_up_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("start_up_cost"), np.zeros(len(data.index))
            )[i],
            doc="Time dependent start up cost (W)",
        )
        self.add_parameter(
            "running_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("running_cost"), np.zeros(len(data.index))
            )[i],
            doc="Running cost (EUR)",
        )
        # VARIABLES
        self.add_variable(
            "condenser_heat",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (
                -max(self.capacity_heating[i], self.capacity_cooling[i]),
                0,
            ),
            initialize=0,
            doc="Heat flow from the heat pump (W)",
        )
        self.add_variable(
            "condenser_heat_times_cooling",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (
                -max(self.capacity_heating[i], self.capacity_cooling[i]),
                0,
            ),
            initialize=0,
            doc="Additional var to calculate the evaporator heat - linearisation",
        )
        self.add_variable(
            "evaporator_heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (
                0,
                max(self.capacity_heating[i], self.capacity_cooling[i]),
            ),
            initialize=0,
            doc="Heat flow from the low temperature source to the heat pump (W)",
        )
        self.add_variable(
            "cooling",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Binary variable indicating heat pump in cooling (1) or heating (0)",
        )
        self.add_variable(
            "active_heating",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc=(
                "Binary variable indiciation if heat pump is turned on"
                " (=active) and in heating operation {0,1}"
            ),
        )
        self.add_variable(
            "active_cooling",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc=(
                "Binary variable indiciation if heat pump is turned on"
                " (=active) and in cooling operation {0,1}"
            ),
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0,
            bounds=lambda m, i: (
                -self.capacity_heating[i],
                self.capacity_cooling[i],
            ),
            doc=(
                "Heat exchanged - negative = heat to the building, positive ="
                " heat extracted from the building (W)"
            ),
        )
        self.add_variable(
            "heat_heating",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            initialize=0,
            bounds=lambda m, i: (-self.capacity_heating[i], 0),
            doc="Heat for heating (W)",
        )
        self.add_variable(
            "heat_cooling",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            bounds=lambda m, i: (0, self.capacity_cooling[i]),
            doc="Heat for cooling (W)",
        )
        # Status of the heat pump
        self.add_variable(
            "on",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Binary variable indicating heat pump operation (1) or not (0)",
        )
        self.add_variable(
            "off",
            self.model.i,
            domain=pyomo.Binary,
            initialize=1,
            bounds=(0, 1),
            doc="Binary variable indicating heat pump operation (1) or not (0)",
        )
        # Cost variables
        self.add_variable(
            "operational_cost_start_up",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the heat pump start ups (EUR)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the heat pump operation (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        # Product of 2 binaries (1 - cooling) x on - definition of three additional constraints
        self.add_constraint(
            "constraint_active_heating_1",
            self.model.i,
            rule=lambda m, i: self.active_heating[i] <= (1 - self.cooling[i]),
        )
        self.add_constraint(
            "constraint_active_heating_2",
            self.model.i,
            rule=lambda m, i: self.active_heating[i] <= self.on[i],
        )
        self.add_constraint(
            "constraint_active_heating_3",
            self.model.i,
            rule=lambda m, i: self.active_heating[i]
            >= (1 - self.cooling[i]) + self.on[i] - 1,
        )
        # Product of 2 binaries cooling x on - definition of three additional constraints
        self.add_constraint(
            "constraint_active_cooling_1",
            self.model.i,
            rule=lambda m, i: self.active_cooling[i] <= self.cooling[i],
        )
        self.add_constraint(
            "constraint_active_cooling_2",
            self.model.i,
            rule=lambda m, i: self.active_cooling[i] <= self.on[i],
        )
        self.add_constraint(
            "constraint_active_cooling_3",
            self.model.i,
            rule=lambda m, i: self.active_cooling[i]
            >= self.cooling[i] + self.on[i] - 1,
        )
        # Override the rule regarding the condenser heat
        self.add_constraint(
            "constraint_condenser_heat_ub",
            self.model.i,
            rule=lambda m, i: -self.condenser_heat[i]
            <= self.capacity_heating[i] * self.active_heating[i]
            + self.capacity_cooling[i] * self.active_cooling[i],
        )
        self.add_constraint(
            "constraint_condenser_heat_lb",
            self.model.i,
            rule=lambda m, i: -self.condenser_heat[i]
            >= self.minimum_heating[i] * self.active_heating[i]
            + self.minimum_cooling[i] * self.active_cooling[i],
        )
        # Evaporator heat = product of variables
        self.add_constraint(
            "constraint_condenser_heat_times_cooling_1",
            self.model.i,
            rule=lambda m, i: self.condenser_heat_times_cooling[i]
            >= self.condenser_heat[i],
        )
        self.add_constraint(
            "constraint_condenser_heat_times_cooling_2",
            self.model.i,
            rule=lambda m, i: self.condenser_heat_times_cooling[i]
            >= -self.capacity_cooling[i] * self.cooling[i],
        )
        self.add_constraint(
            "constraint_condenser_heat_times_cooling_3",
            self.model.i,
            rule=lambda m, i: self.condenser_heat_times_cooling[i]
            <= self.condenser_heat[i]
            - self.capacity_heating[i] * (self.cooling[i] - 1),
        )
        self.add_constraint(
            "constraint_evaporator_heat",
            self.model.i,
            rule=lambda m, i: self.evaporator_heat[i]
            == -self.condenser_heat[i] * (1.0 - 1.0 / self.COP[i])
            + ((1.0 - 1.0 / self.COP[i]) - (1.0 - 1.0 / self.EER[i]))
            * self.condenser_heat_times_cooling[i],
        )
        # Additional constraints to help with product of continious variable and binary
        self.add_constraint(
            "constraint_heat",
            self.model.i,
            rule=lambda m, i: self.heat[i]
            == self.condenser_heat[i] - 2 * self.condenser_heat_times_cooling[i],
            doc=(
                "Heat delivered to the building = negative, heat extracted"
                " from the building = positive"
            ),
        )
        # Calculate the heat_heating = heat * active_heating = continious x binary
        self.add_constraint(
            "constraint_heat_heating_1",
            self.model.i,
            rule=lambda m, i: self.heat_heating[i]
            >= -self.capacity_heating[i] * self.active_heating[i],
        )
        self.add_constraint(
            "constraint_heat_heating_2",
            self.model.i,
            rule=lambda m, i: self.heat_heating[i] >= self.heat[i],
        )
        self.add_constraint(
            "constraint_heat_heating_3",
            self.model.i,
            rule=lambda m, i: self.heat_heating[i]
            <= self.heat[i] - self.capacity_cooling[i] * (self.active_heating[i] - 1),
        )
        # Calculate the heat_cooling = heat * active_cooling = continious x binary
        self.add_constraint(
            "constraint_heat_cooling_1",
            self.model.i,
            rule=lambda m, i: self.heat_cooling[i]
            <= self.capacity_cooling[i] * self.active_cooling[i],
        )
        self.add_constraint(
            "constraint_heat_cooling_2",
            self.model.i,
            rule=lambda m, i: self.heat_cooling[i] <= self.heat[i],
        )
        self.add_constraint(
            "constraint_heat_cooling_3",
            self.model.i,
            rule=lambda m, i: self.heat_cooling[i]
            >= self.heat[i] + self.capacity_heating[i] * (self.active_cooling[i] - 1),
        )
        # Add an off status to the Heat pump
        self.add_constraint(
            "constraint_off",
            self.model.i,
            rule=lambda m, i: self.off[i] == 1 - self.on[i],
        )
        # Calculate the statup cost and operational cost
        self.add_constraint(
            "constraint_operational_cost_start_up",
            self.model.i,
            rule=lambda m, i: self.operational_cost_start_up[i]
            >= (
                self.start_up_cost[i] * (self.on[i] - self.on[i - 1])
                if i - 1 > 0
                else self.start_up_cost[i] * (self.on[i] - self.on_ini)
            ),
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == self.operational_cost_start_up[i]
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
        df[self.namespace("heat_heating")] = [
            -pyomo.value(self.heat_heating[i]) for i in self.model.i
        ]
        df[self.namespace("heat_cooling")] = [
            -pyomo.value(self.heat_cooling[i]) for i in self.model.i
        ]
        df[self.namespace("condenser_heat")] = [
            -pyomo.value(self.condenser_heat[i]) for i in self.model.i
        ]
        df[self.namespace("evaporator_heat")] = [
            -pyomo.value(self.evaporator_heat[i]) for i in self.model.i
        ]
        df[self.namespace("active_heating")] = [
            pyomo.value(self.active_heating[i]) for i in self.model.i
        ]
        df[self.namespace("active_cooling")] = [
            pyomo.value(self.active_cooling[i]) for i in self.model.i
        ]
        df[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]
        return df

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)
        if "heat" not in config:
            config["heat"] = {"plot": []}
        config["heat"]["plot"].append(
            {
                "key": self.namespace("heat"),
                "kwargs": {"color": color, "drawstyle": "steps-post"},
            }
        )
        return config


class ElectricityDrivenHeatPumpModel(HeatPumpBaseModel):
    """
    Models the thermal and electrical behavior of a heat pump supplying heat with a single time dependent COP
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Electrical energy flow to the heat pump (W)",
        )
        self.add_parameter(
            "base_power",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("base_power"), 0 * np.ones(len(self.model.i))
            )[i],
            doc=(
                "Electrical energy flow to the heat pump when it is not"
                " producing heat (W)"
            ),
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: (self.power[i] - self.base_power[i]) * self.COP[i]
            == -self.condenser_heat[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
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
        return config


class WIPBiDirectionalElectricityDrivenHeatPumpModel(WIPBiDirectionalHeatPumpBaseModel):
    """
    Models the thermal and electrical behavior of a heat pump supplying heat with a single time dependent COP and EER

    FIXME: During testing we were not able to get the model working, therefor, a 'WIP' state has been added
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Electrical energy flow to the heat pump (W)",
        )
        self.add_parameter(
            "base_power",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("base_power"), 0 * np.ones(len(self.model.i))
            )[i],
            doc="Electrical energy flow to the heat pump when idle (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i] - self.base_power[i]
            == (-self.condenser_heat[i]) - self.evaporator_heat[i],
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
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
        return config


class ElectricityDrivenHeatPumpMultiCOPModel(OnOffComponentModelBase):
    def __init__(self, *args, cop_index=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cop_index = cop_index

        self.cop_models = {
            index: ElectricityDrivenHeatPumpModel("{}.{}".format(self.name, index))
            for index in self.cop_index
        }

    def set_manager(self, manager):
        self.manager = manager
        for cop_model in self.cop_models.values():
            cop_model.set_manager(manager)

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        for index, cop_model in self.cop_models.items():
            cop_model.model = self.model
            cop_model.extend_model_variables(data, par, ini)

        self.add_variable(
            "condenser_heat",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            initialize=0.0,
            doc="Heat flow to the heat pump condenser (W)",
        )
        self.add_variable(
            "evaporator_heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Heat flow to the heat pump evaporator (W)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Electrical energy flow to the heat pump (W)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the heat pump operation (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        for cop_model in self.cop_models.values():
            cop_model.extend_model_constraints(data, par, ini)

        self.add_constraint(
            "constraint_condenser_heat",
            self.model.i,
            rule=lambda m, i: self.condenser_heat[i]
            == sum(
                self.cop_models[index].condenser_heat[i] for index in self.cop_index
            ),
        )
        self.add_constraint(
            "constraint_evaporator_heat",
            self.model.i,
            rule=lambda m, i: self.evaporator_heat[i]
            == sum(
                self.cop_models[index].evaporator_heat[i] for index in self.cop_index
            ),
        )
        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i]
            == sum(self.cop_models[index].power[i] for index in self.cop_index),
        )
        self.add_constraint(
            "constraint_on",
            self.model.i,
            self.cop_index,
            rule=lambda m, i, j: self.on[i] >= self.cop_models[j].on[i],
        )
        self.add_constraint(
            "constraint_off",
            self.model.i,
            rule=lambda m, i: self.on[i]
            <= sum(self.cop_models[j].on[i] for j in self.cop_index),
        )
        self.add_constraint(
            "constraint_not_simultaneous",
            self.model.i,
            rule=lambda m, i: sum(self.cop_models[j].on[i] for j in self.cop_index)
            <= 1,
            doc="Constraint prohibiting simultaneous operation at different COPS",
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            == sum(
                self.cop_models[index].operational_cost[i] for index in self.cop_index
            ),
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("condenser_heat")] = [
            -pyomo.value(self.condenser_heat[i]) for i in self.model.i
        ]
        df[self.namespace("evaporator_heat")] = [
            pyomo.value(self.evaporator_heat[i]) for i in self.model.i
        ]
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]

        for c in self.cop_models.values():
            df[c.namespace("condenser_heat")] = [
                -pyomo.value(c.condenser_heat[i]) for i in self.model.i
            ]
            df[c.namespace("evaporator_heat")] = [
                pyomo.value(c.evaporator_heat[i]) for i in self.model.i
            ]
            df[c.namespace("on")] = [pyomo.value(c.on[i]) for i in self.model.i]
            df[c.namespace("heat_min")] = [
                pyomo.value(c.heat_min[i]) for i in self.model.i
            ]
            df[c.namespace("heat_max")] = [
                pyomo.value(c.heat_max[i]) for i in self.model.i
            ]
        return df

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)
        if "heat" not in config:
            config["heat"] = {"plot": []}
        config["heat"]["plot"].append(
            {
                "key": self.namespace("condenser_heat"),
                "kwargs": {"color": color, "drawstyle": "steps-post"},
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


class GasDrivenHeatPumpModel(HeatPumpBaseModel):
    """Gas heat pump"""

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "gas_flow_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.gas_max".format(self.name), 10e6 * np.ones(len(data.index))
            )[i],
            doc="Maximum input gas flow to the heat pump, (m3/h)",
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
            "gas_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.gas_flow_max[i]),
            initialize=0.0,
            doc="The input gas flow to the heat pump, (m3/h)",
        )
        self.add_variable(
            "gas_heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (
                0,
                self.gas_flow_max[i] * self.calorific_value[i],
            ),
            doc="Gas heat to heat pump, (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_gas_flow",
            self.model.i,
            rule=lambda m, i: self.gas_flow[i] * self.calorific_value[i] * 1000
            == self.gas_heat[i],
            doc="Gas heat constraint",
        )
        self.add_constraint(
            "constraint_gas_heat",
            self.model.i,
            rule=lambda m, i: self.COP[i] * self.gas_heat[i] == -self.condenser_heat[i],
            doc="Efficiency heat pump constraint",
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("condenser_heat")] = [
            -pyomo.value(self.condenser_heat[i]) for i in self.model.i
        ]
        df[self.namespace("gas_flow")] = [
            pyomo.value(self.gas_flow[i]) for i in self.model.i
        ]
        df[self.namespace("gas_heat")] = [
            pyomo.value(self.gas_heat[i]) for i in self.model.i
        ]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]

        return df


# class PerformanceMapHeatPumpModel(ElectricityDrivenHeatPumpMultiCOPModel):
#     def extend_model_variables(self, data, par, ini):
#         for model_index, model in self.cop_models.items():
#             f_cop = interpolate.interp2d(
#                 par[self.namespace("performance_water_temperature")],
#                 par[self.namespace("performance_ambient_temperature")],
#                 par[self.namespace("performance_cop")],
#                 kind="linear",
#                 bounds_error=False,
#             )
#             f_capacity = interpolate.interp2d(
#                 par[self.namespace("performance_water_temperature")],
#                 par[self.namespace("performance_ambient_temperature")],
#                 par[self.namespace("performance_capacity")],
#                 kind="linear",
#                 bounds_error=False,
#             )
#
#             data[model.namespace("COP")] = np.array(
#                 [
#                     f_cop(
#                         data[
#                             self.namespace(
#                                 "{}.water_temperature".format(model_index)
#                             )
#                         ][i],
#                         data[self.namespace("ambient_temperature")][i],
#                     )
#                     for i in self.model.i
#                 ]
#             )
#             data[model.namespace("heat_max")] = np.array(
#                 [
#                     f_capacity(
#                         data[
#                             self.namespace(
#                                 "{}.water_temperature".format(model_index)
#                             )
#                         ][i],
#                         data[self.namespace("ambient_temperature")][i],
#                     )
#                     for i in self.model.i
#                 ]
#             )
#             data[model.namespace("heat_min")] = (
#                 0.3 * data[model.namespace("heat_max")]
#             )
#         super().extend_model_variables(data, par, ini)
#
#
# class HeatPumpSpaceHeatingDHWModel(PerformanceMapHeatPumpModel):
#     """
#     Models the thermal behavior of a heat pump supplying for:
#                         - space heating (sh) and
#                         - domestic hot water (dhw).
#     """
#
#     def __init__(self, *args, **kwargs):
#         kwargs["cop_index"] = ["sh", "dhw"]
#         super().__init__(*args, **kwargs)


# class MitsubishiEcodanXSpaceHeatingDHWHeatPumpModel(
#     HeatPumpSpaceHeatingDHWModel
# ):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         self.performance_ambient_temperature = np.arange(-15, 25, 5)
#         self.performance_water_temperature = np.arange(35, 65, 5)
#         self.performance_cop = np.array(
#             [
#                 [1.97, 1.71, 1.46, 1.22, 0, 0],
#                 [2.40, 2.08, 1.77, 1.53, 1.28, 0],
#                 [2.72, 2.35, 1.98, 1.76, 1.54, 0],
#                 [2.97, 2.72, 2.47, 2.13, 1.76, 1.38],
#                 [4.42, 3.87, 3.32, 2.84, 2.32, 1.77],
#                 [5.05, 4.34, 3.63, 3.19, 2.73, 2.23],
#                 [5.46, 4.68, 3.89, 3.43, 2.92, 2.38],
#                 [5.87, 5.03, 4.19, 3.68, 3.14, 2.56],
#             ]
#         )
#         self.performance_capacity = (
#             np.array(
#                 [
#                     [3.46, 3.32, 3.18, 3.02, 0, 0],
#                     [4.22, 4.11, 4.00, 3.81, 3.61, 0],
#                     [4.40, 4.40, 4.40, 4.40, 4.40, 0],
#                     [5.00, 5.00, 5.00, 5.00, 5.00, 5.00],
#                     [6.00, 6.00, 6.00, 6.00, 6.00, 6.00],
#                     [7.07, 7.07, 7.07, 7.07, 7.07, 7.07],
#                     [7.54, 7.54, 7.54, 7.54, 7.54, 7.54],
#                     [8.04, 8.04, 8.04, 8.04, 8.04, 8.04],
#                 ]
#             )
#             * 1000
#         )
#
#     def extend_model_variables(self, data, par, ini):
#         par[
#             self.namespace("performance_ambient_temperature")
#         ] = self.performance_ambient_temperature
#         par[
#             self.namespace("performance_water_temperature")
#         ] = self.performance_water_temperature
#         par[self.namespace("performance_cop")] = self.performance_cop
#         par[self.namespace("performance_capacity")] = self.performance_capacity
#         super().extend_model_variables(data, par, ini)
#
#
# class PerformanceMapWaterWaterHeatPumpModel(
#     ElectricityDrivenHeatPumpMultiCOPModel
# ):
#     def extend_model_variables(self, data, par, ini):
#         for model_index, model in self.cop_models.items():
#             f_cop = interpolate.interp2d(
#                 par[self.namespace("performance_water_temperature")],
#                 par[self.namespace("performance_fractional_load")],
#                 par[self.namespace("performance_cop")],
#                 kind="linear",
#                 bounds_error=False,
#             )
#
#             data[model.namespace("COP")] = np.array(
#                 [
#                     f_cop(
#                         data[
#                             self.namespace(
#                                 "{}.water_temperature".format(model_index)
#                             )
#                         ][i],
#                         data[self.namespace("ambient_temperature")][i],
#                     )
#                     for i in self.model.i
#                 ]
#             )
#         super().extend_model_variables(data, par, ini)


# class HeijmansWaterWaterHeatPump(PerformanceMapWaterWaterHeatPumpModel):
#     """
#     Water/water heat pumps
#     Heijmans in Devo example
#     """
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         self.performance_source_water_temperature = 13
#         self.performance_fractional_load = np.arange(0.00, 1.00, 0.25)
#         self.performance_water_temperature = np.arange(40, 55, 2.5)
#         self.performance_cop = np.array(
#             [
#                 [4.89, 4.64, 4.29, 4.07, 3.77, 3.60, 3.36],
#                 [5.75, 5.44, 5.01, 4.75, 4.39, 4.17, 3.89],
#                 [5.85, 5.54, 5.10, 4.83, 4.46, 4.22, 3.93],
#                 [5.62, 5.32, 4.90, 4.65, 4.30, 4.09, 3.81],
#             ]
#         )
#
#     def extend_model_variables(self, data, par, ini):
#         par[
#             self.namespace("performance_ambient_temperature")
#         ] = self.performance_source_water_temperature
#         par[
#             self.namespace("performance_fractional_load")
#         ] = self.performance_fractional_load
#         par[
#             self.namespace("performance_water_temperature")
#         ] = self.performance_water_temperature
#         par[self.namespace("performance_cop")] = self.performance_cop
#         super().extend_model_variables(data, par, ini)


class AirAirHeatPumpModel(OnOffComponentModelBase):
    """
    Air-Air heat pump model for space heating (SH), direct cooling/heating by a refrigerant
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sys_index = range(0, 3)

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "T_required_air",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("required_heat"), 20 * np.zeros(len(data.index))
            )[i],
            doc="Required temperature in building space, (C)",
        )
        self.add_parameter(
            "T_out",
            self.model.i,
            initialize=lambda m, i: data["building_1_1.outdoor_temperature"][i],
            doc="outdoor temperature, (C)",
        )
        self.add_parameter(
            "COP",
            self.model.i,
            initialize=lambda m, i: 3,  # 2 + 3 * (self.T_out[i]-(-15))/35, # COP = 2 for T_out = -15 C and COP=5 for T_out =20
            doc="Coefficient of performance of the air-air heat pump, (-)",
        )
        self.add_parameter(
            "heat_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("heat_max")][i],
            doc="Time dependent maximum heat output (W)",
        )
        self.add_parameter(
            "start_up_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("start_up_cost"), np.zeros(len(data.index))
            )[i],
            doc="Time dependent start up cost (W)",
        )
        self.add_parameter(
            "on_ini",
            initialize=lambda m: ini.get(self.namespace("on"), 0),
            doc="",
        )
        self.add_variable(
            "condenser_heat",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            bounds=lambda m, i: (-self.heat_max[i], 0),
            initialize=0,
            doc="Potential heat for space heating, (W)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Electrical energy flow to the heat pump (W)",
        )
        self.add_variable(
            "on",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Binary variable indicating heat pump operation (1) or not (0)",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the heat pump operation (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_power",
            self.model.i,
            self.sys_index,
            rule=lambda m, i, j: -self.power[i] * self.COP[i] == self.condenser_heat[i],
            doc="Heat pump power, (W)",
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i]
            >= (
                self.start_up_cost[i] * (self.on[i] - self.on[i - 1])
                if i - 1 > 0
                else self.start_up_cost[i] * (self.on[i] - self.on_ini)
            ),
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("condenser_heat")] = [
            pyomo.value(self.condenser_heat[i]) for i in self.model.i
        ]
        df[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]
        return df


class WaterBoreholeCooling(ComponentModel):
    # def __init__(self, *args, **kwargs):
    #     # super().__init__(*args, **kwargs)
    #     self.cw = 4180
    #     self.Tgw = 12 # ground water temperature

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "borehole_capacity",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("borehole_capacity"), 0 * np.zeros(len(data.index))
            )[i],
            doc="Borehole capacity, (W)",
        )
        self.add_parameter(
            "water_pump_capacity",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("water_pump_capacity"), 0 * np.zeros(len(data.index))
            )[i],
            doc="Water pump capacity, (W)",
        )
        self.add_parameter(
            "outdoor_temperature",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("outdoor_temperature")][i],
            doc="Outdoor temperature near the building (°C)",
        )
        self.add_parameter(
            "temperature_limit",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_limit"), 12 * np.ones(len(data.index))
            )[i],
            doc="Outdoor temperature near the building (°C)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.borehole_capacity[i]),
            initialize=0,
            doc="Heat power from the water, (W)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.water_pump_capacity[i]),
            initialize=0,
            doc="Power for electricity needs, (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_heat",
            self.model.i,
            rule=lambda m, i: (
                (
                    self.heat[i]
                    == self.power[i]
                    * self.borehole_capacity[i]
                    / self.water_pump_capacity[i]
                )
                if self.outdoor_temperature[i] < self.temperature_limit[i]
                else self.heat[i] == 0
            ),
            doc="Ratio between power and heat, (W)",
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        return df


class WaterBoreholeCooling(ComponentModel):
    # def __init__(self, *args, **kwargs):
    #     # super().__init__(*args, **kwargs)
    #     self.cw = 4180
    #     self.Tgw = 12 # ground water temperature

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "borehole_capacity",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("borehole_capacity"), 0 * np.zeros(len(data.index))
            )[i],
            doc="Borehole capacity, (W)",
        )
        self.add_parameter(
            "water_pump_capacity",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("water_pump_capacity"), 0 * np.zeros(len(data.index))
            )[i],
            doc="Water pump capacity, (W)",
        )
        self.add_parameter(
            "outdoor_temperature",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("outdoor_temperature")][i],
            doc="Outdoor temperature near the building (°C)",
        )
        self.add_parameter(
            "temperature_limit",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("temperature_limit"), 12 * np.ones(len(data.index))
            )[i],
            doc="Outdoor temperature near the building (°C)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.borehole_capacity[i]),
            initialize=0,
            doc="Heat power from the water, (W)",
        )
        self.add_variable(
            "power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.water_pump_capacity[i]),
            initialize=0,
            doc="Power for electricity needs, (W)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_heat",
            self.model.i,
            rule=lambda m, i: (
                (
                    self.heat[i]
                    == self.power[i]
                    * self.borehole_capacity[i]
                    / self.water_pump_capacity[i]
                )
                if self.outdoor_temperature[i] < self.temperature_limit[i]
                else self.heat[i] == 0
            ),
            doc="Ratio between power and heat, (W)",
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        return df


# def cop_interpolation(Tw, Ta):
#     Ta_m = np.arange(-15, 25, 5)
#     Tw_m = np.arange(35, 65, 5)
#
#     COP_m = np.array(
#         [
#             [1.97, 1.71, 1.46, 1.22, 0, 0],
#             [2.40, 2.08, 1.77, 1.53, 1.28, 0],
#             [2.72, 2.35, 1.98, 1.76, 1.54, 0],
#             [2.97, 2.72, 2.47, 2.13, 1.76, 1.38],
#             [4.42, 3.87, 3.32, 2.84, 2.32, 1.77],
#             [5.05, 4.34, 3.63, 3.19, 2.73, 2.23],
#             [5.46, 4.68, 3.89, 3.43, 2.92, 2.38],
#             [5.87, 5.03, 4.19, 3.68, 3.14, 2.56],
#         ]
#     )
#
#     TT_x, TT_y = np.meshgrid(Ta_m, Tw_m)
#     f = interpolate.interp2d(Tw_m, Ta_m, COP_m, kind="linear")
#     return f(Tw, Ta)


# def capacity_interpolation(Tw, Ta):
#     Ta_m = np.arange(-15, 25, 5)
#     Tw_m = np.arange(35, 65, 5)
#
#     Capacity_m = np.array(
#         [
#             [3.46, 3.32, 3.18, 3.02, 0, 0],
#             [4.22, 4.11, 4.00, 3.81, 3.61, 0],
#             [4.40, 4.40, 4.40, 4.40, 4.40, 0],
#             [5.00, 5.00, 5.00, 5.00, 5.00, 5.00],
#             [6.00, 6.00, 6.00, 6.00, 6.00, 6.00],
#             [7.07, 7.07, 7.07, 7.07, 7.07, 7.07],
#             [7.54, 7.54, 7.54, 7.54, 7.54, 7.54],
#             [8.04, 8.04, 8.04, 8.04, 8.04, 8.04],
#         ]
#     )
#
#     TT_x, TT_y = np.meshgrid(Ta_m, Tw_m)
#     f = interpolate.interp2d(Tw_m, Ta_m, Capacity_m, kind="linear")
#     return f(Tw, Ta)


component_models = {}
