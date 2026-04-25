"""Base class for experiment-level protections.

A ``Protection`` is a self-contained bundle of JS that the experiment
compilation embeds at well-defined points. The contract is intentionally
small so new protections (CAPTCHA, attention checks, fingerprinting, ...)
can be added without touching ``Experiment`` or stimulus internals.

Hook points, in the order they fire in the generated experiment:

1. :meth:`head_assets`  — extra HTML for ``<head>`` (only used by ``to_html``).
2. :meth:`runtime_js`   — JS embedded BEFORE ``initJsPsych``. Use to inline a
                          library (e.g. ``BotDetection`` IIFE) so it is in
                          scope by the time the experiment starts.
3. :meth:`init_js`      — JS run AFTER ``initJsPsych`` exists but before
                          trials start. Typical use: call ``Lib.initialize()``
                          and register global handlers.
4. :meth:`on_load_for_stimulus` / :meth:`on_finish_for_stimulus`
                        — per-trial JS injected into each stimulus's
                          ``on_load`` / ``on_finish`` callbacks. ``data`` is
                          in scope inside ``on_finish`` (it's the trial row).
5. :meth:`summary_js`   — JS expression returning a summary object. The
                          experiment wraps it in
                          ``jsPsych.data.addProperties({<name>: <expr>})``
                          so the result lands on every saved row.

Subclasses override only the hooks they need. The default implementations
return empty strings (no-op), so a minimal ``Protection`` adds nothing.
"""


class Protection:
    """Base class — see module docstring for the hook contract."""

    name: str = "protection"

    def head_assets(self) -> str:
        """Extra HTML injected into ``<head>``. Used by ``Experiment.to_html``."""
        return ""

    def runtime_js(self) -> str:
        """JS source emitted before ``initJsPsych``. Typically the protection
        library (IIFE) being inlined into the page."""
        return ""

    def init_js(self) -> str:
        """JS source run after ``initJsPsych`` but before trials run. Typical
        use: call the library's ``initialize`` and register global handlers."""
        return ""

    def summary_js(self) -> str:
        """JS expression that evaluates to a summary object. Empty disables.
        Wired into the experiment's ``on_finish`` so it lands on every row of
        saved data via ``jsPsych.data.addProperties``."""
        return ""

    def on_load_for_stimulus(self, stimulus) -> str:
        """Per-trial JS injected into the stimulus's ``on_load`` callback.

        Return ``""`` to no-op for this stimulus type. Implementations may
        inspect ``stimulus`` (e.g. ``isinstance``) to specialize.
        """
        return ""

    def on_finish_for_stimulus(self, stimulus) -> str:
        """Per-trial JS injected into the stimulus's ``on_finish`` callback.

        ``data`` is in scope and refers to the trial's data row — mutate it
        directly to attach per-trial signals.
        """
        return ""
