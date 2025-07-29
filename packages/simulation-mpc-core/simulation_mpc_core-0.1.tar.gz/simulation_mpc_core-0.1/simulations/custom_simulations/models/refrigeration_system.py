import CoolProp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyomo.environ as pyomo
from CoolProp.CoolProp import PropsSI
from CoolProp.Plots import PropertyPlot

from imby.simulations.custom_simulations.models.base import ComponentModel


class PhysicalProperties(ComponentModel):
    """

    Model for the calculating physical properties of the refrigerant

    """

    def __init__(
        self,
        *args,
        refrigerant="NH3",
        temperature_subcooling=7,
        temperature_superheating=4,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.refrigerant = refrigerant
        self.temperature_subcooling = temperature_subcooling
        self.temperature_superheating = temperature_subcooling

    def extend_model_variables(self, data, par, ini):
        # Evaporating and condensing temperature and pressure
        self.add_parameter(
            "compressor_efficiency",
            self.model.i,
            initialize=lambda m, i: data["{}.compressor_efficiency".format(self.name)][
                i
            ],
            doc="Compressor efficiency, (-)",
        )
        self.add_parameter(
            "evaporating_temperature",
            self.model.i,
            initialize=lambda m, i: (
                data["{}.requested_temperature".format(self.name)][i]
                - data["{}.delta_temperature_evaporating".format(self.name)][i]
                + 273.15
            ),
            doc=(
                "Evaporating temperature as function of requested temperature - Te, (C)"
            ),
        )
        self.add_parameter(
            "condensing_temperature",
            self.model.i,
            initialize=lambda m, i: (
                data["{}.outdoor_temperature".format(self.name)][i]
                + data["{}.delta_temperature_condensing".format(self.name)][i]
                + 273.15
            ),
            doc="Condensing temperature as function of outdoor temperature -Tc, (C)",
        )
        self.add_parameter(
            "evaporating_pressure",
            self.model.i,
            initialize=lambda m, i: PropsSI(
                "P",
                "T",
                self.evaporating_temperature[i],
                "Q",
                0.5,
                self.refrigerant,
            ),
            doc="Evaporating pressure as function of evaporating temperature - , (Pa)",
        )
        self.add_parameter(
            "condensing_pressure",
            self.model.i,
            initialize=lambda m, i: PropsSI(
                "P",
                "T",
                self.condensing_temperature[i],
                "Q",
                0.5,
                self.refrigerant,
            ),
            doc="Condensing pressure as function of condensing temperature, (Pa)",
        )
        self.add_parameter(
            "adiabatic_entrophy",
            self.model.i,
            initialize=lambda m, i: PropsSI(
                "S",
                "P",
                self.evaporating_pressure[i],
                "T",
                self.evaporating_temperature[i] + self.temperature_superheating,
                self.refrigerant,
            ),
            doc="Discharge enthalpy by adiabatic compression - s_2a, (J/kgK)",
        )
        # Enthalpies
        self.add_parameter(
            "enthalpy_suction",
            self.model.i,
            initialize=lambda m, i: PropsSI(
                "H",
                "P",
                self.evaporating_pressure[i],
                "T",
                self.evaporating_temperature[i] + self.temperature_superheating,
                self.refrigerant,
            ),
            doc="Suction refrigerant enthalpy - h_1, (J/kg)",
        )
        self.add_parameter(
            "enthalpy_discharge",
            self.model.i,
            initialize=lambda m, i: self.enthalpy_suction[1]
            + (
                PropsSI(
                    "H",
                    "P",
                    self.condensing_pressure[i],
                    "S",
                    self.adiabatic_entrophy[i],
                    self.refrigerant,
                )
                - self.enthalpy_suction[i]
            )
            / self.compressor_efficiency[i],
            doc="Discharging refrigerant enthalpy, (J/kg)",
        )
        self.add_parameter(
            "enthalpy_liquid",
            self.model.i,
            initialize=lambda m, i: PropsSI(
                "H",
                "P",
                self.condensing_pressure[i],
                "T",
                self.condensing_temperature[i] - self.temperature_subcooling,
                self.refrigerant,
            ),
            doc="Liquid refrigerant enthalpy - h_3, (J/kg)",
        )

    def ploting(self):
        # plot = PropertyPlot('HEOS::R134a', 'TS', unit_system='EUR', tp_limits='ACHP')
        # plot.calc_isolines(CoolProp.iQ, num=5)

        fig, ax1 = plt.subplots()
        # ax1 = CoolProp.Plots.PropsPlot('R134a','PH',show=True)
        # ax1 = PropertyPlot('HEOS::R134a', 'TS', unit_system='EUR', tp_limits='ACHP')
        ax1 = CoolProp.Plots.SimpleCycles.SimpleCycle(
            "R134a",
            Te=263.15,
            Tc=303.15,
            DTsh=5.0,
            DTsc=7.0,
            eta_a=0.70,
            skipPlot=False,
        )
        ax1 = CoolProp.Plots.SimpleCycles.SimpleCycle(
            "R134a",
            Te=263.15,
            Tc=303.15,
            DTsh=5.0,
            DTsc=7.0,
            eta_a=0.80,
            skipPlot=False,
        )
        ax1 = CoolProp.Plots.SimpleCycles.SimpleCycle(
            "R134a",
            Te=263.15,
            Tc=303.15,
            DTsh=5.0,
            DTsc=7.0,
            eta_a=0.90,
            skipPlot=False,
        )

        ax1 = PropertyPlot("HEOS::R134a", "TS", unit_system="EUR", tp_limits="ACHP")

    def get_results(self):
        df = super().get_results()
        df[self.namespace("condensing_temperature")] = [
            pyomo.value(self.condensing_temperature[i]) for i in self.model.i
        ]
        df[self.namespace("evaporating_temperature")] = [
            pyomo.value(self.evaporating_temperature[i]) for i in self.model.i
        ]

        return df


class RefrigerationModel(PhysicalProperties):
    """
    General refrigerarion modules
            with fixed requested temperature
                      outdoor temperature
    """

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        # Parameters
        self.add_parameter(
            "compressor_power_max",
            self.model.i,
            initialize=lambda m, i: data["{}.compressor_power_max".format(self.name)][
                i
            ],
            doc="Maximum power of compressor in the refrigeration system, (W)",
        )
        self.add_parameter(
            "refrigeration_capacity",
            self.model.i,
            initialize=lambda m, i: data["{}.refrigeration_capacity".format(self.name)][
                i
            ],
            doc="Refrigeration (maximum) capacity in the regrigeration system, (W)",
        )
        self.add_parameter(
            "start_up_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.start_up_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Start up cost of the refrigeration system, (EUR)",
        )
        self.add_parameter(
            "on_ini",
            initialize=lambda m: ini.get("{}.on".format(self.name), 0),
            doc="Initialisation of the refrigeration system, (-)",
        )
        # Variables
        self.add_variable(
            "COP",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Coefficient Of Performance - COP in heat pump case, (-)",
        )
        self.add_variable(
            "EER",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Energy Efficiency Ratio - EER in the refrigeration system case, (-)",
        )
        self.add_variable(
            "refrigerant_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Refrigerant flow throughout the refrigeration system, (kg/s)",
        )
        self.add_variable(
            "condensing_heat",
            self.model.i,
            domain=pyomo.NonPositiveReals,
            initialize=0.0,
            doc="Condensing heat of the refrigeration system, (W)",
        )
        self.add_variable(
            "compressor_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0.0, self.compressor_power_max[i]),
            initialize=0.0,
            doc="Compressor power in the refrigeration system, (W)",
        )
        self.add_variable(
            "evaporating_heat",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            bounds=lambda m, i: (0, self.refrigeration_capacity[i]),
            initialize=0.0,
            doc="Evaporating heat in the refrigeration system, (W)",
        )
        self.add_variable(
            "on",
            self.model.i,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc=(
                "Binary variable indicating the refrigeration sytem operation,"
                " [1] or [0]"
            ),
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the refrigeration system, (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_compressor_power_max",
            self.model.i,
            rule=lambda m, i: self.compressor_power[i]
            <= self.compressor_power_max[i] * self.on[i],
            doc="Maximum compressor power constraint",
        )
        self.add_constraint(
            "constraint_compressor_power_min",
            self.model.i,
            rule=lambda m, i: self.compressor_power[i]
            >= 0.0 * self.compressor_power_max[i] * self.on[i],
            doc="Minimum compressor power constraint",
        )
        self.add_constraint(
            "constraint_evaporating_heat",
            self.model.i,
            rule=lambda m, i: self.evaporating_heat[i]
            == self.refrigerant_flow[i]
            * (self.enthalpy_suction[i] - self.enthalpy_liquid[i]),
            doc="The refrigeration heat of the system, (W)",
        )
        self.add_constraint(
            "constraint_condensing_heat",
            self.model.i,
            rule=lambda m, i: -self.condensing_heat[i]
            == self.refrigerant_flow[i]
            * (self.enthalpy_discharge[i] - self.enthalpy_liquid[i]),
            doc="The condensing heat from the system, (W)",
        )
        self.add_constraint(
            "constraint_compressor_power",
            self.model.i,
            rule=lambda m, i: self.compressor_power[i]
            == self.refrigerant_flow[i]
            * (self.enthalpy_discharge[i] - self.enthalpy_suction[i]),
            doc="The compressor power in the system, (W)",
        )
        self.add_constraint(
            "constraint_COP",
            self.model.i,
            rule=lambda m, i: self.COP[i]
            == (self.enthalpy_discharge[i] - self.enthalpy_liquid[i])
            / (self.enthalpy_discharge[i] - self.enthalpy_suction[i]),
            doc="COP of the heat pump, (-)",
        )
        self.add_constraint(
            "constraint_EER",
            self.model.i,
            rule=lambda m, i: self.EER[i]
            == (self.enthalpy_suction[i] - self.enthalpy_liquid[i])
            / (self.enthalpy_discharge[i] - self.enthalpy_suction[i]),
            doc="EER of the refrigeration system, (-)",
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
        df[self.namespace("compressor_power")] = [
            pyomo.value(self.compressor_power[i]) for i in self.model.i
        ]
        df[self.namespace("evaporating_heat")] = [
            pyomo.value(self.evaporating_heat[i]) for i in self.model.i
        ]
        df[self.namespace("condensing_heat")] = [
            pyomo.value(self.condensing_heat[i]) for i in self.model.i
        ]
        df[self.namespace("COP")] = [pyomo.value(self.COP[i]) for i in self.model.i]
        df[self.namespace("EER")] = [pyomo.value(self.EER[i]) for i in self.model.i]
        df[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]

        return df


class RefrigerationModelMultiCOP(RefrigerationModel):
    def __init__(
        self,
        *args,
        refrigerant="NH3",
        compressor_efficiency=0.70,
        temperature_subcooling=5,
        temperature_superheating=5,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        N_eff = 10
        self.efficiency_index = range(N_eff + 1)
        # self.compressor_efficiency = [0.65,0.65,0.65,0.65,0.65,0.65,0.65,0.65,0.65,0.65,0.65]
        # self.compressor_efficiency = [0.78,0.78,0.78,0.78,0.78,0.78,0.78,0.78,0.78,0.78,0.78]
        self.compressor_efficiency = [
            0.75,
            0.75,
            0.75,
            0.75,
            0.75,
            0.75,
            0.75,
            0.75,
            0.75,
            0.75,
            0.75,
        ]
        # self.compressor_efficiency = [0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8,0.8]
        self.flow_par = np.arange(0, 1.01, 1 / N_eff)

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

        # parameters
        self.add_parameter(
            "enthalpy_discharge",
            self.model.i,
            self.efficiency_index,
            initialize=lambda m, i, j: self.enthalpy_suction[1]
            + (
                PropsSI(
                    "H",
                    "P",
                    self.condensing_pressure[i],
                    "S",
                    self.adiabatic_entrophy[i],
                    self.refrigerant,
                )
                - self.enthalpy_suction[i]
            )
            / self.compressor_efficiency[j],
            doc="Discharging refrigerant enthalpy, (J/kg)",
        )
        self.add_parameter(
            "refrigerant_flow_par",
            self.model.i,
            self.efficiency_index,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i, j: self.flow_par[j]
            * self.refrigeration_capacity[i]
            / (self.enthalpy_suction[i] - self.enthalpy_liquid[i]),
            doc="Refrigerant flow parameters throughout the system, (kg/s)",
        )
        self.add_parameter(
            "condensing_heat_par",
            self.model.i,
            self.efficiency_index,
            domain=pyomo.NonPositiveReals,
            initialize=lambda m, i, j: -self.refrigerant_flow_par[i, j]
            * (self.enthalpy_discharge[i, j] - self.enthalpy_liquid[i]),
            doc="Condensing heat parameters of the system, (W)",
        )
        self.add_parameter(
            "compressor_power_par",
            self.model.i,
            self.efficiency_index,
            domain=pyomo.NonNegativeReals,
            initialize=lambda m, i, j: self.refrigerant_flow_par[i, j]
            * (self.enthalpy_discharge[i, j] - self.enthalpy_suction[i]),
            doc="Total compressor power in the system, (W)",
        )
        self.add_parameter(
            "COP_par",
            self.model.i,
            self.efficiency_index,
            rule=lambda m, i, j: (
                self.enthalpy_discharge[i, j] - self.enthalpy_liquid[i]
            )
            / (self.enthalpy_discharge[i, j] - self.enthalpy_suction[i]),
            doc="COP parameters of the pump, (-)",
        )
        self.add_parameter(
            "EER_par",
            self.model.i,
            self.efficiency_index,
            rule=lambda m, i, j: (self.enthalpy_suction[i] - self.enthalpy_liquid[i])
            / (self.enthalpy_discharge[i, j] - self.enthalpy_suction[i]),
            doc="EER parameters of the system, (-)",
        )
        # variables
        self.add_variable(
            "on_par",
            self.model.i,
            self.efficiency_index,
            domain=pyomo.Binary,
            initialize=0,
            bounds=(0, 1),
            doc=(
                "Spectra of binary variables indicating the refrigeration"
                " sytem operation, [0,0,1,0,0]"
            ),
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        self.add_constraint(
            "constraint_refrigerant_flow",
            self.model.i,
            self.efficiency_index,
            rule=lambda m, i, j: self.refrigerant_flow[i]
            == sum(
                self.refrigerant_flow_par[i, j] * self.on_par[i, j]
                for j in self.efficiency_index
            ),
            doc="The refrigeration flow in the system, (kg/s)",
        )
        # self.model.del_component(self.namespace('constraint_condensing_heat'))
        self.add_constraint(
            "constraint_condensing_heat",
            self.model.i,
            self.efficiency_index,
            rule=lambda m, i, j: self.condensing_heat[i]
            == sum(
                self.condensing_heat_par[i, j] * self.on_par[i, j]
                for j in self.efficiency_index
            ),
            doc="The condensing heat computed by parameters spacrtum, (W)",
        )
        self.add_constraint(
            "constraint_compressor_power",
            self.model.i,
            self.efficiency_index,
            rule=lambda m, i, j: self.compressor_power[i]
            == sum(
                self.compressor_power_par[i, j] * self.on_par[i, j]
                for j in self.efficiency_index
            ),
            doc="The compressor power compured by parameters spectrum, (W)",
        )
        self.add_constraint(
            "constraint_COP",
            self.model.i,
            self.efficiency_index,
            rule=lambda m, i, j: self.COP[i]
            == sum(
                self.COP_par[i, j] * self.on_par[i, j] for j in self.efficiency_index
            ),
            doc="The COP calculation by existing parameters in the system, (-)",
        )
        self.add_constraint(
            "constraint_EER",
            self.model.i,
            self.efficiency_index,
            rule=lambda m, i, j: self.EER[i]
            == sum(
                self.EER_par[i, j] * self.on_par[i, j] for j in self.efficiency_index
            ),
            doc=(
                "The energy efficiency ratio calculation by existing"
                " parameters in the system, (-)"
            ),
        )
        self.add_constraint(
            "constraint_on_par",
            self.model.i,
            self.efficiency_index,
            rule=lambda m, i, j: sum(self.on_par[i, j] for j in self.efficiency_index)
            == 1,
            doc="On_par varaible definition, (-)",
        )
        self.add_constraint(
            "constraint_on_variable",
            self.model.i,
            self.efficiency_index,
            rule=lambda m, i, j: self.on[i]
            == sum(self.on_par[i, j] for j in range(1, len(self.efficiency_index))),
            doc=(
                "ON varaible is equal to sum of wokring ON_PAR (ON_PAR[0]- the"
                " system does not work), (-) "
            ),
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
            doc="Operational cost of refrigeration system or heat pump, (EUR)",
        )

    def get_results(self):
        df = pd.DataFrame()
        df = super().get_results()
        df[self.namespace("compressor_power")] = [
            pyomo.value(self.compressor_power[i]) for i in self.model.i
        ]
        df[self.namespace("evaporating_heat")] = [
            pyomo.value(self.evaporating_heat[i]) for i in self.model.i
        ]
        df[self.namespace("condensing_heat")] = [
            pyomo.value(self.condensing_heat[i]) for i in self.model.i
        ]
        df[self.namespace("COP")] = [pyomo.value(self.COP[i]) for i in self.model.i]
        df[self.namespace("EER")] = [pyomo.value(self.EER[i]) for i in self.model.i]
        df[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]

        return df


class TwoTemperaturePhysicalPropertiesModel(ComponentModel):
    """
    Two Temperature Refrigeration System - Module
    Inputs: evaporating temperatures : cooling -    - 6 C
                                       freeezing - - 32 C
            condenisng temperatute varies with outdoor temperature
    """

    def __init__(
        self,
        *args,
        refrigerant="NH3",
        evaporating_temperature_fix=[-6, -32],
        compressor_efficiency=0.75,
        temperature_subcooling=7,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        Ne = 2
        self.refrigerant = refrigerant
        self.evaporating_temperature_fix = evaporating_temperature_fix
        self.compressor_efficiency = compressor_efficiency
        self.evaporating_index = range(Ne)
        self.temperature_subcooling = 7

    def extend_model_variables(self, data, par, ini):
        # Evaporating and condensing temperature and pressure
        self.add_parameter(
            "evaporating_temperature",
            self.model.i,
            self.evaporating_index,
            initialize=lambda m, i, j: 273.15 + self.evaporating_temperature_fix[j],
            doc="Evaporating temperatures in the system - Te, (K)",
        )
        self.add_parameter(
            "evaporating_temperature_1",
            self.model.i,
            initialize=lambda m, i: 273.15 + self.evaporating_temperature_fix[0],
            doc="Evaporating temperatures in the system - Te, (K)",
        )
        self.add_parameter(
            "evaporating_temperature_2",
            self.model.i,
            initialize=lambda m, i: 273.15 + self.evaporating_temperature_fix[1],
            doc="Evaporating temperatures in the system - Te, (K)",
        )
        self.add_parameter(
            "condensing_temperature",
            self.model.i,
            initialize=lambda m, i: (30 + 7 + 273.15),
            doc="Condensing temperature as function of outdoor temperature -Tc, (C)",
        )
        self.add_parameter(
            "evaporating_pressure",
            self.model.i,
            self.evaporating_index,
            initialize=lambda m, i, j: PropsSI(
                "P",
                "T",
                self.evaporating_temperature[i, j],
                "Q",
                0.5,
                self.refrigerant,
            ),
            doc="Evaporating pressures in the system, (Pa)",
        )
        self.add_parameter(
            "condensing_pressure",
            self.model.i,
            initialize=lambda m, i: PropsSI(
                "P",
                "T",
                self.condensing_temperature[i],
                "Q",
                0.5,
                self.refrigerant,
            ),
            doc="Condensing pressure as function of outdoor temperature, (Pa)",
        )
        # Parameters on evaporating temperatures
        self.add_parameter(
            "vapour_evaporator_out",
            self.model.i,
            self.evaporating_index,
            initialize=lambda m, i, j: 0.9,
            doc="Vapour states from evaporators, (-)",
        )
        self.add_parameter(
            "evaporating_enthalpy_out",
            self.model.i,
            self.evaporating_index,
            initialize=lambda m, i, j: PropsSI(
                "H",
                "P",
                self.evaporating_pressure[i, j],
                "Q",
                self.vapour_evaporator_out[i, j],
                self.refrigerant,
            ),
            doc="Outlet enthalpies from evaporators, (-)",
        )
        self.add_parameter(
            "evaporating_enthalpy_liquid",
            self.model.i,
            self.evaporating_index,
            initialize=lambda m, i, j: PropsSI(
                "H",
                "T",
                self.evaporating_temperature[i, j],
                "Q",
                0,
                self.refrigerant,
            ),
            doc="Enthalpy of supersaturated liquid on evaporating temperatures, (J/kg)",
        )
        self.add_parameter(
            "evaporating_enthalpy_vapour",
            self.model.i,
            self.evaporating_index,
            initialize=lambda m, i, j: PropsSI(
                "H",
                "T",
                self.evaporating_temperature[i, j],
                "Q",
                1,
                self.refrigerant,
            ),
            doc=(
                "Enthalpies of supersaturated liquids on evaporating"
                " temperatures, (J/kg)"
            ),
        )
        self.add_parameter(
            "evaporating_density_vapour",
            self.model.i,
            self.evaporating_index,
            initialize=lambda m, i, j: PropsSI(
                "D",
                "T",
                self.evaporating_temperature[i, j],
                "Q",
                1,
                self.refrigerant,
            ),
            doc="Densities of vapour on evaporating temperatures, (kg/m3)",
        )
        self.add_parameter(
            "evaporating_entrophy_vapour",
            self.model.i,
            self.evaporating_index,
            initialize=lambda m, i, j: PropsSI(
                "S",
                "T",
                self.evaporating_temperature[i, j],
                "Q",
                1,
                self.refrigerant,
            ),
            doc="Entropies of vapour on evaporating temperatures, (J/kg)",
        )

        # Characteristic Enthalpies in two-temperature systems
        self.add_parameter(
            "enthalpy_1",
            self.model.i,
            initialize=lambda m, i: self.evaporating_enthalpy_vapour[i, 1],
            doc="Enthalpy in the point 1, (J/kg)",
        )
        self.add_parameter(
            "enthalpy_2",
            self.model.i,
            initialize=lambda m, i: self.enthalpy_1[i]
            + (
                PropsSI(
                    "H",
                    "P",
                    self.evaporating_pressure[i, 0],
                    "S",
                    self.evaporating_entrophy_vapour[i, 1],
                    self.refrigerant,
                )
                - self.enthalpy_1[i]
            )
            / self.compressor_efficiency,
            doc="Enthalpy in the point 2, (J/kg)",
        )
        self.add_parameter(
            "enthalpy_3",
            self.model.i,
            initialize=lambda m, i: self.evaporating_enthalpy_vapour[i, 0],
            doc="Enthalpy in the point 3, (J/kg)",
        )
        self.add_parameter(
            "enthalpy_4",
            self.model.i,
            initialize=lambda m, i: (self.enthalpy_2[i] + self.enthalpy_3[i]) / 2,
            doc="Enthalpy in the point 4, (J/kg)",
        )
        self.add_parameter(
            "enthalpy_52",
            self.model.i,
            initialize=lambda m, i: self.enthalpy_2[i]
            + (
                PropsSI(
                    "H",
                    "P",
                    self.condensing_pressure[i],
                    "S",
                    PropsSI(
                        "S",
                        "P",
                        self.evaporating_pressure[i, 0],
                        "H",
                        self.enthalpy_2[i],
                        self.refrigerant,
                    ),
                    self.refrigerant,
                )
                - self.enthalpy_2[i]
            )
            / self.compressor_efficiency,
            doc="Enthalpy in the point 52, (J/kg)",
        )
        self.add_parameter(
            "enthalpy_53",
            self.model.i,
            initialize=lambda m, i: self.enthalpy_3[i]
            + (
                PropsSI(
                    "H",
                    "P",
                    self.condensing_pressure[i],
                    "S",
                    self.evaporating_entrophy_vapour[i, 0],
                    self.refrigerant,
                )
                - self.enthalpy_3[i]
            )
            / self.compressor_efficiency,
            doc="Enthalpy in the point 4, (J/kg)",
        )
        self.add_parameter(
            "enthalpy_6",
            self.model.i,
            initialize=lambda m, i: PropsSI(
                "H",
                "P",
                self.condensing_pressure[i],
                "T",
                self.condensing_temperature[i] - self.temperature_subcooling,
                self.refrigerant,
            ),
            doc="Liquid enthalpy on condensing pressure, (J/kg)",
        )
        self.add_parameter(
            "enthalpy_7",
            self.model.i,
            initialize=lambda m, i: self.enthalpy_6[i],
            doc="Input enthalpy to the cooling-evaporating tank, (J/kg)",
        )
        self.add_parameter(
            "enthalpy_8",
            self.model.i,
            initialize=lambda m, i: self.evaporating_enthalpy_liquid[i, 0],
            doc="Liquid enthalpy in  cooling tank, (J/kg)",
        )
        self.add_parameter(
            "enthalpy_9",
            self.model.i,
            initialize=lambda m, i: self.enthalpy_8[i],
            doc="Input enthalpy to freezing tank, (J/kg)",
        )
        self.add_parameter(
            "enthalpy_10",
            self.model.i,
            initialize=lambda m, i: self.evaporating_enthalpy_liquid[i, 1],
            doc="Liquid enthalpy in the freezing-evaporating tank, (J/kg)",
        )
        # Vapour fraction for inpurs enthalpies in both tanks and entropies
        self.add_parameter(
            "fraction_input_0",
            self.model.i,
            initialize=lambda m, i: PropsSI(
                "Q",
                "P",
                self.evaporating_pressure[i, 0],
                "H",
                self.enthalpy_7[i],
                self.refrigerant,
            ),
            doc=(
                "Input fraction Liquid enthalpy in the freezing-evaporating"
                " tank, (J/kg)"
            ),
        )
        self.add_parameter(
            "fraction_input_1",
            self.model.i,
            initialize=lambda m, i: PropsSI(
                "Q",
                "P",
                self.evaporating_pressure[i, 1],
                "H",
                self.enthalpy_9[i],
                self.refrigerant,
            ),
            doc=(
                "Input fraction Liquid enthalpy in the freezing-evaporating"
                " tank, (J/kg)"
            ),
        )


class TwoTemperatureRefrigerationModel(TwoTemperaturePhysicalPropertiesModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        # Parameters - Compressors
        compressor_index = []
        for key in data.columns:
            s = self.namespace("COM_maximum_power_")
            if s in key:
                compressor_index.append(int(key[len(s) :]))
        self.compressor_index = compressor_index

        # Parameters - Compressors characteristics
        self.add_parameter(
            "compressor_steps",
            compressor_index,
            initialize=lambda m, j: 4,
            doc="Number of steps in compressors, (-)",
        )
        self.add_parameter(
            "compressor_on_off",
            compressor_index,
            initialize=lambda m, j: 4,
            doc="Ramping compressors possibility, (-)",
        )
        self.add_parameter(
            "maximum_power",
            self.model.i,
            self.compressor_index,
            initialize=lambda m, i, j: data[
                self.namespace("COM_maximum_power_{}".format(j))
            ][i],
            doc="Maximum power of compressor, (W)",
        )
        self.add_parameter(
            "on_ini",
            self.compressor_index,
            initialize=1,
            doc="Initialisation of the refrigeration system, (-)",
        )
        self.add_parameter(
            "start_up_cost",
            self.model.i,
            initialize=lambda m, i: data.get(
                "{}.start_up_cost".format(self.name), np.zeros(len(data.index))
            )[i],
            doc="Start-up cost of compressors, (EUR)",
        )
        # Parameters - Maximum flows
        self.add_parameter(
            "m_out_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("m_out_max")][i],
            doc="Maximum refrigerant flow in the condenser unit, (kg/s)",
        )
        self.add_parameter(
            "m_cooling_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("m_cooling_max")][i],
            doc="Maximum refrigerant flow in the cooling part, (kg/s)",
        )
        self.add_parameter(
            "m_freezing_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("m_freezing_max")][i],
            doc="Maximum refrigerant flow in the freezing part, (kg/s)",
        )
        # Parameters - Tanks/Accumulators
        self.add_parameter(
            "tank_volume_cooling",
            initialize=lambda m: par[self.namespace("tank_volume_cooling")],
            doc="Tank volume on the cooling temperature, (l)",
        )
        self.add_parameter(
            "tank_volume_freezing",
            initialize=lambda m: par[self.namespace("tank_volume_freezing")],
            doc="Tank volume on the freezing temperature, (l)",
        )
        self.add_parameter(
            "tank_cooling_min",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("tank_cooling_min")][i],
            doc="Lower limit in the cooling tank, (-)",
        )
        self.add_parameter(
            "tank_cooling_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("tank_cooling_max")][i],
            doc="Upper limit in the cooling tank, (-)",
        )
        self.add_parameter(
            "tank_freezing_min",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("tank_freezing_min")][i],
            doc="Lower limit in the freezing tank, (-)",
        )
        self.add_parameter(
            "tank_freezing_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("tank_freezing_max")][i],
            doc="Upper limit in the freezing tank, (-)",
        )
        self.add_parameter(
            "tank_cooling_ini",
            initialize=ini[self.namespace("tank_cooling")],
            doc="Iniitial stant in the cooling tank, (-)",
        )
        self.add_parameter(
            "tank_freezing_ini",
            initialize=ini[self.namespace("tank_freezing")],
            doc="Initial state in the freezing tank, (-)",
        )
        # Parameters - Evaporation
        self.add_parameter(
            "evaporating_cooling_heat_max",
            self.model.i,
            initialize=lambda m, i: data[
                self.namespace("evaporating_cooling_heat_max")
            ][i],
            doc="Maximum cooling heat, (W)",
        )
        self.add_parameter(
            "evaporating_freezing_heat_max",
            self.model.i,
            initialize=lambda m, i: data[
                self.namespace("evaporating_freezing_heat_max")
            ][i],
            doc="Maximum freezing heat, (W)",
        )
        # Variables - Compressors
        self.add_variable(
            "compressor_power",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Compressor power in the refrigeration system, (W)",
        )
        self.add_variable(
            "compressor_power_1",
            self.model.i,
            self.compressor_index,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Compressor power in the refrigeration system, (W)",
        )
        self.add_variable(
            "compressor_power_2",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Compressor power in the refrigeration system, (W)",
        )
        self.add_variable(
            "compressor_power_tot",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Total power of compressors, (W)",
        )
        # Variables - Flows
        self.add_variable(
            "m_out",
            self.model.i,
            domain=pyomo.Reals,
            initialize=0.0,
            bounds=lambda m, i: (0, self.m_out_max[i]),
            doc="Flow in the condensation unit, (kg/s)",
        )
        self.add_variable(
            "m_cooling",
            self.model.i,
            self.compressor_index,
            domain=pyomo.Reals,
            bounds=lambda m, i, j: (0, self.m_cooling_max[i]),
            initialize=0.0,
            doc="Cooling refrigerant flow in compressor, (kg/s)",
        )
        self.add_variable(
            "m_freezing",
            self.model.i,
            self.compressor_index,
            domain=pyomo.Reals,
            initialize=0.0,
            bounds=lambda m, i, j: (0, self.m_freezing_max[i]),
            doc="freezing refrigerant flow in compressor, (kg/s)",
        )
        # Variables - Tanks/Accumulators
        self.add_variable(
            "tank_cooling_state",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                self.tank_cooling_min[i],
                self.tank_cooling_max[i],
            ),
            doc="State in the cooling tank, (-)",
        )
        self.add_variable(
            "tank_freezing_state",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                self.tank_freezing_min[i],
                self.tank_freezing_max[i],
            ),
            doc="State in the freezing tank, (-)",
        )
        # Variables - Evaporation
        self.add_variable(
            "evaporating_cooling_heat",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (0, self.evaporating_cooling_heat_max[i]),
            doc="evaporating cooling heat, (W)",
        )
        self.add_variable(
            "evaporating_freezing_heat",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (0, self.evaporating_freezing_heat_max[i]),
            doc="evaporating freezing heat, (W)",
        )
        self.add_variable(
            "evaporating_cooling_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            bounds=lambda m, i: (
                0,
                self.evaporating_cooling_heat_max[i]
                / (self.evaporating_enthalpy_out[i, 0] - self.enthalpy_8[i]),
            ),
            doc="Flow throughout cooling evaporators, (m3/s)",
        )
        self.add_variable(
            "evaporating_freezing_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            bounds=lambda m, i: (
                0,
                self.evaporating_freezing_heat_max[i]
                / (self.evaporating_enthalpy_out[i, 1] - self.enthalpy_10[i]),
            ),
            doc="Flow throughout freezing evaporators, (m3/s)",
        )
        # Variables - General
        self.add_variable(
            "N_freq",
            self.model.i,
            self.compressor_index,
            domain=pyomo.Integers,
            initialize=1,
            doc="Step number of compressor, [1/s]",
        )
        self.add_variable(
            "operational_cost",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
            doc="The operational costs related to the refrigeration system, (EUR)",
        )

    def extend_model_constraints(self, data, par, ini):
        # Constraints - Tank/Accumlators
        self.add_constraint(
            "constraint_tank_cooling",
            self.model.i,
            self.compressor_index,
            rule=lambda m, i, j: (
                self.tank_volume_cooling
                * self.evaporating_density_vapour[i, 0]
                * (self.tank_cooling_state[i] - self.tank_cooling_state[i - 1])
                / (m.timestamp[i] - m.timestamp[i - 1])
                == self.vapour_evaporator_out[i, 0] * self.evaporating_cooling_flow[i]
                + self.fraction_input_0[i] * self.m_out[i]
                - (sum(self.m_cooling[i, j] for j in self.compressor_index))
                if i > 0
                else self.tank_cooling_state[0] == self.tank_cooling_ini
            ),
        )
        self.add_constraint(
            "constriant_tank_freezing",
            self.model.i,
            self.compressor_index,
            rule=lambda m, i, j: (
                self.tank_volume_freezing
                * self.evaporating_density_vapour[i, 1]
                * (self.tank_freezing_state[i] - self.tank_freezing_state[i - 1])
                / (m.timestamp[i] - m.timestamp[i - 1])
                == self.vapour_evaporator_out[i, 1] * self.evaporating_freezing_flow[i]
                - (1 - self.fraction_input_1[i])
                * (sum(self.m_freezing[i, j] for j in self.compressor_index))
                if i > 0
                else self.tank_freezing_state[0] == self.tank_freezing_ini
            ),
        )
        # Constraints - Compressors
        self.add_constraint(
            "constraint_compressor_power_maximum",
            self.model.i,
            self.compressor_index,
            rule=lambda m, i, j: self.compressor_power[i, j]
            <= self.maximum_power[i, j],
            doc="Maximum compressors powers",
        )
        self.add_constraint(
            "constraint_compressor_power_integer",
            self.model.i,
            self.compressor_index,
            rule=lambda m, i, j: self.compressor_power[i, j]
            == self.N_freq[i, j]
            * (self.maximum_power[i, j] / self.compressor_steps[j]),
            doc="Minumum compressors powers",
        )
        self.add_constraint(
            "constraint_compressor_power_ramping",
            self.model.i,
            self.compressor_index,
            rule=lambda m, i, j: (
                -self.maximum_power[i, j] / self.compressor_on_off[j]
                <= (self.compressor_power[i, j] - self.compressor_power[i - 1, j])
                <= self.maximum_power[i, j] / self.compressor_on_off[j]
                if i > 1
                else self.compressor_power[0, j]
                == self.maximum_power[0, j] / self.compressor_on_off[j]
            ),
        )
        # Compressors power consumptions
        self.add_constraint(
            "constraint_compressor_power",
            self.model.i,
            self.compressor_index,
            rule=lambda m, i, j: self.compressor_power[i, j]
            == self.m_freezing[i, j] * (self.enthalpy_2[i] - self.enthalpy_1[i])
            + self.m_freezing[i, j] * (self.enthalpy_52[i] - self.enthalpy_2[i])
            + self.m_cooling[i, j] * (self.enthalpy_53[i] - self.enthalpy_3[i]),
        )
        self.add_constraint(
            "constraint_compressor_power_1",
            self.model.i,
            rule=lambda m, i, j: self.compressor_power_1[i]
            == self.compressor_power[i, 1],
        )
        self.add_constraint(
            "constraint_compressor_power_2",
            self.model.i,
            self.compressor_index,
            rule=lambda m, i, j: self.compressor_power_2[i]
            == sum(self.compressor_power[i, j] for j in self.compressor_index),
        )
        self.add_constraint(
            "constraint_compressor_power_tot",
            self.model.i,
            self.compressor_index,
            rule=lambda m, i, j: self.compressor_power_tot[i]
            == sum(self.compressor_power[i, j] for j in self.compressor_index),
        )
        # Constraints - Flows
        self.add_constraint(
            "constraint_total_mass_flow",
            self.model.i,
            self.compressor_index,
            rule=lambda m, i, j: self.m_out[i]
            == sum(
                self.m_cooling[i, j] + self.m_freezing[i, j]
                for j in self.compressor_index
            ),
        )
        # Constraints - Evaporation
        self.add_constraint(
            "constraint_cooling_evaporating_heat",
            self.model.i,
            rule=lambda m, i: self.evaporating_cooling_flow[i]
            * (self.evaporating_enthalpy_out[i, 0] - self.enthalpy_8[i])
            == self.evaporating_cooling_heat[i],
        )
        self.add_constraint(
            "constraint_freezing_evaporating_heat",
            self.model.i,
            rule=lambda m, i: self.evaporating_freezing_flow[i]
            * (self.evaporating_enthalpy_out[i, 1] - self.enthalpy_10[i])
            == self.evaporating_freezing_heat[i],
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("fraction_input_1")] = [
            pyomo.value(self.fraction_input_1[i]) for i in self.model.i
        ]
        df[self.namespace("evaporating_temperature_2")] = [
            pyomo.value(self.evaporating_temperature_2[i]) for i in self.model.i
        ]
        df[self.namespace("evaporating_temperature_1")] = [
            pyomo.value(self.evaporating_temperature_1[i]) for i in self.model.i
        ]
        df[self.namespace("condensing_temperature")] = [
            pyomo.value(self.condensing_temperature[i]) for i in self.model.i
        ]
        df[self.namespace("compressor_power_1")] = [
            pyomo.value(self.compressor_power[i, 1]) for i in self.model.i
        ]
        df[self.namespace("compressor_power_2")] = [
            pyomo.value(self.compressor_power[i, 2]) for i in self.model.i
        ]
        df[self.namespace("compressor_power_tot")] = [
            pyomo.value(self.compressor_power_tot[i]) for i in self.model.i
        ]
        df[self.namespace("m_out")] = [pyomo.value(self.m_out[i]) for i in self.model.i]
        df[self.namespace("m_cooling_1")] = [
            pyomo.value(self.m_cooling[i, 1]) for i in self.model.i
        ]
        df[self.namespace("m_freezing_1")] = [
            pyomo.value(self.m_freezing[i, 1]) for i in self.model.i
        ]
        df[self.namespace("m_cooling_2")] = [
            pyomo.value(self.m_cooling[i, 2]) for i in self.model.i
        ]
        df[self.namespace("m_freezing_2")] = [
            pyomo.value(self.m_freezing[i, 2]) for i in self.model.i
        ]
        df[self.namespace("tank_cooling_state")] = [
            pyomo.value(self.tank_cooling_state[i]) for i in self.model.i
        ]
        df[self.namespace("tank_freezing_state")] = [
            pyomo.value(self.tank_freezing_state[i]) for i in self.model.i
        ]
        df[self.namespace("evaporating_cooling_heat")] = [
            pyomo.value(self.evaporating_cooling_heat[i]) for i in self.model.i
        ]
        df[self.namespace("evaporating_freezing_heat")] = [
            pyomo.value(self.evaporating_freezing_heat[i]) for i in self.model.i
        ]
        return df


class ChamberModel(TwoTemperaturePhysicalPropertiesModel):
    """
    Implements the thermal behavior of a single zone building with a 1st order model
    """

    rho_cp = 1000 * 4180

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)

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
            bounds=lambda m, i: (-self.evaporating_capacity[i], 0),
            initialize=0,
            doc="Heat flow to the storage tank (W)",
        )
        self.add_variable(
            "evaporating_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0.0,
            doc="Flow throughout freezing evaporators, (m3/s)",
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
            "constraint_evaporating_flow",
            self.model.i,
            rule=lambda m, i: self.evaporating_flow[i]
            * (self.evaporating_enthalpy_out[i, 1] - self.enthalpy_10[i])
            == -self.heat[i],
        )

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
        df[self.namespace("evaporating_flow")] = [
            pyomo.value(self.evaporating_flow[i]) for i in self.model.i
        ]

        return df


class VFRIndoorUnitModel(PhysicalProperties):
    """
    VRF indoor unit model
    """

    cp_air = 1000

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        # Parameters - VFR_indoor_unit
        self.add_parameter(
            "mode",
            self.model.i,
            domain=pyomo.Integers,
            doc="mode is 1 for heating, 2 for dry, 3 for fan, 4 for cooling, (-)",
        )
        self.add_parameter(
            "heat_capacity",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("cool_capacity")][i],
            doc="Maximum heating capacity of indoor unit, (W)",
        )
        self.add_parameter(
            "cool_capacity",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("heating_capacity")][i],
            doc="Maximum cooling capacity of indoor unit, (W)",
        )
        self.add_parameter(
            "air_flow",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("air_flow")][i],
            doc="Maximum air flow, (m3/s)",
        )
        self.add_parameter(
            "UA",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("UA")][i],
            doc="heat transfer coeffiecient and area in the indoor unit, (W/K)",
        )

        # Variables - VFR_inddor_unit
        self.add_variable(
            "refrigerant_temperature",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            doc="Refrigerant temperature in indoor unit, (C)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                -self.cool_capacity[i],
                self.heat_capacity[i],
            ),
            doc="Indoor unit heating/cooling heat, (W)",
        )
        self.add_variable(
            "refrigerant_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            doc="Refrigerant flow throughout the indoor unit, (kg/s)",
        )
        self.add_variable(
            "air_temperature_in",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            doc="Inlet air indoor temperature, (C)",
        )
        self.add_variable(
            "air_temperature_out",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            doc="Outlet air indoor temperature, (C)",
        )

    def extend_model_constraints(self, data, par, ini):
        # Constraints - VFR_inddor_unit
        self.add_constraint(
            "constraint_refrigerant_temperature",
            self.model.i,
            rule=lambda m, i: (
                self.refrigerant_temperature[i] == self.condensing_temperature[i]
                if mode == 1
                else self.refrigerant_temperature[i] == self.evaporating_temperature[i]
            ),
        )
        self.add_constraint(
            "constraint_refrigerant_heat",
            self.model.i,
            rule=lambda m, i: (
                self.heat[i]
                == self.refrigerant_flow[i]
                * (self.enthalpy_discharge[i] - self.enthalpy_liquid[i])
                if mode == 1
                else self.heat[i]
                == -self.refrigerant_flow[i]
                * (self.enthalpy_suction[i] - self.enthalpy_liquid[i])
            ),
        )
        self.add_constraint(
            "constraint_air_heat",
            self.model.i,
            rule=lambda m, i: self.heat[i]
            == self.air_flow[i]
            * self.cp_air
            * (self.air_temperature_out[i] - self.air_temperature_in[i]),
        )
        self.add_constraint(
            "constraint_heat_temperature_difference",
            self.model.i,
            rule=lambda m, i: self.heat[i]
            == self.UA[i]
            * (
                self.refrigerant_temperature[i]
                - (self.air_temperature_out[i] + self.air_temperature_in[i]) / 2
            ),
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("refrigerant_flow")] = [
            pyomo.value(self.refrigerant_flow[i]) for i in self.model.i
        ]
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("air_temperature_in")] = [
            pyomo.value(self.air_temperature_in[i]) for i in self.model.i
        ]
        df[self.namespace("air_temperature_out")] = [
            pyomo.value(self.air_temperature_out[i]) for i in self.model.i
        ]
        return df


class VFROutdoorUnitModel(PhysicalProperties):
    """
    VRF outdoor unit model
    """

    cp_air = 1000

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        # Parameters - VFR_inddor_unit
        self.add_parameter(
            "mode",
            self.model.i,
            domain=pyomo.Integers,
            doc="mode is 1 for heating, 2 for dry, 3 for fan, 4 for cooling, (-)",
        )
        self.add_parameter(
            "heat_capacity",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("cool_capacity")][i],
            doc="Maximum heating capacity of outdoor unit, (W)",
        )
        self.add_parameter(
            "cool_capacity",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("heating_capacity")][i],
            doc="Maximum cooling capacity of outdoor unit, (W)",
        )
        self.add_parameter(
            "air_flow",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("air_flow")][i],
            doc="Maximum air flow throughout outdoor unit, (m3/s)",
        )
        self.add_parameter(
            "UA",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("UA")][i],
            doc="heat transfer coeffiecient and area in the indoor unit, (W/K)",
        )
        self.add_parameter(
            "compressor_power_max",
            self.model.i,
            initialize=lambda m, i: data[self.namespace("compressor_power_max")][i],
            doc="Maximum power of compressor, (W)",
        )

        # Variables - VFR_outdoor_unit
        self.add_variable(
            "compressor_power",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (0, self.compressor_power_max[i]),
            doc="Indoor unit heating/cooling heat, (W)",
        )
        self.add_variable(
            "heat",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (
                -self.cool_capacity[i],
                self.heat_capacity[i],
            ),
            doc="Indoor unit heating/cooling heat, (W)",
        )
        self.add_variable(
            "refrigerant_flow",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            doc="Refrigerant flow throughout the indoor unit, (kg/s)",
        )
        self.add_variable(
            "air_temperature_in",
            self.model.i,
            domain=pyomo.Reals,
            initialize=lambda m, i: data[self.namespace("outdoor_temperature")][i],
            doc="Inlet air is equal to outdoor temperature, (C)",
        )
        self.add_variable(
            "air_temperature_out",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            doc="Outlet air indoor temperature, (C)",
        )

    def extend_model_constraints(self, data, par, ini):
        # Constraints - VFR_outdoor_unit
        self.add_constraint(
            "constraint_refrigerant_temperature",
            self.model.i,
            rule=lambda m, i: (
                self.refrigerant_temperature[i] == self.evaporating_temperature[i]
                if mode == 1
                else self.refrigerant_temperature[i] == self.condensing_temperature[i]
            ),
        )
        self.add_constraint(
            "constraint_compressor_power",
            self.model.i,
            rule=lambda m, i: self.compressor_power[i]
            == self.refrigerant_flow[i]
            * (self.enthalpy_discharge[i] - self.enthalpy_suction[i]),
        )
        self.add_constraint(
            "constraint_refrigerant_flow",
            self.model.i,
            rule=lambda m, i: (
                self.heat[i]
                == -self.refrigerant_flow[i]
                * (self.enthalpy_suction[i] - self.enthalpy_liquid[i])
                if mode == 1
                else self.heat[i]
                == self.refrigerant_flow[i]
                * (self.enthalpy_discharge[i] - self.enthalpy_liquid[i])
            ),
        )
        self.add_constraint(
            "constraint_air_heat",
            self.model.i,
            rule=lambda m, i: (
                self.heat[i]
                == -self.air_flow[i]
                * self.cp_air
                * (self.air_temperature_out[i] - self.air_temperature_in[i])
                if mode == 1
                else self.heat[i]
                == self.air_flow[i]
                * self.cp_air
                * (self.air_temperature_out[i] - self.air_temperature_in[i])
            ),
        )
        self.add_constraint(
            "constraint_heat_temperature_difference",
            self.model.i,
            rule=lambda m, i: self.heat[i]
            == -self.UA[i]
            * (
                self.refrigerant_temperature[i]
                - (self.air_temperature_out[i] + self.air_temperature_in[i]) / 2
            ),
        )

    def get_results(self):
        df = pd.DataFrame()
        df[self.namespace("refrigerant_flow")] = [
            pyomo.value(self.refrigerant_flow[i]) for i in self.model.i
        ]
        df[self.namespace("compressor_power")] = [
            pyomo.value(self.compressor_power[i]) for i in self.model.i
        ]
        df[self.namespace("heat")] = [pyomo.value(self.heat[i]) for i in self.model.i]
        df[self.namespace("air_temperature_in")] = [
            pyomo.value(self.air_temperature_in[i]) for i in self.model.i
        ]
        df[self.namespace("air_temperature_out")] = [
            pyomo.value(self.air_temperature_out[i]) for i in self.model.i
        ]
        return df


component_models = {
    "RefrigerationModel": RefrigerationModel,
    "RefrigerationModelMultiCOP": RefrigerationModelMultiCOP,
    "TwoTemperatureRefrigerationModel": TwoTemperatureRefrigerationModel,
    "ChamberModel": ChamberModel,
    "VFRIndoorUnitModel": VFRIndoorUnitModel,
    "VFROutdoorUnitModel": VFROutdoorUnitModel,
}
