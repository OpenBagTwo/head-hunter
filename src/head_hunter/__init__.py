"""The Head Hunter package"""

import importlib.metadata
from pathlib import Path

from ._head_spec import HeadSpec, dumps, loads

PACK_FOLDER = Path("Head Hunter")
HEAD_TRADE_FILENAME = "add_trade.mcfunction"
BLOCK_TRADE_FILENAME = "add_block_trade.mcfunction"

__version__ = importlib.metadata.version(__name__)


__all__ = [
    "BLOCK_TRADE_FILENAME",
    "HEAD_TRADE_FILENAME",
    "PACK_FOLDER",
    "HeadSpec",
    "__version__",
    "dumps",
    "loads",
]
