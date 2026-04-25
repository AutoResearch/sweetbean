"""Module-level context for the currently-active protections during JS generation.

Stimulus-level hooks (``_BaseStimulus._on_load_js`` / ``to_js``) consult this
during compilation so each trial's ``on_load`` and ``on_finish`` callbacks can
embed protection-specific JS (e.g. per-trial slider tracking, inline traps).

``Experiment`` sets the active protections immediately before generating
stimulus JS and clears them in a ``finally`` so a partial compile never leaks
state into a later one.
"""

from typing import List

_active_protections: List = []


def get_active_protections() -> List:
    return list(_active_protections)


def set_active_protections(protections) -> None:
    global _active_protections
    _active_protections = list(protections) if protections else []
