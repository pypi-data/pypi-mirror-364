import numpy as np
import pyomo.environ as pyomo

# from scipy.interpolate import interp1d

from imby.simulations.custom_simulations.models.base import ComponentModel


class FixedValueModel(ComponentModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "value",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("value"), 0 * np.ones(len(self.model.i))
            )[i],
        )


class ConstrainedValueModel(ComponentModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "value_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("value_min"),
                -np.inf * np.ones(len(self.model.i)),
            )[i],
        )
        self.add_parameter(
            "value_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("value_max"),
                np.inf * np.ones(len(self.model.i)),
            )[i],
        )
        self.add_parameter(
            "activation_allowed",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("activation_allowed"),
                np.ones(len(self.model.i)),
            )[i],
        )
        self.add_variable(
            "value",
            self.model.i,
            domain=pyomo.Reals,
            bounds=lambda m, i: (self.value_min[i], self.value_max[i]),
            initialize=0,
        )

    def get_results(self):
        results = super().get_results()
        results[self.namespace("value")] = [
            pyomo.value(self.value[i]) for i in self.model.i
        ]
        results[self.namespace("value_min")] = [
            pyomo.value(self.value_min[i]) for i in self.model.i
        ]
        results[self.namespace("value_max")] = [
            pyomo.value(self.value_max[i]) for i in self.model.i
        ]
        return results


class SoftConstrainedValueModel(ComponentModel):
    def extend_model_variables(self, data, par, ini):
        super().extend_model_variables(data, par, ini)
        self.add_parameter(
            "value_soft_min",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("value_min"),
                -np.inf * np.ones(len(self.model.i)),
            )[i],
        )
        self.add_parameter(
            "value_soft_max",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("value_max"),
                np.inf * np.ones(len(self.model.i)),
            )[i],
        )
        self.add_parameter(
            "activation_allowed",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("activation_allowed"),
                np.ones(len(self.model.i)),
            )[i],
        )
        self.add_parameter(
            "constraint_violation_scale",
            self.model.i,
            initialize=lambda m, i: data.get(
                self.namespace("value_constraint_violation_scale"),
                0 * np.ones(len(self.model.i)),
            )[i],
        )
        self.add_variable("value", self.model.i, domain=pyomo.Reals, initialize=0)
        self.add_variable(
            "value_slack_min",
            self.model.i,
            domain=pyomo.NonNegativeReals,
            initialize=0,
        )
        self.add_variable(
            "value_slack_max",
            self.model.i,
            domain=pyomo.NonNegativeReals,
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
            "constraint_value_slack_min",
            self.model.i,
            rule=lambda m, i: (
                self.value_slack_min[i] >= self.value_soft_min[i] - self.value[i]
                if not np.isnan(self.value_soft_min[i])
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_value_slack_max",
            self.model.i,
            rule=lambda m, i: (
                self.value_slack_max[i] >= self.value[i] - self.value_soft_max[i]
                if not np.isnan(self.value_soft_max[i])
                else pyomo.Constraint.Skip
            ),
        )
        self.add_constraint(
            "constraint_constraint_violation",
            self.model.i,
            rule=lambda m, i: (
                self.constraint_violation[i]
                == +self.value_slack_min[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                * self.constraint_violation_scale[i]
                + self.value_slack_max[i]
                * (m.timestamp[i + 1] - m.timestamp[i])
                / 3.6e6
                * self.constraint_violation_scale[i]
                if i + 1 < len(m.i)
                else self.constraint_violation[i] == 0
            ),
        )

    def get_results(self):
        results = super().get_results()
        results[self.namespace("value")] = [
            pyomo.value(self.value[i]) for i in self.model.i
        ]
        results[self.namespace("value_min")] = [
            pyomo.value(self.value_soft_min[i]) for i in self.model.i
        ]
        results[self.namespace("value_max")] = [
            pyomo.value(self.value_soft_max[i]) for i in self.model.i
        ]
        return results

    def get_plot_config(self, color="k"):
        config = super().get_plot_config(color=color)

        if "value" not in config:
            config["value"] = {"plot": []}
        config["value"]["plot"].append(
            {
                "key": self.namespace("value"),
                "kwargs": {"color": color, "drawstyle": "steps-post"},
            }
        )
        config["value"]["plot"].append(
            {
                "key": self.namespace("value_min"),
                "kwargs": {
                    "color": color,
                    "drawstyle": "steps-post",
                    "marker": "^",
                    "label": "",
                    "linestyle": "",
                    "alpha": 0.3,
                },
            }
        )
        config["value"]["plot"].append(
            {
                "key": self.namespace("value_max"),
                "kwargs": {
                    "color": color,
                    "drawstyle": "steps-post",
                    "marker": "v",
                    "label": "",
                    "linestyle": "",
                    "alpha": 0.3,
                },
            }
        )
        return config


# class TimeOfDayBasedConstrainedValueModel(ConstrainedValueModel):
#     def __init__(
#         self,
#         *args,
#         constraint_hour=None,
#         constraint_min=None,
#         constraint_max=None,
#         activation_allowed=None,
#         timezone="Europe/Brussels",
#         **kwargs
#     ):
#         super().__init__(*args, **kwargs)
#         self.timezone = timezone
#         self._constraint_hour = constraint_hour
#         self._constraint_min = constraint_min
#         self._constraint_max = constraint_max
#         self._activation_allowed = activation_allowed
#
#     def get_data(self, timestamps):
#         data, par, ini = super().get_data(timestamps)
#
#         value_min = -np.inf * np.ones(len(timestamps))
#         value_max = np.inf * np.ones(len(timestamps))
#         activation_allowed = np.ones(len(timestamps))
#
#         datetimes = [
#             datetime.datetime.fromtimestamp(t, tz=pytz.timezone(self.timezone))
#             for t in timestamps
#         ]
#         hours = [d.hour + d.minute / 60 for d in datetimes]
#
#         if len(self._constraint_hour) > 0:
#             constraint_hour = (
#                 [self._constraint_hour[-1] - 24]
#                 + self._constraint_hour
#                 + [self._constraint_hour[0] + 24]
#             )
#             if self._constraint_min is not None:
#                 constraint_min = (
#                     [self._constraint_min[-1]]
#                     + self._constraint_min
#                     + [self._constraint_min[0]]
#                 )
#                 f = interp1d(
#                     constraint_hour,
#                     [v if v is not None else -np.inf for v in constraint_min],
#                     kind="zero",
#                     bounds_error=False,
#                 )
#                 value_min = f(hours)
#             if self._constraint_max is not None:
#                 constraint_max = (
#                     [self._constraint_max[-1]]
#                     + self._constraint_max
#                     + [self._constraint_max[0]]
#                 )
#                 f = interp1d(
#                     constraint_hour,
#                     [v if v is not None else np.inf for v in constraint_max],
#                     kind="zero",
#                     bounds_error=False,
#                 )
#                 value_max = f(hours)
#             if self._activation_allowed is not None:
#                 activation_allowed = (
#                     [self._activation_allowed[-1]]
#                     + self._activation_allowed
#                     + [self._activation_allowed[0]]
#                 )
#                 f = interp1d(
#                     constraint_hour,
#                     [
#                         v if v is not None else np.inf
#                         for v in activation_allowed
#                     ],
#                     kind="zero",
#                     bounds_error=False,
#                 )
#                 activation_allowed = f(hours)
#
#         data[self.namespace("value_min")] = value_min
#         data[self.namespace("value_max")] = value_max
#         data[self.namespace("activation_allowed")] = activation_allowed
#         return data, par, ini
#
#     def get_results(self):
#         results = super().get_results()
#         results["activation_allowed"] = [
#             pyomo.value(self.activation_allowed[i]) for i in self.model.i
#         ]
#         return results


# class TimeOfDayBasedSoftConstrainedValueModel(SoftConstrainedValueModel):
#     def __init__(
#         self,
#         *args,
#         constraint_hour=None,
#         constraint_min=None,
#         constraint_max=None,
#         activation_allowed=None,
#         timezone="Europe/Brussels",
#         constraint_violation_multiplier=ConstraintViolationMultiplier.COMMITMENT,
#         **kwargs
#     ):
#         super().__init__(*args, **kwargs)
#         self.timezone = timezone
#         self._constraint_hour = constraint_hour
#         self._constraint_min = constraint_min
#         self._constraint_max = constraint_max
#         self._activation_allowed = activation_allowed
#         self._constraint_violation_multiplier = constraint_violation_multiplier
#
#     def get_data(self, timestamps):
#         data, par, ini = super().get_data(timestamps)
#
#         value_min = -np.inf * np.ones(len(timestamps))
#         value_max = np.inf * np.ones(len(timestamps))
#         activation_allowed = np.ones(len(timestamps))
#
#         datetimes = [
#             datetime.datetime.fromtimestamp(t, tz=pytz.timezone(self.timezone))
#             for t in timestamps
#         ]
#         hours = [d.hour + d.minute / 60 for d in datetimes]
#
#         # FIXME not DRY
#         if len(self._constraint_hour) > 0:
#             constraint_hour = (
#                 [self._constraint_hour[-1] - 24]
#                 + self._constraint_hour
#                 + [self._constraint_hour[0] + 24]
#             )
#             if self._constraint_min is not None:
#                 constraint_min = (
#                     [self._constraint_min[-1]]
#                     + self._constraint_min
#                     + [self._constraint_min[0]]
#                 )
#                 f = interp1d(
#                     constraint_hour,
#                     [v if v is not None else -np.inf for v in constraint_min],
#                     kind="zero",
#                     bounds_error=False,
#                 )
#                 value_min = f(hours)
#             if self._constraint_max is not None:
#                 constraint_max = (
#                     [self._constraint_max[-1]]
#                     + self._constraint_max
#                     + [self._constraint_max[0]]
#                 )
#                 f = interp1d(
#                     constraint_hour,
#                     [v if v is not None else np.inf for v in constraint_max],
#                     kind="zero",
#                     bounds_error=False,
#                 )
#                 value_max = f(hours)
#             if self._activation_allowed is not None:
#                 activation_allowed = (
#                     [self._activation_allowed[-1]]
#                     + self._activation_allowed
#                     + [self._activation_allowed[0]]
#                 )
#                 f = interp1d(
#                     constraint_hour,
#                     [
#                         v if v is not None else np.inf
#                         for v in activation_allowed
#                     ],
#                     kind="zero",
#                     bounds_error=False,
#                 )
#                 activation_allowed = f(hours)
#
#         data[self.namespace("value_min")] = value_min
#         data[self.namespace("value_max")] = value_max
#         data[self.namespace("activation_allowed")] = activation_allowed
#         data[
#             self.namespace("value_constraint_violation_scale")
#         ] = self._constraint_violation_multiplier
#         return data, par, ini


component_models = {
    # "TimeOfDayBasedConstrainedValueModel": TimeOfDayBasedConstrainedValueModel,
    # "TimeOfDayBasedSoftConstrainedValueModel": TimeOfDayBasedSoftConstrainedValueModel,
}
