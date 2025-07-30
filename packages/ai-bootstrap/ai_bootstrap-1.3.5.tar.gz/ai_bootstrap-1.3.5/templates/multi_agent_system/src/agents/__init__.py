"""Agent modules for {{ project_name }}."""

from .supervisor import supervisor_node

# Dynamically import agent nodes if AGENT_NAMES is defined elsewhere
try:
    from .agent_names import AGENT_NAMES  # AGENT_NAMES should be a list of agent names as strings
except ImportError:
    AGENT_NAMES = []

for agent_name in AGENT_NAMES:
    module = __import__(f".{agent_name}", globals(), locals(), [f"{agent_name}_node"], 1)
    globals()[f"{agent_name}_node"] = getattr(module, f"{agent_name}_node")

__all__ = ["supervisor_node"] + [f"{name}_node" for name in AGENT_NAMES]
