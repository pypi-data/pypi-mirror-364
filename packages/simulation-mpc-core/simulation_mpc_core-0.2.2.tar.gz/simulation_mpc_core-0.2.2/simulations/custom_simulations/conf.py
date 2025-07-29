from enum import IntEnum


class ConstraintViolationMultiplier(IntEnum):
    """
    * PHYSICS e.g. grid connection, minimum or maximum temperatures, allowed battery SOC, ... : 200
    * COMFORT e.g. EV not charged up to desired level, comfort temperature not reached, ... : 100
    * COMMITMENT e.g. USEF orders, ... : 50
    * PRECHECKEDCONSTRAINT e.g. USEF allowed flex, ... : 20
    * REQUESTS e.g. request to increase consumption based on the imbalance prices, USEF requested flex : 2

    """

    PHYSICS = 100
    STRONG_COMMITMENT = 80
    COMFORT = 60
    COMMITMENT = 40
    PRECHECKEDCONSTRAINT = 20
    REQUEST = 2
