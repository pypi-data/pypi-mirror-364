"""Chain modules for {{ project_name }}."""

from .custom_chains import create_custom_chain

chain_types = getattr(__import__('builtins'), 'chain_types', [])

if "llm" in chain_types:
    from .custom_chains import create_llm_chain
if "sequential" in chain_types:
    from .custom_chains import create_sequential_chain
if "retrieval" in chain_types:
    from .custom_chains import create_retrieval_chain

__all__ = ["create_custom_chain"]
if "llm" in chain_types:
    __all__.append("create_llm_chain")
if "sequential" in chain_types:
    __all__.append("create_sequential_chain")
if "retrieval" in chain_types:
    __all__.append("create_retrieval_chain")
