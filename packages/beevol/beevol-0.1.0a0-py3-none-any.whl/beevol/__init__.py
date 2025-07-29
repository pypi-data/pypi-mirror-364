from .hive import DEFAULT_CONFIG
from .swarm import sting

# backwards compatibility for older tests/code
bee_swarm = sting

__all__ = ["sting", "bee_swarm", "DEFAULT_CONFIG"]
