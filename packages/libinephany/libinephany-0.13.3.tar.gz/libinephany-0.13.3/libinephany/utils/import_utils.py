# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import importlib
from types import ModuleType

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

WANDB = "wandb"

# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def try_to_import_module(module_name: str) -> ModuleType | None:
    """
    :param module_name: Module to try and import.
    :return: None or the imported module.
    """

    try:
        return importlib.import_module(module_name)

    except ImportError:
        return None


def try_import_wandb() -> ModuleType | None:
    """
    :return: None or the imported weights and biases module.
    """

    return try_to_import_module(module_name=WANDB)
