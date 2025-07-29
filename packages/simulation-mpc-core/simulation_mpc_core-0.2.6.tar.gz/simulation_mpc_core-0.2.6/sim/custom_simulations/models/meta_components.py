from .battery import (
    component_models as battery_component_models,
)
from .boiler import (
    component_models as boiler_component_models,
)
from .building import (
    component_models as building_component_models,
)
from .combined_heat_power import (
    component_models as combined_heat_power_component_models,
)
from .cooling_chambers import (
    component_models as cooling_chambers_component_models,
)
from .demand import (
    component_models as demand_component_models,
)
from .distribution import (
    component_models as distribution_component_models,
)
from .ev import (
    component_models as ev_component_models,
)
from .group import (
    component_models as group_component_models,
)
from .heat_pump import (
    component_models as heat_pump_component_models,
)
from .heat_storage import (
    component_models as heat_storage_component_models,
)
from .power_grid import (
    component_models as grid_component_models,
)
from .pv import (
    component_models as pv_component_models,
)
from .utils import (
    component_models as utils_component_models,
)


component_models = {}
component_models.update(battery_component_models)
component_models.update(boiler_component_models)
component_models.update(building_component_models)
component_models.update(combined_heat_power_component_models)
component_models.update(cooling_chambers_component_models)
component_models.update(demand_component_models)
component_models.update(distribution_component_models)
component_models.update(ev_component_models)
component_models.update(grid_component_models)
component_models.update(heat_pump_component_models)
component_models.update(heat_storage_component_models)
component_models.update(pv_component_models)
component_models.update(group_component_models)
component_models.update(utils_component_models)