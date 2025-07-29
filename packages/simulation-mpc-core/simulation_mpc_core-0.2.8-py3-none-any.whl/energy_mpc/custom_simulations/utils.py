# import numpy as np


# def integrate(x, y):
#     return np.trapz(y, x=x)
def integrate(time: list, val: list):
    """
    Helper method to compute the zero-order-hold integral of a quantity.

    Parameters
    ----------
    time: array
        time points in datetime or times in seconds

    val: array
        values

    """
    # Artem and Misha chek
    if len(time) <= 1:
        return 0

    dt = time[1:] - time[:-1]
    if hasattr(dt[0], "total_seconds"):
        return sum([dt_i.total_seconds() * val_i for dt_i, val_i in zip(dt, val[:-1])])
    else:
        return sum([dt_i * val_i for dt_i, val_i in zip(dt, val[:-1])])
