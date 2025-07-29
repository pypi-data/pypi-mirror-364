import numpy as np
import pandas as pd
import pyomo.environ as pyomo

from .base import ComponentModel


# Water flow levels in distribution systems
class DistributionModel(ComponentModel):
    """
    Distribution system in DEVO project
    """

    def __init__(self, *args, flow_levels=range(10, 31, 5), **kwargs):
        super().__init__(*args, **kwargs)
        self.flow_index = range(0, len(flow_levels))
        self.flow_levels = flow_levels
        self.cp = 4186

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "flow_parameter",
            self.model.i,
            self.flow_index,
            initialize=lambda m, i, j: self.flow_levels[j],
            domain=pyomo.NonNegativeReals,
            doc="Water flow levels in distribution system, (kg/s)",
        )
        self.add_parameter(
            "temperature_supply_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.temperature_supply_max".format(self.name),
                80 * np.ones(len(data.index)),
            )[i],
            doc="Maximum supply temperature, (C)",
        )
        self.add_parameter(
            "temperature_supply_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.temperature_supply_min".format(self.name),
                40 * np.ones(len(data.index)),
            )[i],
            doc="Minium supply temperature, (C)",
        )
        self.add_parameter(
            "temperature_supply_par",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.temperature_supply_par".format(self.name),
                75 * np.ones(len(data.index)),
            )[i],
            doc="Supply temperature, (C)",
        )
        self.add_parameter(
            "temperature_V3_limit",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.temperature_LT_limit".format(self.name),
                55 * np.ones(len(data.index)),
            )[i],
            doc="Temperature limit of the lower-temperature part, (C)",
        )
        self.add_parameter(
            "temperature_return_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.temperature_return_min".format(self.name),
                10 * np.ones(len(data.index)),
            )[i],
            doc="Minium return temperature, (C)",
        )
        self.add_variable(
            "flow_binary",
            self.model.i,
            self.flow_index,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Binary variables indicating flow level: [1], [2], [3] and [4]",
        )
        self.add_variable(
            "flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            doc="Water flow in the distribution system, (kg/s)",
        )
        self.add_variable(
            "temperature_supply",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (
                self.temperature_supply_min[i],
                self.temperature_supply_max[i],
            ),
            initialize=0.0,
            doc="Supply temperature in the distribution system, (C)",
        )
        self.add_variable(
            "temperature_V3",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (
                self.temperature_return_min[i],
                self.temperature_V3_limit[i],
            ),
            initialize=0.0,
            doc="Temperature between the lower and higher part, (C)",
        )
        self.add_variable(
            "temperature_return",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            doc="Return temperature from the distribution system, (C)",
        )
        self.add_variable(
            "heat_HT_parameters",
            self.model.i,
            self.flow_index,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="High-temperature heats for various flow parameters, (W)",
        )
        self.add_variable(
            "heat_LT_parameters",
            self.model.i,
            self.flow_index,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Low-temperature heats for various flow parameters, (W)",
        )
        self.add_variable(
            "heat_HT",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="High-temperature part of the heat, (W)",
        )
        self.add_variable(
            "heat_LT",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Low-temperature part of the heat, (W)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="demand heat, (W)",
        )
        self.add_variable(
            "x_1",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Boolean varaible - CHP, (-)",
        )
        self.add_variable(
            "x_21",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Boolean varaible - GB_1, (-)",
        )
        self.add_variable(
            "x_22",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Boolean varaible - GB_2, (-)",
        )
        self.add_variable(
            "x_31",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Boolean varaible - HP_1, (-)",
        )
        self.add_variable(
            "x_32",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Boolean varaible - HP_2, (-)",
        )
        self.add_variable(
            "x_4",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc="Boolean varaible - buffer_HT, (-)",
        )

    def extend_model_constraints(self, data, par, ini):
        # Flow constraints
        self.add_constraint(
            "constraint_flow_binary",
            self.model.i,
            self.flow_index,
            rule=lambda m, i, j: sum(self.flow_binary[i, j] for j in self.flow_index)
            <= 1,
            doc=(
                "Constraint of flow binary variable, can be one on the"
                " selected flow levels, [1,2,3,4]"
            ),
        )
        self.add_constraint(
            "constraint_flow_rate",
            self.model.i,
            self.flow_index,
            rule=lambda m, i, j: self.flow[i]
            == sum(
                self.flow_binary[i, j] * self.flow_parameter[i, j]
                for j in self.flow_index
            ),
            doc="Mass flow in the distribution system, [kg/s]",
        )
        # Supply temperature constraint - fixed supply temperature or compensation curve
        self.add_constraint(
            "constraint_temperature_supply",
            self.model.i,
            rule=lambda m, i: self.temperature_supply[i]
            == self.temperature_supply_par[i],
            doc="Supply temperature constraint - Fixed or compensation curve",
        )
        # Heat_HT_constaints / product between binary variable (flow binary) and continuous variable (temperature difference)
        self.add_constraint(
            "constraint_heat_HT_1",
            self.model.i,
            self.flow_index,
            rule=lambda m, i, j: self.heat_HT_parameters[i, j]
            <= self.flow_binary[i, j]
            * self.flow_parameter[i, j]
            * self.cp
            * (self.temperature_supply_max[i] - self.temperature_return_min[i]),
            doc="1st constraint - heat is less than the maximum possible heat",
        )
        self.add_constraint(
            "constraint_heat_HT_2",
            self.model.i,
            self.flow_index,
            rule=lambda m, i, j: self.heat_HT_parameters[i, j]
            <= self.flow_parameter[i, j]
            * self.cp
            * (self.temperature_supply[i] - self.temperature_V3[i]),
            doc=(
                "2nd constraint - Heat is less then product between flow and"
                " temperature difference"
            ),
        )
        self.add_constraint(
            "constraint_heat_HT_3",
            self.model.i,
            self.flow_index,
            rule=lambda m, i, j: self.heat_HT_parameters[i, j]
            >= self.flow_parameter[i, j]
            * self.cp
            * (self.temperature_supply[i] - self.temperature_V3[i])
            - (1 - self.flow_binary[i, j])
            * self.flow_parameter[i, j]
            * self.cp
            * (self.temperature_supply_max[i] - self.temperature_return_min[i]),
            doc="3rd constraint - Additional complex constraint",
        )
        self.add_constraint(
            "constraint_heat_HT_4",
            self.model.i,
            self.flow_index,
            rule=lambda m, i, j: self.heat_HT_parameters[i, j] >= 0,
            doc="4th constraint - Heat should be higher than 0",
        )
        self.add_constraint(
            "constraint_heat_HT_tot",
            self.model.i,
            rule=lambda m, i: self.heat_HT[i]
            == sum(self.heat_HT_parameters[i, j] for j in self.flow_index),
            doc="High-temperature part of demand heat, (W)",
        )
        # Heat_LT_constaints
        self.add_constraint(
            "constraint_heat_LT_1",
            self.model.i,
            self.flow_index,
            rule=lambda m, i, j: self.heat_LT_parameters[i, j]
            <= self.flow_binary[i, j]
            * self.flow_parameter[i, j]
            * self.cp
            * (self.temperature_V3_limit[i] - self.temperature_return_min[i]),
            doc="1st constraint - heat is less than the maximum possible heat",
        )
        self.add_constraint(
            "constraint_heat_LT_2",
            self.model.i,
            self.flow_index,
            rule=lambda m, i, j: self.heat_LT_parameters[i, j]
            <= self.flow_parameter[i, j]
            * self.cp
            * (self.temperature_V3[i] - self.temperature_return[i]),
            doc=(
                "2nd constraint - Heat is less then product between flow and"
                " temperature difference"
            ),
        )
        self.add_constraint(
            "constraint_heat_LT_3",
            self.model.i,
            self.flow_index,
            rule=lambda m, i, j: self.heat_LT_parameters[i, j]
            >= self.flow_parameter[i, j]
            * self.cp
            * (self.temperature_V3[i] - self.temperature_return[i])
            - (1 - self.flow_binary[i, j])
            * self.flow_parameter[i, j]
            * self.cp
            * (self.temperature_V3_limit[i] - self.temperature_return_min[i]),
            doc="3rd constraint - Additional complex constraint",
        )
        self.add_constraint(
            "constraint_heat_LT_4",
            self.model.i,
            self.flow_index,
            rule=lambda m, i, j: self.heat_LT_parameters[i, j] >= 0,
            doc="4th constraint - Heat should be higher than 0",
        )
        self.add_constraint(
            "constraint_heat_LT_tot",
            self.model.i,
            rule=lambda m, i: self.heat_LT[i]
            == sum(self.heat_LT_parameters[i, j] for j in self.flow_index),
            doc="Low-temperature part of demand heat, (W)",
        )
        self.add_constraint(
            "constraint_heat_tot",
            self.model.i,
            rule=lambda m, i: self.heat[i] == self.heat_LT[i] + self.heat_HT[i],
            doc="Demand heat, (W)",
        )

        self.add_constraint(
            "constraint_boolean_variable",
            self.model.i,
            rule=lambda m, i: self.x_4[i] == self.x_1[i]
            or (not self.x_1[i] and (not self.x_21[i] or not self.x_22[i])),
            doc="System boolean variable constraint, (-)",
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("heat_LT")] = [
            pyomo.value(self.heat_LT[i]) for i in self.model.i
        ]
        df[self.namespace("heat_HT")] = [
            pyomo.value(self.heat_HT[i]) for i in self.model.i
        ]
        df[self.namespace("flow")] = [pyomo.value(self.flow[i]) for i in self.model.i]
        df[self.namespace("temperature_V3")] = [
            pyomo.value(self.temperature_V3[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_supply")] = [
            pyomo.value(self.temperature_supply[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_return")] = [
            pyomo.value(self.temperature_return[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_supply_max")] = [
            pyomo.value(self.temperature_supply_max[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_supply_min")] = [
            pyomo.value(self.temperature_supply_min[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_return_min")] = [
            pyomo.value(self.temperature_return_min[i]) for i in self.model.i
        ]

        return df


class DistributionVentilation(ComponentModel):
    """
    Distribution system in Merin building
    """

    def extend_model_variables(self, data, par, ini):
        self.add_parameter(
            "number_zones",
            self.model.i,
            domain=pyomo.Integers,
            initialize=lambda m, i: data[self.namespace("number_zones")][i],
            doc="Number of Zones, (-)",
        )
        for j in range(1, 7):
            self.add_variable(
                "temperature_Z{}".format(j),
                self.model.i,
                domain=pyomo.Reals,
                doc="Temperature from Z-ith zone, (C)",
            )
        self.add_variable(
            "temperature_Zbg",
            self.model.i,
            domain=pyomo.Reals,
            doc="Temperature from Zbg, (C)",
        )
        self.add_variable(
            "temperature_return",
            self.model.i,
            domain=pyomo.Reals,
            doc="Return air temperature from zones, (C)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_temperature_return",
            self.model.i,
            rule=lambda m, i: self.temperature_return[i]
            == (
                self.temperature_Z1[i]
                + self.temperature_Z2[i]
                + self.temperature_Z3[i]
                + self.temperature_Z4[i]
                + self.temperature_Z5[i]
                + self.temperature_Z6[i]
                + self.temperature_Zbg[i]
            )
            / self.number_zones[i],
            doc="Temperature return to central ventilation, (C)",
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("temperature_return")] = [
            pyomo.value(self.temperature_return[i]) for i in self.model.i
        ]

        return df


class DistrubutionWater(ComponentModel):
    """
    Distribution system in Merin building
    """

    def __init__(self, *args, number_zones=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.number_zones = number_zones
        self.set_zones = range(1, number_zones + 1)

    def extend_model_variables(self, data, par, ini):
        for z in self.set_zones:
            self.add_parameter(
                f"mass_flow_{z}",
                self.model.i,
                initialize=lambda m, i: data.get(
                    f"{self.name}.mass_flow_{z}", 1 * np.ones(len(data.index))
                )[i],
                doc="Water mass flow through the radiator, (kg/s)",
            )
        for z in self.set_zones:
            self.add_variable(
                f"temperature_{z}",
                self.model.i,
                domain=pyomo.Reals,
                doc="Temperature from Radiator, (C)",
            )
        for z in self.set_zones:
            self.add_variable(
                f"temperature_req_{z}",
                self.model.i,
                domain=pyomo.Reals,
                doc="Temperature requested from Radiator, (C)",
            )
            self.add_variable(
                f"b_{z}",
                self.model.i,
                domain=pyomo.Reals,
                doc=(
                    "Additional coefficient b_i for finding min C for max(A,B)"
                    " that C>=A, C>=B"
                ),
            )
        self.add_variable(
            "temperature_return",
            self.model.i,
            domain=pyomo.Reals,
            doc="Return air temperature from zones, (C)",
        )
        self.add_variable(
            "temperature_req_max",
            self.model.i,
            domain=pyomo.Reals,
            doc="Return max requested temperature of all zones, (C)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_temperature_return",
            self.model.i,
            rule=lambda m, i: self.temperature_return[i]
            == sum(
                [
                    getattr(self, f"temperature_{j}")[i]
                    * getattr(self, f"mass_flow_{j}")[i]
                    for j in self.set_zones
                ]
            )
            / sum([getattr(self, f"mass_flow_{z}")[i] for z in self.set_zones]),
            doc="Temperature return to central ventilation, (C)",
        )
        for zone in self.set_zones:
            self.add_constraint(
                f"constraint_temperature_req_{zone}",
                self.model.i,
                rule=lambda m, i: self.temperature_req_max[i]
                >= getattr(self, f"temperature_req_{zone}")[i],
            )
        #     self.add_constraint(
        #         f"constraint_b_{zone}",
        #         self.model.i,
        #         rule=lambda m,i:self.temperature_req_max[i]<=getattr(self,f'temperature_req_{zone}')[i]+1e18*(1-getattr(self,f'b_{zone}')[i]),
        #         doc=""
        #     )
        # self.add_constraint(
        #     f"constraint_sum_b_i=1",
        #     self.model.i,
        #     rule=lambda m,i:sum([getattr(self,f'b_{j}')[i] for j in self.set_zones])==1,
        #     doc=""
        # )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("temperature_return")] = [
            pyomo.value(self.temperature_return[i]) for i in self.model.i
        ]
        df[self.namespace("temperature_req_max")] = [
            pyomo.value(self.temperature_req_max[i]) for i in self.model.i
        ]
        return df


component_models = {}
