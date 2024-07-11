"""The Head Hunter package"""

from pathlib import Path

from ._head_spec import HeadSpec, dumps, loads

PACK_FOLDER = Path("Head Hunter")
HEAD_TRADE_FILENAME = "add_trade.mcfunction"
BLOCK_TRADE_FILENAME = "add_block_trade.mcfunction"


__all__ = [
    "HeadSpec",
    "dumps",
    "loads",
    "PACK_FOLDER",
    "HEAD_TRADE_FILENAME",
    "BLOCK_TRADE_FILENAME",
]
