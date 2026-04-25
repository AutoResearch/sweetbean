"""Pluggable protections (bot/agent detection, ...) for SweetBean experiments.

Pass instances to :class:`sweetbean.Experiment` via ``protections=[...]``.
See :mod:`sweetbean.protection.protection` for the hook contract.
"""

from sweetbean.protection.bot_detection import BotDetection
from sweetbean.protection.protection import Protection

__all__ = ["BotDetection", "Protection"]
