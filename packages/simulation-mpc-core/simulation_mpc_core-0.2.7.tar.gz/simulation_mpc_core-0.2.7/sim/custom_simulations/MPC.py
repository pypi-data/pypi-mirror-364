import logging
import os
import sys
from threading import Thread
from typing import Optional, Tuple, Union
from uuid import uuid4
import platform
# # Should be uncommented only if no any important errors/warnings appear. It is added only to ignore battery warnings
# # like: WARNING (W1002): Setting Var 'battery__energy[X]' to a numeric value `0`
# #    outside the bounds (X, X).
# #    See also https://pyomo.readthedocs.io/en/stable/errors.html#w1002
# import logging
# logging.getLogger('pyomo.core').setLevel(logging.ERROR)

import numpy as np
import pandas as pd
# from matplotlib import pyplot as plt
from pyomo import environ as pyomo
from pyomo.opt import TerminationCondition
from pyomo.util.infeasible import (
    log_infeasible_bounds,
    log_infeasible_constraints,
)

from .models import (
    component_models as simulation_component_models,
)


component_models = {}
component_models.update(simulation_component_models)

logger = logging.getLogger(__name__)



class MPCModel(object):
    """
    Manager class for building optimization models.

    Parameters
    ----------
    component_models: list of models.base.ComponentModel
        A list of Component models to be used in the optimization.
        The different models must be linked to each other in the models themselves.
    flow_connections: list of lists of str
        A list of lists of variables to  be linked with a flow constraint, meaning they must sum to 0. Variables are
        defined using the `component_name.variable_name` pattern.
    potential_connections: list of lists of str
        A list of lists of 2 variables to  be linked with a potential constraint, meaning they must be equal. Variables
        are defined using the `component_name.variable_name` pattern.
    objective_variables: list of string
        A list of model variables to be added in the objective function.
        The objective is always minimized.
    constraint_violation_variables: list of strings
        A list of model variables to be added to the objective function, representing constraint violations.
    reference_objective: float (EUR/kWh)
        A reference for the value of energy used to scale the constraint violation in some component models.
    optimizer: str
        The optimizer, passed to `pyomo.environ.SolverFactory`.
    optimizer_options: dict
        A dictionary of optimizer options passed to the pyomo solver.
    time_limit_multiplier: int
        When an optimization fails due to a time limit it is automatically restarted with the time limit multiplied by
        this factor.

    Examples
    --------

    .. code-block:: python

        model = ModelManager(
            component_models=[
                HeatPump('heat_pump'),
                HeatDemand('heat_demand'),
                PV('pv'),
                Battery('battery'),
                Grid('grid'),
            ],
            flow_connections = [
                ('heat_pump.heat', 'heat_demand.heat'),
                ('grid.power', 'heat_pump.power', 'pv.power', 'battery.power'),
            ],
            potential_connections = [],
            objective_variables=[
                'grid.operational_cost',
            ],
            constraint_violation_variables=[
                'battery.constraint_violation',
            ],
        )
        data, par, ini = model.get_data()
        results = model.solve(data, par, ini)
        model.send_commands()

    """

    OPTIMIZER_TERMINATION_CONDITION = {
        "optimal": 0,
        "feasible": 1,
        "intermediateNonInteger": 2,
        "infeasible": -1,
        "maxTimeLimit": -2,
    }

    def __init__(
        self,
        identifier: Optional[str] = None,
        component_models: list = None,
        flow_connections: list = None,
        potential_connections: list = None,
        objective_variables: list = None,
        constraint_violation_variables: Optional[list] = None,
        reference_objective: Optional[float] = 0.1,
        optimizer: Optional[str] = "cbc",
        optimizer_options: Optional[dict] = None,
        time_limit_multiplier: Optional[int] = -1,
        generate_report_when_infeasible: Optional[bool] = True,
        investigate_when_infeasible: Optional[bool] = False,
        get_data_threaded: Optional[bool] = True,
    ):
        self.identifier = identifier
        self.component_models = component_models or []
        self.flow_connections = flow_connections or []
        self.potential_connections = potential_connections or []
        self.objective_variables = objective_variables or []
        self.constraint_violation_variables = constraint_violation_variables or []
        self.reference_objective = reference_objective
        self.optimizer_string = optimizer
        self.optimizer = pyomo.SolverFactory(optimizer)
        self.optimizer = pyomo.SolverFactory(
            optimizer
        )  # twice to avoid a strange error
        self.get_data_threaded = get_data_threaded
        self.optimizer_result = None

        self.time_limit_multiplier = time_limit_multiplier
        self.generate_report_when_infeasible = generate_report_when_infeasible
        self.investigate_when_infeasible = investigate_when_infeasible

        if optimizer_options is None:
            if self.optimizer_string == "cbc":
                optimizer_options = {
                    "ratio": 0.01,
                    "sec": 20,
                }
            elif self.optimizer_string == "glpk":
                optimizer_options = {
                    "mipgap": 0.01,
                    "tmlim": 20,
                }
            else:
                optimizer_options = {}

        for key, val in optimizer_options.items():
            self.optimizer.options[key] = val

        self.model = None
        self.optimizer_termination_condition = None
        self.obj = None

        # create a reference to the manager in all components
        for c in self.component_models:
            c.set_manager(self)

        self.solved = False
        self.results = None
        self.data = None
        self.par = None
        self.ini = None
        self.command_ids = []
        self.solver_report = ""

    @property
    def component_models_dict(self):
        return {c.name: c for c in self.component_models}

    @classmethod
    def from_dict(cls, config, **kwargs):
        return cls(
            component_models=[
                get_component_model(key, val)
                for key, val in config["component_models"].items()
            ],
            flow_connections=config.get("flow_connections", None),
            potential_connections=config.get("potential_connections", None),
            objective_variables=config.get("objective_variables", None),
            constraint_violation_variables=config.get(
                "constraint_violation_variables", None
            ),
            optimizer=config.get("optimizer", "cbc"),
            optimizer_options=config.get("optimizer_options", None),
            **kwargs,
        )

    def to_dict(self):
        config = {
            "component_models": {c.name: c.to_dict() for c in self.component_models},
            "flow_connections": self.flow_connections,
            "potential_connections": self.potential_connections,
            "objective_variables": self.objective_variables,
            "constraint_violation_variables": self.constraint_violation_variables,
            "optimizer": self.optimizer_string,
            "optimizer_options": dict(self.optimizer.options),
            "reference_objective": self.reference_objective,
        }
        return config

    @staticmethod
    def var_to_attribute_name(key):
        return key.replace(".", "__")

    def objective(self, *args, **kwargs):
        """
        Method to define a custom objective function, overwriting the default objective created from the
        `objective_variables` and `constraint_violation_variables` attributes.

        Wrapper method for `pyomo.environ.Objective`.

        """
        self.obj = pyomo.Objective(*args, **kwargs)

    def get_data(
        self, timestamps: Union[np.ndarray, list]
    ) -> Tuple[pd.DataFrame, dict, dict]:
        """
        Retrieves data, parameters and initial conditions from all component models and combines them.

        Parameters
        ----------
        timestamps: list of numbers
            A list of timestamps for when to retrieve the data.

        Returns
        -------
        a 3-tuple of data, par, ini which can be passed to the `solve` method.

        """
        data = pd.DataFrame(
            data={"timestamp": timestamps},
            index=pd.to_datetime(timestamps, unit="s"),
        )
        par = {}
        ini = {}

        if self.get_data_threaded:
            get_data_threads = []
            datas = {}
            pars = {}
            inis = {}

            def append_component_data(component_model, timestamps):
                try:
                    c_data, c_par, c_ini = component_model.get_data(timestamps)
                    datas[component_model.name] = c_data
                    pars[component_model.name] = c_par
                    inis[component_model.name] = c_ini
                except:
                    logger.exception(
                        "{}: could not load data for component {}".format(
                            self, component_model
                        )
                    )

            for c in self.component_models:
                thread = Thread(target=append_component_data, args=(c, timestamps))
                thread.start()
                get_data_threads.append(thread)

            for thread in get_data_threads:
                thread.join()

            for c in self.component_models:
                if c.name in datas:
                    data = pd.concat([data, datas[c.name]], axis=1)
                    par.update(pars[c.name])
                    ini.update(inis[c.name])
                else:
                    raise Exception("could not load data")

        else:
            for c in self.component_models:
                c_data, c_par, c_ini = c.get_data(timestamps)
                data = pd.concat([data, c_data], axis=1)
                par.update(c_par)
                ini.update(c_ini)

        return data, par, ini

    def make_optimization_model(self, data, par, ini):
        """
        Creates a pyomo model.

        Parameters
        ----------
        data: pandas.DataFrame
            A dataframe with a pandas.datetime index containing the disturbances, all time dependent parameters.

        par: dict
            A dictionary with time independent parameters.

        ini: dict
            A dictionary with initial conditions for all state variables.

        """
        model = pyomo.ConcreteModel()
        self.model = model

        model.i = pyomo.Set(
            initialize=range(len(data.index)),
            doc="The time index",
        )
        model.timestamp = pyomo.Param(
            model.i,
            initialize=lambda m, i: data.index.values[i]
            .astype("datetime64[s]")
            .astype("int"),
            doc="The unix timestamp representing time in the model",
        )
        model.objective = pyomo.Var(
            model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc="Objective to be minimized in each time interval (EUR)",
        )
        model.constraint_violation = pyomo.Var(
            model.i,
            domain=pyomo.Reals,
            initialize=0,
            doc=(
                "Constraint violation cost in each time interval, same units"
                " as the objective (EUR)"
            ),
        )

        for c in self.component_models:
            c.model = model
            c.extend_model_variables(data, par, ini)

        model.constraint_objective = pyomo.Constraint(
            model.i,
            rule=lambda m, i: m.objective[i]
            == sum(
                [
                    (-1 if var.startswith("-") else 1)
                    * getattr(
                        m,
                        self.var_to_attribute_name(
                            var[1:] if var.startswith("-") else var
                        ),
                    )[i]
                    for var in self.objective_variables
                ]
            ),
        )
        model.constraint_constraint_violation = pyomo.Constraint(
            model.i,
            rule=lambda m, i: m.constraint_violation[i]
            == sum(
                [
                    getattr(m, self.var_to_attribute_name(var))[i]
                    for var in self.constraint_violation_variables
                ]
            ),
        )

        for c in self.component_models:
            c.extend_model_constraints(data, par, ini)

        for i, c in enumerate(self.flow_connections):
            constraint_name = "flow_connection_{}".format(i)
            setattr(
                model,
                constraint_name,
                pyomo.Constraint(
                    model.i,
                    rule=lambda m, i: sum(
                        [
                            (-1 if var.startswith("-") else 1)
                            * getattr(
                                m,
                                self.var_to_attribute_name(
                                    var[1:] if var.startswith("-") else var
                                ),
                            )[i]
                            for var in c
                        ]
                    )
                    == 0,
                ),
            )

        for i, c in enumerate(self.potential_connections):
            if len(c) != 2:
                raise Exception("Potential connections must consist of 2 variables")
            constraint_name = "potential_connection_{}".format(i)
            setattr(
                model,
                constraint_name,
                pyomo.Constraint(
                    model.i,
                    rule=lambda m, i: (-1 if c[0].startswith("-") else 1)
                    * getattr(
                        m,
                        self.var_to_attribute_name(
                            c[0][1:] if c[0].startswith("-") else c[0]
                        ),
                    )[i]
                    - (-1 if c[1].startswith("-") else 1)
                    * getattr(
                        m,
                        self.var_to_attribute_name(
                            c[1][1:] if c[1].startswith("-") else c[1]
                        ),
                    )[i]
                    == 0,
                ),
            )

        if self.obj is None:
            model.optimization_objective = pyomo.Objective(
                rule=lambda m: sum(m.objective[i] for i in m.i)
                + sum(m.constraint_violation[i] for i in m.i)
            )
        else:
            model.optimization_objective = self.obj

        return model

    def solve(self, data, par=None, ini=None, **kwargs):
        """
        Solves the optimization problem.

        Parameters
        ----------
        data: pandas.DataFrame
            A dataframe with a pandas.datetime index containing the disturbances, all time dependent parameters.
        par: dict
            A dictionary with time independent parameters.
        ini: dict
            A dictionary with initial conditions for all state variables.
        """
        self.solved = False
        self.results = None
        self.data = data
        self.par = par
        self.ini = ini

        par = par or {}
        ini = ini or {}

        model = self.make_optimization_model(data, par, ini)

        try:
            self.optimizer_result = self.optimizer.solve(model, **kwargs)
            self.optimizer_termination_condition = (
                self.optimizer_result.solver.termination_condition
            )
            if self.optimizer_termination_condition != TerminationCondition.optimal:
                from src.imby.sim.custom_simulations.models.power_grid import ImbalanceMarketModel
                if [i for i in self.component_models if type(i) == ImbalanceMarketModel]:
                    raise Exception('Imbalance infeasibility error')

        except Exception as e:
            if 'Imbalance infeasibility error' in e and platform.system() == 'Windows':
                raise Exception('Imbalance infeasibility error')
            # logger.debug(e)
            self.optimizer_termination_condition = TerminationCondition.other

        if self.optimizer_termination_condition == TerminationCondition.maxTimeLimit:
            try:
                [pyomo.value(model.objective[i]) for i in model.i]
                self.optimizer_termination_condition = TerminationCondition.feasible
            except:
                pass

        if self.optimizer_termination_condition == TerminationCondition.maxTimeLimit:
            # redo with a longer time limit
            if "sec" in self.optimizer.options and self.time_limit_multiplier > 1:
                sys.stdout.write(" redo")
                logger.warning(
                    "no solution available yet, re-solving the problem with a"
                    " longer time limit"
                )

                sec_temp = self.optimizer.options["sec"]
                tee_temp = kwargs.get("tee", False)
                symbolic_solver_labels_temp = kwargs.get(
                    "symbolic_solver_labels", False
                )

                self.optimizer.options["sec"] *= self.time_limit_multiplier
                kwargs["tee"] = False
                kwargs["symbolic_solver_labels"] = False

                self.optimizer_result = self.optimizer.solve(model, **kwargs)
                self.optimizer_termination_condition = (
                    self.optimizer_result.solver.termination_condition
                )
                self.optimizer.options["sec"] = sec_temp
                kwargs["tee"] = tee_temp
                kwargs["symbolic_solver_labels"] = symbolic_solver_labels_temp
            else:
                logger.error(
                    "{}: solver time limit reached without available solution".format(
                        self
                    )
                )

        elif self.optimizer_termination_condition in [
            TerminationCondition.infeasible,
            TerminationCondition.other,
        ]:
            log_infeasible_constraints(model)
            log_infeasible_bounds(model)
            report = ""
            if self.generate_report_when_infeasible:
                report += self.get_solver_output(model, **kwargs) + "\n"

            if self.investigate_when_infeasible:
                logger.info("{}: investigating infeasibility".format(self))
                report += self.investigate_infeasibility(data, par, ini) + "\n"

            logger.error(
                "{}: the problem is infeasible or has an unknown termination"
                " condition: {}".format(self, str(self.optimizer_termination_condition))
            )
            self.solver_report = report
        elif self.optimizer_termination_condition in [
            TerminationCondition.intermediateNonInteger
        ]:
            logger.warning("{}: intermediate non integer solution".format(self))

        if self.optimizer_termination_condition in [
            TerminationCondition.optimal,
            TerminationCondition.feasible,
            TerminationCondition.intermediateNonInteger,
        ]:
            self.solved = True
            self.results = self.get_results()
        return self.results

    def get_results(self):
        """
        Retrieves the results.

        Returns
        -------
        A `pandas.DataFrame` with the value of the result variables.

        """
        results = pd.DataFrame()
        results["i"] = [i for i in self.model.i]
        results["timestamp"] = [
            int(pyomo.value(self.model.timestamp[i])) for i in self.model.i
        ]
        results["objective"] = [
            pyomo.value(self.model.objective[i]) for i in self.model.i
        ]
        results["constraint_violation"] = [
            pyomo.value(self.model.constraint_violation[i]) for i in self.model.i
        ]
        results["optimizer_termination_condition"] = (
            self.OPTIMIZER_TERMINATION_CONDITION.get(
                str(self.optimizer_termination_condition), -1
            )
        )

        for c in self.component_models:
            results = pd.concat([results, c.get_results()], axis=1)

        results = results.set_index(pd.to_datetime(results["timestamp"], unit="s"))
        results.index.name = "time"
        return results

    def store_forecasts(self):
        for c in self.component_models:
            c.store_forecasts()

    def get_model_timestamps(self):
        """
        Helper method to return the timestamps defined in the model.

        """
        return [pyomo.value(self.model.timestamp[i]) for i in self.model.i]

    def send_commands(self):
        """
        Retrieve the schedules to be applied to the the different components.

        Returns
        -------
        A dictionary of schedules with the control id as key and a list of (timestamp, value) tuples as value.

        """
        logger.debug("{}: sending commands".format(self))
        if self.get_data_threaded:
            send_commands_threads = []
            c_ids = {}

            def append_command_ids(component_model):
                try:
                    c_ids[component_model.name] = component_model.send_commands()
                except Exception as e:
                    logger.exception(
                        "{}: could not send commands, {}".format(component_model, e)
                    )

            for c in self.component_models:
                thread = Thread(target=append_command_ids, args=(c,))
                thread.start()
                send_commands_threads.append(thread)

            for thread in send_commands_threads:
                thread.join()

            command_ids = []
            for ids in c_ids.values():
                command_ids += ids or []

        else:
            command_ids = []
            for c in self.component_models:
                command_ids += c.send_commands()
        self.command_ids = command_ids
        return self.command_ids

    def get_objective(self):
        timestamps = [int(pyomo.value(self.model.timestamp[i])) for i in self.model.i]
        values = [pyomo.value(self.model.objective[i]) for i in self.model.i]
        return np.trapz(values, x=timestamps)

    @property
    def states(self):
        """
        Property returning a list of state variables in all component models.

        """
        states = []
        for c in self.component_models:
            states += c.states
        return states

    def compute_cost(
        self,
        result: pd.DataFrame,
        data: pd.DataFrame,
        par: dict,
        cost_data: dict = None,
    ) -> dict:
        """
        Compute the cost related to a result.
        This is not the cost function used in the objective as the objective may contain artificial data to steer the
        optimization in a certain direction.

        Parameters
        ----------
        result: pandas.DataFrame
            A dataframe with the optimization results, returned by the `solve` method.

        data: pandas.DataFrame
            A dataframe similar to the one passed to `solve` but possibly with different values.

        par: dict
            A dictionary similar to the one passed to solve.

        cost_data: dict
            A dictionary with specific investment cost data for all component models. Most component models have default
            cost_data, these are overwritten if the same keys are supplied.

        """
        cost = {}
        for c in self.component_models:
            cost.update(c.compute_cost(result, data, par, cost_data))
        return cost

    def get_solver_output(self, model, **kwargs):
        # redo solution with symbolic labels to find the infeasibility
        if platform.system() == 'Windows':
            #logfile = 'E:\\Custom%20simulations\\log\\solverlog_{}.log'.format(uuid4())  # hardcode
            logfile = os.path.join(
                os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__), "..", "..", "..", ".."
                    )
                ),
                "log", f"solverlog_{uuid4()}.log"
            )
        else:
            logfile = "/tmp/solverlog_{}.log".format(uuid4())

        #if self.data.last_valid_index():

        kwargs["logfile"] = logfile
        kwargs["symbolic_solver_labels"] = True

        self.optimizer.solve(model, **kwargs)

        with open(logfile, "r") as f:
            solver_output = f.read()
        os.remove(logfile)
        return solver_output

    def investigate_infeasibility(self, data, par, ini, **kwargs):
        report = "Infeasibility analysis:\n"

        # loop over all constraints, remove one and solve the problem
        for component_name in dir(self.model):
            attr = getattr(self.model, component_name)
            if isinstance(attr, pyomo.Constraint):
                optimization_model = self.make_optimization_model(data, par, ini)
                optimization_model.del_component(component_name)
                kwargs["symbolic_solver_labels"] = True
                result = self.optimizer.solve(optimization_model, **kwargs)
                termination_condition = result.solver.termination_condition
                if termination_condition not in [
                    TerminationCondition.infeasible,
                    TerminationCondition.other,
                ]:
                    report += "removing constraint {}: {}\n".format(
                        component_name, termination_condition
                    )

        # loop over variables and remove bounds
        for component_name in dir(self.model):
            attr = getattr(self.model, component_name)
            if isinstance(attr, pyomo.Var):
                optimization_model = self.make_optimization_model(data, par, ini)
                var = getattr(optimization_model, component_name)
                has_bounds = False
                for key in var.keys():
                    if var[key].lb is not None and var[key].lb > -np.inf:
                        var[key].setlb(-np.inf)
                        has_bounds = True
                    if var[key].ub is not None and var[key].ub < np.inf:
                        var[key].setub(np.inf)
                        has_bounds = True

                if has_bounds:
                    kwargs["symbolic_solver_labels"] = True
                    result = self.optimizer.solve(optimization_model, **kwargs)
                    termination_condition = result.solver.termination_condition
                    if termination_condition not in [
                        TerminationCondition.infeasible,
                        TerminationCondition.other,
                    ]:
                        report += "removing bounds on variable {}: {}\n".format(
                            component_name, termination_condition
                        )

        return report

    # def get_plot_config(self, exclude_components=None):
    #     cmap = plt.get_cmap("tab10")
    #     if exclude_components is None:
    #         exclude_components = []
    #     config = {}
    #
    #     plot_models = [
    #         m for m in self.component_models if m.name not in exclude_components
    #     ]
    #     for i, c in enumerate(plot_models):
    #         color = cmap(i % 10)
    #         c_config = c.get_plot_config(color=color)
    #         for key in c_config:
    #             if key not in config:
    #                 config[key] = {}
    #             for kind in c_config[key]:
    #                 if kind not in config[key]:
    #                     config[key][kind] = []
    #                 config[key][kind] += c_config[key][kind]
    #
    #     # add explicit labels to keys starting with '_'
    #     for key in config:
    #         for kind in config[key]:
    #             for pl in config[key][kind]:
    #                 if (
    #                     pl["key"].startswith("_")
    #                     and "kwargs" in pl
    #                     and "label" not in pl["kwargs"]
    #                 ):
    #                     pl["kwargs"]["label"] = pl["key"][1:]
    #     return config

    # def get_measurement_plot_config(self, exclude_components=None):
    #     cmap = plt.get_cmap("tab10")
    #     if exclude_components is None:
    #         exclude_components = []
    #     config = {}
    #
    #     plot_models = [
    #         m for m in self.component_models if m.name not in exclude_components
    #     ]
    #     for i, c in enumerate(plot_models):
    #         color = cmap(i % 10)
    #         c_config = c.get_measurement_plot_config(color=color)
    #         for key in c_config:
    #             if key not in config:
    #                 config[key] = {}
    #             for kind in c_config[key]:
    #                 if kind not in config[key]:
    #                     config[key][kind] = []
    #                 config[key][kind] += c_config[key][kind]
    #     return config

    # def plot(
    #     self,
    #     results=None,
    #     plot_function=plt,
    #     plot_measurements=False,
    #     exclude_components=None,
    #     **kwargs,
    # ):
    #     if results is None:
    #         if self.results is not None:
    #             results = self.results
    #         else:
    #             results = self.get_results()
    #     plot_config = self.get_plot_config(exclude_components=exclude_components)
    #     if plot_measurements:
    #         measurement_plot_config = self.get_measurement_plot_config(
    #             exclude_components=exclude_components
    #         )
    #     else:
    #         measurement_plot_config = None
    #     return plot_function(
    #         plot_config,
    #         results,
    #         measurement_plot_config=measurement_plot_config,
    #         **kwargs,
    #     )

    def __repr__(self):
        return "<{} identifier={}>".format(self.__class__.__name__, self.identifier)


def get_component_model(name, config):
    """
    Helper function to retrieve a model instance from a config dictionary.
    """
    return component_models[config["class"]](name, **config.get("parameters", {}))