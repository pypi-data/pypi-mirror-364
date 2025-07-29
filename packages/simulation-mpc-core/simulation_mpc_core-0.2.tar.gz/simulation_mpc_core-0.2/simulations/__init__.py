from .custom_simulations.models import *
from .custom_simulations import *
import os


new_path = os.path.join(os.path.dirname(__file__), "Cbc-refactor-win64-msvc14-mt", "bin")

current_path = os.environ.get('PATH', '')

if new_path not in current_path:
    os.environ['PATH'] += f";{new_path}"
