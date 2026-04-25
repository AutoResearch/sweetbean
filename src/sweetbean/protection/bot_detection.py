"""Bot/agent detection protection.

Wraps ``assets/bot-detection.js`` (a self-contained IIFE that exposes a
``BotDetection`` global) and wires it into the SweetBean compile flow:

* :meth:`runtime_js`  — inlines the IIFE so ``window.BotDetection`` exists
                        before ``initJsPsych`` runs.
* :meth:`init_js`     — calls ``BotDetection.initialize`` and (optionally)
                        installs a single document-level ``input`` listener
                        that records every range-slider move. This removes
                        the need for a per-stimulus mixin: any ``<input
                        type="range">`` (jsPsych's slider plugin or any
                        custom slider) is automatically tracked.
* :meth:`on_load_for_stimulus`   — resets per-trial slider tracking.
* :meth:`on_finish_for_stimulus` — feeds the trial RT into the cumulative
                                   buffer and merges per-trial slider stats
                                   + the running bot-detection summary into
                                   the data row.
* :meth:`summary_js`  — emits ``BotDetection.getSummary()`` so the
                        experiment's ``on_finish`` adds the full summary to
                        every saved row via ``jsPsych.data.addProperties``.
"""

from pathlib import Path

from sweetbean.protection.protection import Protection

_ASSET_PATH = Path(__file__).parent / "assets" / "bot-detection.js"


class BotDetection(Protection):
    """Bot/agent detection layer."""

    name = "bot_detection"

    def __init__(
        self,
        enable_countermeasures: bool = True,
        track_sliders: bool = True,
    ):
        """
        Arguments:
            enable_countermeasures: when False, only passive logging runs —
                no honeypot DOM, no clipboard/devtools blocking, no inline
                traps. Useful for pilots / debugging.
            track_sliders: when True, install a document-level ``input``
                listener that calls ``BotDetection.recordSliderMove()`` for
                every range slider, so per-trial slider stats are captured
                without modifying any stimulus class.
        """
        self.enable_countermeasures = enable_countermeasures
        self.track_sliders = track_sliders

    def runtime_js(self) -> str:
        return _ASSET_PATH.read_text(encoding="utf-8")

    def init_js(self) -> str:
        cm = "true" if self.enable_countermeasures else "false"
        js = f"BotDetection.initialize({cm});"
        if self.track_sliders:
            js += (
                "document.addEventListener('input',function(e){"
                "if(e.target&&e.target.type==='range'){"
                "if(window.BotDetection){BotDetection.recordSliderMove();}}"
                "},true);"
            )
        return js

    def summary_js(self) -> str:
        return "BotDetection.getSummary()"

    def on_load_for_stimulus(self, stimulus) -> str:
        return "if(window.BotDetection){BotDetection.resetTrialTracking();}"

    def on_finish_for_stimulus(self, stimulus) -> str:
        return (
            "if(window.BotDetection){"
            "if(typeof data.rt==='number'){BotDetection.addRT(data.rt);}"
            "Object.assign(data,BotDetection.getTrialInteractionData());"
            "Object.assign(data,BotDetection.getTrialLevelSummary());"
            "}"
        )
