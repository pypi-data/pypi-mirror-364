import json
import os
import pickle
import sys
import time
from hashlib import sha256
from typing import Optional

import pandas as pd

from src.imby.sim.custom_simulations import MPCModel


def moving_horizon_optimization(
    model: MPCModel,
    data: pd.DataFrame,
    par: dict,
    ini: dict,
    horizon: int,
    moving: int,
    since: Optional[int] = None,
    until: Optional[int] = None,
    precomputing: Optional[int] = 0,
    update_data: Optional[callable] = None,
    verbose: Optional[int] = 1,
    cache_path: Optional[str] = None,
    **kwargs,
):
    """
    Run a moving horizon simulation for a model.

    Parameters
    ----------
    model:
        The model to be simulated.
    data: pandas.DataFrame
        Time varying data fed to the model in a pandas.DataFrame with a datetime index.
    par: dict
        Time invariant data fed to the model.
    ini: dict
        Model initial conditions.
    since: int
        Simulation start timestamp (s).
    until: int
        Simulation end timestamp (s).
    horizon: int
        Optimization horizon (s).
    moving: int
        The time the horizon is shifted each optimization (s).
    precomputing: int
        Time before the start of the simulation that should also be simulated to get realistic initial conditions. This
        is not included in the results (s).
    update_data: callable
        A function which updates a part of the data based on the results. Requires 2 arguments `data_part`, a part
        of the original data DataFrame in the current horizon and `result`, the available result DataFrame.
    verbose: int
        An integer determining the amount of output printing
    cache_path: str
        Path where results are cached
    **kwargs: keyword arguments
        Arguments are passed to the solve function of Pyomo
    """

    # check the cache
    file_path = None
    if cache_path is not None:
        cache_key = sha256(
            bytes(
                ",".join(
                    [
                        json.dumps(model.to_dict()),
                        data.to_csv(),
                        json.dumps(par, sort_keys=True),
                        json.dumps(ini, sort_keys=True),
                        str(horizon),
                        str(moving),
                        str(since),
                        str(until),
                        str(precomputing),
                    ]
                ),
                encoding="utf-8",
            )
        ).hexdigest()
        cache_filename = "{}_cache.pkl".format(cache_key)
        file_path = os.path.join(cache_path, cache_filename)
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                temp = pickle.load(f)
                return temp["result"], temp["data"], temp["status"]

    if since is None:
        since = (
            int(data.index.values[0].astype("datetime64[s]").astype("int"))
            + precomputing
        )
    if until is None:
        until = int(data.index.values[-1].astype("datetime64[s]").astype("int"))

    since_part = since - precomputing
    result = pd.DataFrame()
    result_part = None
    new_data = pd.DataFrame()

    # start the solution
    start_time = time.time()
    barwidth = 80 - 2
    barvalue = 0
    if verbose > 0:
        sys.stdout.write("start")
        # sys.stdout.write("[" + (" " * barwidth) + "] ")
        # sys.stdout.flush()
        # time.sleep(0.2)
    tee = verbose > 1

    while True:
        until_part = since_part + horizon

        if verbose > 1:
            print(
                "\n### running optimization {} -> {} ###".format(since_part, until_part)
            )

        since_part_dt = pd.to_datetime(since_part, unit="s")
        until_part_dt = pd.to_datetime(until_part, unit="s")
        data_part = data.loc[since_part_dt:until_part_dt]
        if update_data is not None and result_part is not None:
            data_part = update_data(data_part, result)

        # get the new initial_conditions
        if result_part is not None:
            ini = {
                key: float(result_part[key].loc[since_part_dt]) for key in model.states
            }

        result_part = model.solve(data_part, par, ini, tee=tee, **kwargs)
        # result_part = model.solve(data_part, par, ini, tee=tee, logfile='logs.log')
        if result_part is None:
            if until_part >= since_part:
                status = "infeasible at the end"
                break
            # infeasibility = True
            # while infeasibility:
            #     print(f'infeasibility with {until_part_dt} as last timestamp. Trying to cut the results and recalculate')
            #     if until_part_dt > data.index[-1]:
            #         until_part_dt = data.index[-1]
            #     else:
            #         until_part_dt = until_part_dt - pd.DateOffset(minutes=15)# - pd.DateOffset(days=1)
            #     data_part = data.loc[since_part_dt:until_part_dt]
            #     result_part = model.solve(data_part, par, ini, tee=tee, **kwargs)
            #     if result_part is not None:
            #         infeasibility = False

        # solver error handling
        if result_part["optimizer_termination_condition"].iloc[1] == -2:
            if verbose > 0:
                print(" time limit, {}".format(since_part_dt))
            status = "time limit"
            break
        elif result_part["optimizer_termination_condition"].iloc[1] < 0:
            if verbose > 0:
                print(" infeasible, {}".format(since_part_dt))
            status = "infeasible"
            break

        # concatenate the result and data
        result = pd.concat([result, result_part])
        result = result.reset_index()
        result = result.drop_duplicates(subset="time", keep="last")
        result = result.set_index("time")

        new_data = pd.concat([new_data, data_part])
        new_data = new_data.reset_index()
        new_data = new_data.drop_duplicates(subset="index", keep="last")
        new_data = new_data.set_index("index")

        if verbose == 1:
            precentage_done = (since_part + moving - since) / (until - since)
            if precentage_done * barwidth > barvalue:
                barvalue += int(round(precentage_done * barwidth - barvalue))
                sys.stdout.write(
                    "\r[" + ("=" * barvalue) + (" " * (barwidth - barvalue)) + "] "
                )
                sys.stdout.flush()
                time.sleep(0.2)

        since_part += moving
        if since_part >= until:
            status = "success"
            if verbose == 1:
                print(" runtime: {:.1f} s".format(time.time() - start_time))
            break

    # trim the result and data to the requested times
    since_dt = pd.to_datetime(since, unit="s")
    until_dt = pd.to_datetime(until, unit="s")
    result = result.loc[since_dt:until_dt]
    data = new_data.loc[since_dt:until_dt]

    # save to cache
    if file_path is not None:
        with open(file_path, "w") as f:
            pickle.dump({"result": result, "data": data, "status": status}, f)

    return result, data, status
