from .core import KIMVVTestDriver
from .EquilibriumCrystalStructure.test_driver.test_driver import TestDriver as __EquilibriumCrystalStructure
from .ElasticConstantsCrystal.test_driver.test_driver import TestDriver as __ElasticConstantsCrystal


class EquilibriumCrystalStructure(__EquilibriumCrystalStructure, KIMVVTestDriver):
    pass


class ElasticConstantsCrystal(__ElasticConstantsCrystal, KIMVVTestDriver):
    pass


__all__ = [
    "EquilibriumCrystalStructure",
    "ElasticConstantsCrystal",
]
