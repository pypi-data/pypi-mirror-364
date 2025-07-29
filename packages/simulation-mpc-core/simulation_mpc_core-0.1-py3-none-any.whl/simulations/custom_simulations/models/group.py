import pyomo.environ as pyomo

from imby.simulations.custom_simulations.models.base import ComponentModel


class PowerGroupModel(ComponentModel):
    def extend_model_variables(self, data, par, ini):
        self.add_variable("power", self.model.i, domain=pyomo.Reals)
        self.add_variable("power_in", self.model.i, domain=pyomo.Reals)
        self.add_variable("constraint_violation", self.model.i, domain=pyomo.Reals)
        self.add_variable("constraint_violation_in", self.model.i, domain=pyomo.Reals)
        self.add_variable("operational_cost", self.model.i, domain=pyomo.Reals)
        self.add_variable("operational_cost_in", self.model.i, domain=pyomo.Reals)

    def extend_model_constraints(self, data, par, ini):
        self.add_constraint(
            "constraint_power",
            self.model.i,
            rule=lambda m, i: self.power[i] + self.power_in[i] == 0,
        )
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: self.constraint_violation[i]
            + self.constraint_violation_in[i]
            == 0,
        )
        self.add_constraint(
            "constraint_operational_cost",
            self.model.i,
            rule=lambda m, i: self.operational_cost[i] + self.operational_cost_in[i]
            == 0,
        )

    def get_results(self):
        df = super().get_results()
        df[self.namespace("power")] = [pyomo.value(self.power[i]) for i in self.model.i]
        df[self.namespace("operational_cost")] = [
            pyomo.value(self.operational_cost[i]) for i in self.model.i
        ]
        df[self.namespace("constraint_violation")] = [
            pyomo.value(self.constraint_violation[i]) for i in self.model.i
        ]
        return df


component_models = {
    "PowerGroupModel": PowerGroupModel,
}
