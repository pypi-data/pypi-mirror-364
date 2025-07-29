import logging

import numpy as np
import pyomo.environ as pyomo

from imby.simulations.custom_simulations.models.base import (
    Binary,
    ComponentModel,
    Reals,
    Skip,
)

logger = logging.getLogger(__name__)


class OnOffComponentModelBase(ComponentModel):
    """
    Base model for devices with an on-off state
    """

    def __init__(self, *args, on_commitment_time=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._on_commitment_time = (
            0 if on_commitment_time is None else on_commitment_time
        )

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_variable("on", self.model.i, domain=Binary)
        self.add_parameter("on_ini", initialize=ini.get(self.namespace("on"), 0))
        self.add_parameter(
            "on_committed",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("on_committed"), np.nan * np.ones(len(data))
            )[i],
        )
        self.add_parameter(
            "minimum_on_time",
            initialize=par.get(self.namespace("minimum_on_time"), 0),
        )
        self.add_parameter(
            "minimum_off_time",
            initialize=par.get(self.namespace("minimum_off_time"), 0),
        )
        self.add_parameter(
            "last_on_change",
            initialize=par.get(self.namespace("last_on_change"), -1),
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)
        self.add_constraint(
            "constraint_minimum_on_time",
            self.model.i,
            self.model.i,
            rule=lambda m, i1, i2: (
                Skip
                if self.minimum_on_time <= 0
                else (
                    Skip
                    if i2 < i1
                    else (
                        Skip
                        if m.timestamp[i2] >= self.minimum_on_time + m.timestamp[i1]
                        else (
                            Skip
                            if i1 == 0
                            and self.on_ini == 1
                            and m.timestamp[i2]
                            >= self.minimum_on_time + self.last_on_change
                            else (
                                1 + (self.on_ini - self.on[i2]) <= 1
                                if self.on_ini == 1 and i1 == 0 and i2 == 0
                                else (
                                    1 + (self.on[i2 - 1] - self.on[i2]) <= 1
                                    if self.on_ini == 1 and i1 == 0
                                    else (
                                        1 + (self.on_ini - self.on[i2]) <= 1
                                        if self.on_ini == 1 and i2 == 0
                                        else (
                                            (self.on[i1] - self.on_ini)
                                            + (self.on_ini - self.on[i2])
                                            <= 1
                                            if i1 == 0 and i2 == 0
                                            else (
                                                (self.on[i1] - self.on_ini)
                                                + (self.on[i2 - 1] - self.on[i2])
                                                <= 1
                                                if i1 == 0
                                                else (
                                                    (self.on[i1] - self.on[i1 - 1])
                                                    + (self.on_ini - self.on[i2])
                                                    <= 1
                                                    if i2 == 0
                                                    else (self.on[i1] - self.on[i1 - 1])
                                                    + (self.on[i2 - 1] - self.on[i2])
                                                    <= 1
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            ),
        )
        self.add_constraint(
            "constraint_minimum_off_time",
            self.model.i,
            self.model.i,
            rule=lambda m, i1, i2: (
                Skip
                if self.minimum_off_time <= 0
                else (
                    Skip
                    if i2 < i1
                    else (
                        Skip
                        if m.timestamp[i2] >= self.minimum_off_time + m.timestamp[i1]
                        else (
                            Skip
                            if i1 == 0
                            and self.on_ini == 0
                            and m.timestamp[i2]
                            >= self.minimum_off_time + self.last_on_change
                            else (
                                1 + (self.on[i2] - self.on_ini) <= 1
                                if self.on_ini == 0 and i1 == 0 and i2 == 0
                                else (
                                    1 + (self.on[i2] - self.on[i2 - 1]) <= 1
                                    if self.on_ini == 0 and i1 == 0
                                    else (
                                        1 + (self.on[i2] - self.on_ini) <= 1
                                        if self.on_ini == 0 and i2 == 0
                                        else (
                                            (self.on_ini - self.on[i1])
                                            + (self.on[i2] - self.on_ini)
                                            <= 1
                                            if i1 == 0 and i2 == 0
                                            else (
                                                (self.on_ini - self.on[i1])
                                                + (self.on[i2] - self.on[i2 - 1])
                                                <= 1
                                                if i1 == 0
                                                else (
                                                    (self.on[i1 - 1] - self.on[i1])
                                                    + (self.on[i2] - self.on_ini)
                                                    <= 1
                                                    if i2 == 0
                                                    else (self.on[i1 - 1] - self.on[i1])
                                                    + (self.on[i2] - self.on[i2 - 1])
                                                    <= 1
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            ),
        )
        self.add_constraint(
            "constraint_on_committed",
            self.model.i,
            rule=lambda m, i: (
                Skip
                if np.isnan(self.on_committed[i])
                else self.on[i] == self.on_committed[i]
            ),
        )

    def get_results(self):
        results = super().get_results()
        results[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        return results


class HysteresisControllerModel(ComponentModel):
    """

    Notes
    -----
    Logic Table:

    on[i-1]  below_on[i]  below_off[i]   on[i]    helper_on[i]  helper_off[i]
    0        0
    0        0
    0        1
    0        1  ...
    1        0
    1        0
    1        1
    1        1


    """

    def __init__(
        self,
        *args,
        switch_on_state=0,
        switch_off_state=1,
        on_value=1,
        off_value=0,
        large_number=1000,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._switch_on_state = switch_on_state
        self._switch_off_state = switch_off_state
        self._on_value = on_value
        self._off_value = off_value
        self._large_number = large_number

    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "switch_on_state",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("switch_on_state"),
                0 * np.ones(len(self.model.i)),
            )[i],
        )
        self.add_parameter(
            "switch_off_state",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("switch_off_state"),
                1 * np.ones(len(self.model.i)),
            )[i],
        )
        self.add_parameter(
            "control_on",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("control_on"), 1 * np.ones(len(self.model.i))
            )[i],
        )
        self.add_parameter(
            "control_off",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("control_off"), 0 * np.ones(len(self.model.i))
            )[i],
        )

        self.add_variable("state", self.model.i, domain=Reals)
        self.add_variable(
            "control",
            self.model.i,
            domain=Reals,
        )
        self.add_variable(
            "on",
            self.model.i,
            domain=Binary,
        )

        self.add_variable("state_below_on", self.model.i, domain=Binary)
        self.add_variable("state_above_off", self.model.i, domain=Binary)

        self.add_variable(
            "helper_on",
            self.model.i,
            domain=Reals,
            bounds=(0, 1),
        )
        self.add_variable(
            "helper_off",
            self.model.i,
            domain=Reals,
            bounds=(0, 1),
        )

    def extend_model_constraints(self, data, par, ini):
        super().extend_model_constraints(data, par, ini)

        self.add_constraint(
            "constraint_control",
            self.model.i,
            rule=lambda m, i: self.control[i]
            == self.on[i] * self.control_on[i] + (1 - self.on[i]) * self.control_off[i],
        )

        self.add_constraint(
            "constraint_state_below_on_geq",
            self.model.i,
            rule=lambda m, i: self.state[i]
            >= self.switch_on_state[i] - self._large_number * self.state_below_on[i],
        )
        self.add_constraint(
            "constraint_state_below_on_leq",
            self.model.i,
            rule=lambda m, i: self.state[i]
            <= self.switch_on_state[i]
            + self._large_number * (1 - self.state_below_on[i]),
        )
        self.add_constraint(
            "constraint_state_above_off_geq",
            self.model.i,
            rule=lambda m, i: self.state[i]
            >= self.switch_off_state[i]
            - self._large_number * (1 - self.state_above_off[i]),
        )
        self.add_constraint(
            "constraint_state_above_off_leq",
            self.model.i,
            rule=lambda m, i: self.state[i]
            <= self.switch_off_state[i] + self._large_number * self.state_above_off[i],
        )

        self.add_constraint(
            "constraint_helper_on_1",
            self.model.i,
            rule=lambda m, i: self.helper_on[i] <= self.on[i - 1] if i > 0 else Skip,
        )
        self.add_constraint(
            "constraint_helper_on_2",
            self.model.i,
            rule=lambda m, i: self.helper_on[i] <= 1 - self.state_above_off[i],
        )
        self.add_constraint(
            "constraint_helper_on_3",
            self.model.i,
            rule=lambda m, i: (
                self.helper_on[i] >= self.on[i - 1] - self.state_above_off[i]
                if i > 0
                else Skip
            ),
        )

        self.add_constraint(
            "constraint_helper_off_1",
            self.model.i,
            rule=lambda m, i: (
                self.helper_off[i] <= 1 - self.on[i - 1] if i > 0 else Skip
            ),
        )
        self.add_constraint(
            "constraint_helper_off_2",
            self.model.i,
            rule=lambda m, i: self.helper_off[i] <= self.state_below_on[i],
        )
        self.add_constraint(
            "constraint_helper_off_3",
            self.model.i,
            rule=lambda m, i: (
                self.helper_off[i] >= self.state_below_on[i] - self.on[i - 1]
                if i > 0
                else Skip
            ),
        )
        self.add_constraint(
            "constraint_on",
            self.model.i,
            rule=lambda m, i: self.on[i] == self.helper_on[i] + self.helper_off[i],
        )

    def get_results(self):
        results = super().get_results()
        results[self.namespace("state")] = [
            pyomo.value(self.state[i]) for i in self.model.i
        ]
        results[self.namespace("on")] = [pyomo.value(self.on[i]) for i in self.model.i]
        results[self.namespace("control")] = [
            pyomo.value(self.control[i]) for i in self.model.i
        ]
        return results
