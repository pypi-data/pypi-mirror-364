import logging
#from copy import deepcopy

import pandas as pd
import pyomo.environ as pyomo

logger = logging.getLogger(__name__)


Skip = pyomo.Constraint.Skip
Binary = pyomo.Binary
Reals = pyomo.Reals
NonNegativeReals = pyomo.NonNegativeReals


class ComponentModel(object):
    """
    A base class for all optimization component models.
    Can be used for design optimization models and in live control models.

    """

    def __init__(self, name):
        self.name = name or self.__class__.__name__
        self._states = []

        self.model_attributes = {}
        self.model = None
        self.manager = None

    @staticmethod
    def var_to_attribute_name(key):
        return key.replace(".", "__")

    @staticmethod
    def attribute_name_to_var(key):
        return key.replace("__", ".")

    @staticmethod
    def get_forecast_config(
        forecast_config,
        default_forecast_config=None,
        merge_forecast_config=True,
    ):
        if forecast_config is not None:
            if merge_forecast_config:
                forecast_config = {
                    **default_forecast_config,
                    **forecast_config,
                }
            else:
                forecast_config = forecast_config
        else:
            forecast_config = default_forecast_config
        return forecast_config

    def get_model(self):
        return self.model

    def set_manager(self, manager):
        self.manager = manager

    def model_namespace(self, key):
        return "{}__{}".format(self.name.replace(".", "__"), key)

    def namespace(self, key):
        return "{}.{}".format(self.name, key)

    def __getattr__(self, key):
        if key in self.model_attributes:
            return self.model_attributes[key]
        else:
            raise KeyError("Model attribute {} does not exist".format(key))

    def add_set(self, key, *args, **kwargs):
        self.model_attributes[key] = pyomo.Set(*args, **kwargs)
        if hasattr(self.model, self.model_namespace(key)):
            self.model.del_component(getattr(self.model, self.model_namespace(key)))
        setattr(self.model, self.model_namespace(key), self.model_attributes[key])

    def add_parameter(self, key, *args, **kwargs):
        self.model_attributes[key] = pyomo.Param(*args, **kwargs)
        if hasattr(self.model, self.model_namespace(key)):
            self.model.del_component(getattr(self.model, self.model_namespace(key)))
        setattr(self.model, self.model_namespace(key), self.model_attributes[key])

    def add_variable(self, key, *args, **kwargs):
        self.model_attributes[key] = pyomo.Var(*args, **kwargs)
        if hasattr(self.model, self.model_namespace(key)):
            self.model.del_component(getattr(self.model, self.model_namespace(key)))
        setattr(self.model, self.model_namespace(key), self.model_attributes[key])

    def add_constraint(self, key, *args, **kwargs):
        self.model_attributes[key] = pyomo.Constraint(*args, **kwargs)
        if hasattr(self.model, self.model_namespace(key)):
            self.model.del_component(getattr(self.model, self.model_namespace(key)))
        setattr(self.model, self.model_namespace(key), self.model_attributes[key])

    def add_binary_product_constraint(
        self, key, product, binary, continuous, *args, **kwargs
    ):
        """
        Adds a constraint linking a binary and 2 continuous variables like ``product == binary * continuous``.

        """
        self.add_constraint(
            "{}_ub_1".format(key),
            *args,
            rule=lambda m, *a: self.product[a]
            <= self.binary[a] * self.continuous_max[a],
            doc="ub_1",
        )
        self.add_constraint(
            "{}_ub_2".format(key),
            *args,
            rule=lambda m, *a: self.product[a] <= self.continuous[a],
            doc="ub_2",
        )
        self.add_constraint(
            "{}_lb_1".format(key),
            *args,
            rule=lambda m, *a: self.product[a]
            >= self.continuous[a] - (1 - self.binary[a]) * self.continuous_max[a],
            doc="lb_1",
        )
        self.add_constraint(
            "{}_lb_2".format(key),
            *args,
            rule=lambda m, *a: self.product[a] >= 0,
            doc="lb_2",
        )

    def extend_model_variables(self, data, par, ini):
        pass

    def extend_model_constraints(self, data, par, ini):
        pass

    def get_data(self, timestamps):
        """
        Redefine in child classes for control models only.

        Returns
        -------
        pandas.DataFrame, dict, dict with data, parameters, initialconditions

        """
        logger.debug("{}: retrieving data".format(self))
        data = pd.DataFrame(data={}, index=pd.to_datetime(timestamps, unit="s"))
        par = {}
        ini = {}
        return data, par, ini

    def get_results(self):
        """
        Redefine in a child class.

        Returns
        -------
        pandas.DataFrame with the solution for the variables in the component

        """
        return pd.DataFrame()

    def store_forecasts(self):
        """
        Redefine in a child class to store forecasts

        """
        pass

    def get_model_timestamps(self):
        """
        Utility method to return the timestamps in the optimization model.

        """
        return [int(pyomo.value(self.model.timestamp[i])) for i in self.model.i]

    def send_commands(self):
        """
        Base method to be overridden in the child classes, called after the problem is solved and should send commands
        to the devices.

        Returns
        -------
        A list of command ids
        """
        return []

    @property
    def states(self):
        return self._states

    def compute_cost(
        self,
        results: pd.DataFrame,
        data: pd.DataFrame,
        parameters: dict,
        cost_data: dict = None,
    ) -> dict:
        return {}

    def get_plot_config(self, color="k"):
        return {}

    def get_measurement_plot_config(self, color="k"):
        return {}

    def to_dict(self):
        config = {"class": self.__class__.__name__, "parameters": {}}
        return config

    def __str__(self):
        if self.manager is not None:
            identifier = self.manager.identifier
        else:
            identifier = "None"
        return "<{}, name={}, model={}>".format(
            self.__class__.__name__, self.name, identifier
        )

    def __reduce__(self):
        return self.__class__, (self.name,)
