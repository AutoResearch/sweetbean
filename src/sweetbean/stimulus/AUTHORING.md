# Authoring SweetBean Stimuli

> **Read this file before adding a new stimulus class to
> `sweetbean/stimulus/`.** It captures the non-obvious rules that make
> Sweetbean stimuli compile to working browser JavaScript, plus the
> patterns the existing stimuli rely on.

A stimulus is the smallest unit of an experiment timeline: it renders
something in the browser via jsPsych and (optionally) collects a
response. Every stimulus extends one of the bases in
`Stimulus.py` (`_BaseStimulus`, `_KeyboardResponseStimulus`, etc.) or a
concrete shipped stimulus (e.g. `HtmlKeyboardResponse`).

This document is for the Python-to-JS boundary. For the runtime
semantics of jsPsych itself, see the jsPsych docs.

## Mental model: where does each line of your stimulus run?

Sweetbean stimuli straddle two execution environments:

| When                                  | Where                | What runs                                                                                                                                                       |
| ------------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MyStimulus(...)` constructor         | Python, build time   | Anything you do in `__init__` — full Python, full module imports, `self`. Use this to pre-compute strings, validate args, build helpers.                        |
| `to_js()` / `Experiment.to_html(...)` | Python, build time   | Sweetbean walks `self.arg`, JSON-serializes literals via `_var_to_js`, and **transpiles `FunctionVariable` callables to JavaScript** via Transcrypt.            |
| Trial render                          | Browser, runtime     | jsPsych invokes the per-trial config. `()=>{ let stimulus=...; return stimulus }` runs in the browser. **Anything reachable from a `FunctionVariable` is JS.** |
| Trial finish                          | Browser, runtime     | `on_finish:(data)=>{...}` runs in the browser; this is also generated JS and stores `bean_<arg>` keys into the trial data.                                      |

The mental rule: **the body of every callable you hand to a
`FunctionVariable` ends up running in the browser as transpiled JS,
not in Python.** Treat it as JavaScript-with-Python-syntax.

## The Transcrypt rules (where most bugs come from)

Sweetbean uses Transcrypt to compile `FunctionVariable` callables to
JS. The rules are:

### 1. No module-level references inside the function

Anything the function looks up via `func.__globals__` (other functions
in the same module, module-level constants, imported names, classes)
**will not be available in the browser**. The browser sees the
literal name and throws `ReferenceError: foo is not defined` at trial
time.

`_fct_to_js` *tries* to reject this at build time, but its check only
inspects the outer function's `co_names` — see footgun #1 below.

Allowed inside the function:

- Pure literals (numbers, strings, lists, dicts, tuples).
- f-strings (compiled to template literals).
- `if/else`, conditional expressions.
- Arithmetic, comparisons, `and`/`or`, `not`.
- `len()`, indexing (`x[0]`), list comprehensions.
- A small allowlist of stdlib modules in `NON_LOCAL_INCLUDES`
  (`math`, `random`, `numpy`, `pandas`, `datetime`, `time`, `re`,
  `os`, `sys`, `json`, `csv`).
- `TouchButton` instances (special-cased).

Not allowed inside the function:

- `self.<anything>` — `self` is a Python concept that doesn't exist
  in the transpiled JS.
- Helper functions defined in the same module (e.g. `render_foo_html`).
- Module-level constants (e.g. `FEATURE_NAMES`). Inline the literal,
  or pass it as a `FunctionVariable` arg.
- Anything imported from another package other than the allowlisted
  modules.

### 2. Pass dependencies as `FunctionVariable` args, not via globals

This is the workaround for rule #1. If a function needs values that
are only known at build time, pass them as args:

```python
# Bad — depends on module-level constant
EXPERTS = (0.9, 0.8, 0.7, 0.6)

def _trial_html(ratings):
    return f"Expert ({EXPERTS[0]*100}%)"  # EXPERTS undefined in browser

stimulus = FunctionVariable("s", _trial_html, [TimelineVariable("ratings")])

# Good — pass the constant in as a literal arg
def _trial_html(ratings, validities_pct):
    return f"Expert ({validities_pct[0]}%)"

stimulus = FunctionVariable(
    "s",
    _trial_html,
    [TimelineVariable("ratings"), [90, 80, 70, 60]],
)
```

Literal lists/tuples/dicts passed as args are JSON-serialized into the
generated JS, so they survive the transpile.

### 3. Operators are lowered to `__add__`, `__mul__`, etc.

Sweetbean's AST transformer rewrites `a + b` to `__add__(a, b)` so
that Python's overloading semantics work in JS. This is invisible
when it works, but if you stare at the generated JS it explains the
`__add__(i, 1)` you'll see.

## Two recommended patterns for trial-varying HTML

### Pattern A: pre-render in Python, pass as a string `TimelineVariable`

If you can compute the full HTML for every trial at build time
(common — you usually know all trial parameters when building the
timeline), this is the simplest, safest pattern. No Transcrypt at
all.

```python
def build_timeline(trials):
    timeline = []
    for t in trials:
        timeline.append({
            "trial_html": render_my_stimulus(t),  # full Python, any helpers
            "option_a": t.option_a,                # also kept on each row
            "option_b": t.option_b,
        })
    return timeline

stim = HtmlKeyboardResponse(
    stimulus=TimelineVariable("trial_html"),
    choices=["f", "j"],
    correct_key="",
)
# Promote option_a / option_b into the trial data so the analysis side can
# read bean_option_a / bean_option_b. See "Promoting fields into trial data"
# below.
stim.arg["option_a"] = TimelineVariable("option_a")
stim.arg["option_b"] = TimelineVariable("option_b")
```

Use this whenever you can. If the only thing that varies per trial is
the HTML, you don't need a `FunctionVariable` at all.

### Online runner payload rule (Firebase / Firestore)

When experiments are uploaded through Firebase-backed runners, every
trial's data row is concatenated into a single observation document.
Firestore caps documents at ~1 MB; long timelines with rich rendered
HTML can blow past that. The fix is to keep trial data rows compact:

- Keep timeline rows to compact trial parameters only (the canonical
  fields you also need for decoding / metrics).
- Prefer rendering rich trial HTML at runtime from those parameters via
  a literals-only `FunctionVariable` (Pattern B).
- For long-timeline stimuli where the rendered HTML is fully
  reconstructible from the trial params (true for almost everything that
  subclasses `HtmlKeyboardResponse` and supplies its own param-driven
  renderer), **drop `stimulus` from the saved trial data** with the
  built-in helper:

  ```python
  trial_stim = HtmlKeyboardResponse(stimulus=..., choices=...)
  trial_stim.skip_data("stimulus")  # see §"Suppressing fields from trial data"
  ```

- For raw `HtmlKeyboardResponse(stimulus="<custom html>")` (consent,
  instructions, debriefs — usually one trial each), leave `stimulus` in
  the data. The HTML is the only record there, and one trial's worth of
  HTML is a few KB, not the bloat source.

This preserves participant-facing UI while keeping uploaded observation
payloads small.

### Pattern B: literals-only `FunctionVariable`

Use this when the rendering must run in the browser (depends on
runtime-resolved variables like `DataVariable` / `SharedVariable`, or
on a value computed by another `FunctionVariable`).

The reference is `DefaultCategoryLearning.py::_feature_vector_to_html`,
which has the comment

> `# Literals only — Transcrypt rejects non-local globals (FunctionVariable / _fct_to_js).`

at the top. Follow that pattern: a single flat function with only
literals, conditionals, indexing, and f-strings. Do not call out to
helpers in the same module.

## Promoting fields into trial data (`bean_<key>`)

Sweetbean's `_params_to_js` emits, in `on_finish(data)`, a
`let <key>=...; data["bean_<key>"]=<key>;` for **every key in
`self.arg`** (whether or not the key is also a body-level config key
like `stimulus` / `choices`). That's how `bean_response_time`,
`bean_stimulus`, `bean_choices` end up on the trial.

To put extra fields on the trial — e.g. the raw structured value
underlying a pre-rendered `trial_html`, so analysis code can read it
back — add them to `self.arg` after `super().__init__`:

```python
class MyStimulus(HtmlKeyboardResponse):
    def __init__(self, *, option_a, option_b, ...):
        ...
        super().__init__(stimulus=..., choices=..., correct_key="")
        self.arg.update({
            "option_a": option_a,  # may be a TimelineVariable / list / dict
            "option_b": option_b,
        })
```

These show up in jsPsych data as `bean_option_a` / `bean_option_b`
and are available to `_observations_to_df`. **Do not** also write
them into `self.arg_js`; that would (incorrectly) emit them as
top-level jsPsych config keys.

## Auto-fit to viewport (`fit_to_viewport`)

Every stimulus inherits a class-level `fit_to_viewport: bool = True`
flag (see `Stimulus.py::_BaseStimulus`). When `True`, the trial config
emits an `on_load` callback that calls `window.__sb_fit__(true)`, which
CSS-`zoom`s `#jspsych-content` so it fills (but never overflows) the
viewport, with the body's overflow set to `hidden`. The scale factor
is clamped to `[0.4, 2.5]` — large content shrinks to fit, small
content grows up to a "reasonable large" cap. A debounced window-resize
listener re-fits on browser resize.

When `False`, the callback calls `window.__sb_fit__(false)`, which
clears any prior zoom and restores `body { overflow: auto }` so the
trial scrolls naturally. **Use `False` for text-heavy screens that may
exceed one viewport** — `InformedConsent` ships with
`fit_to_viewport = False` for exactly this reason.

Three ways to set the flag:

1. **Class default** (most common). Set the class attribute on a
   subclass so every instance opts in/out:
   ```python
   class InformedConsent(HtmlKeyboardResponse):
       fit_to_viewport = False
   ```
2. **Per-instance kwarg.** Stimuli that expose `fit_to_viewport` in
   their `__init__` (currently `HtmlKeyboardResponse` and everything
   that passes through it) accept `fit_to_viewport=True/False/None`
   directly. `None` means "use the class default".
   ```python
   stim = HtmlKeyboardResponse(stimulus="...", fit_to_viewport=False)
   ```
3. **Post-construction.** Any stimulus instance:
   ```python
   stim.fit_to_viewport = False
   ```

The flag is intentionally **not** part of `self.arg`, so it never
leaks into trial data as `bean_fit_to_viewport`.

When you author a new stimulus, decide:

- Pure visual / fixed-size content (Gabors, choice cards, ratings) →
  default (`True`) is right; users get auto-fit for free.
- Long-form text (consent, debriefs, multi-screen instructions where
  scrolling is intended) → override the class attribute to `False`.
- Mixed: prefer the default and let users override per-instance when
  needed.

Mechanism notes (debugging):

- Uses CSS `zoom`, not `transform: scale`. Zoom changes the layout
  box (so flex/center parents see the new size); scale only changes
  paint. We picked zoom so jsPsych's centering still works after
  shrinking/growing the content.
- The fit fires on every trial's `on_load`. Even a `fit_to_viewport
  = False` stimulus emits the callback (with `false`) so transitions
  from a fit trial back to a no-fit trial cleanly clear the prior
  zoom and re-enable scrolling.
- If you set inline overflow styles on `body` from your stimulus
  HTML, the auto-fit will fight them. Don't.

## Minimum response time (`min_rt`)

Every stimulus inherits a class-level `min_rt: int = 0` (ms) on
`_BaseStimulus`. When `> 0`, the trial's `on_load` callback installs a
**document-level capturing** `keydown` listener that calls
`event.stopImmediatePropagation()` + `event.preventDefault()` for the
first `min_rt` ms after the stimulus renders, then removes itself via
`setTimeout`. Because the listener runs in the capture phase, it fires
*before* jsPsych's `getKeyboardResponse` listener (which is registered
on bubble), so no plugin sees those keys at all — the trial cannot end
until the gate elapses, regardless of which html-keyboard-response
plugin version is loaded.

While the gate is active, the same `on_load` also paints a small
**visual indicator** so the participant can tell *why* their keys
aren't doing anything:

* The trial content (`#jspsych-content`, falling back to `<body>`) is
  smoothly dimmed to `opacity:0.7;filter:saturate(0.5)` (still
  readable, clearly muted).
* A thin colored bar fixed at the bottom of the viewport
  (`data-sb-min-rt-bar="1"`, default `#6a90c0`) animates from 0% →
  100% width over exactly `min_rt` ms via CSS `transition`.

When the gate releases, the bar is removed and the original
`opacity` / `filter` / `transition` values are restored. To re-skin
the bar, target `[data-sb-min-rt-bar]` from your own stylesheet — the
attribute is stable across versions; the inline styles are not.

Use cases:

- Cheap guardrail against a participant single-key spamming through
  an entire timeline (Prolific quality control).
- Make sure the participant has at least glanced at the stimulus
  before they can answer (when no real "stimulus duration" makes
  sense).

Three ways to set it (mirrors `fit_to_viewport`):

1. **Class default** on a subclass:
   ```python
   class MyChoice(HtmlKeyboardResponse):
       min_rt = 600
   ```
2. **Per-instance kwarg** on stimuli that expose it
   (`HtmlKeyboardResponse(... , min_rt=800)`). `None` means "use the
   class default"; negative or non-numeric values clamp to 0.
3. **Post-construction**: `stim.min_rt = 800`.

The value is **not** stored in `self.arg`, so it never leaks into
trial data as `bean_min_rt`. It is also not part of `save_trial_parameters`.

Notes:

- The gate only blocks keyboard advance. Mouse, focus, and scroll
  events are unaffected — touchscreen-button extensions or click-
  based plugins are not gated by `min_rt`. Add a separate gate for
  those if you need it.
- Don't combine `min_rt` with `trial_duration < min_rt`: the trial
  will time out before the gate releases and the participant will
  never get a chance to respond. Sweetbean does not currently
  cross-check these.
- The participant should be told about the gate in the instructions
  (otherwise the locked first ~half-second reads as "broken keys").
  See `src/heuristic_decision_making/experiment.py:_render_instructions_html`
  for an example of conditional instruction copy.

## Cardinal rating displays (`sweetbean.util.rating`)

`sweetbean.util.rating` ships small **build-time** HTML helpers for
displaying cardinal-scale ratings (e.g. an expert score from 0–7).
Use them when a row of "pips" (one filled circle per integer) becomes
visually noisy — typically anywhere `rating_max` exceeds ~4.

API:

- `rating_bar_html(value, max_value, ...)` — single horizontal bar
  whose fill width = `value / max_value`, plus an optional `<value>/<max>`
  numeric label. Sensible dark-mode defaults; everything is overridable.
- `rating_row_html(label, value, max_value, ...)` — `[label] [bar] [num]`
  row, suitable for stacking inside a card.
- `rating_card_html(title, rows_html, ...)` — bordered card with a
  title, around a stack of `rating_row_html` outputs.
- `rating_card_from_values_html(title, labels, values, max_value, ...)` —
  one-liner that composes the above directly from parallel iterables.

These are **Python-time only** (Pattern A — pre-render in Python and
ship as a string). Do **not** import them inside a `FunctionVariable`
callable: those callables are transpiled to JavaScript by Transcrypt,
which cannot follow the import. If your trial render is in JS-land
(Pattern B), inline the bar markup directly — the body of
`rating_bar_html` is small and copy/paste-friendly. The HDM trial
render in `src/heuristic_decision_making/experiment.py` does exactly
this and shares only the visual conventions with the helper.

## Footguns

1. **Closure scope hides non-locals from the build-time check.**
   `_fct_to_js` calls `func.__code__.co_names` to find module-level
   refs. Names accessed only inside an inner function (a closure
   nested in your `FunctionVariable` callable) are in
   `inner.__code__.co_names` and never inspected. The check passes,
   Transcrypt emits a literal name reference, and the browser throws
   `ReferenceError` at trial time. **Mitigation:** never use nested
   functions inside a `FunctionVariable` callable — keep it flat. If
   you need a helper, either inline it or use Pattern A.
2. **`self` is not available.** Even if you pass `self` to
   `FunctionVariable` args, attribute access is fine in Python but
   fails in JS (no `__getattr__` semantics). Pass the *value* you
   need, not `self`.
3. **`int(x)` and `str(x)` work; most other builtins do not.** Stick
   to the very small set you can confirm by searching the existing
   transpiled stimuli.
4. **`.format()` is post-processed, but only for simple cases.** F-
   strings are safer.
5. **`bean_*` collisions.** If you add a key to `self.arg` whose
   name already collides with a built-in field (`stimulus`,
   `choices`, `correct_key`, `type`, `duration`, `response`, `rt`),
   you'll overwrite or shadow the framework's own field. Pick
   distinct names.
6. **Pre-rendered HTML balloons the timeline.** Pattern A serializes
   the HTML once per trial into the `<script>` block in
   `experiment.html`. For long timelines with rich HTML this can mean
   a multi-MB HTML file. Acceptable for typical (≤200 trial) studies;
   if it isn't, fall back to Pattern B with a literals-only
   `FunctionVariable`.
7. **Multi-line strings as stimulus params.** Sweetbean serializes
   string params as a single-quoted JS literal (`'...'`).
   `_var_to_js` now escapes `\n`, `\r`, `\\`, `'`, U+2028 and U+2029
   so multi-line HTML/CSS payloads compile to valid JS — but if you
   ever bypass `_var_to_js` (for example, building your own raw JS
   into `js_body`), do the same escaping yourself or you'll get
   `Uncaught SyntaxError: Invalid or unexpected token` at trial start
   in the browser. The regression net is
   `scripts/_check_stim_js_syntax.py` in autopi: it parses every
   timeline stimulus through `node --check`.

## Authoring checklist

Before you declare a new stimulus done:

- [ ] Does it subclass an existing base (`HtmlKeyboardResponse`,
      `_KeyboardResponseStimulus`, `_BaseStimulus`)?
- [ ] Does the constructor call `super().__init__(...)` correctly?
- [ ] If you used a `FunctionVariable`, is the callable
      **flat** (no nested defs) and does its body reference only
      literals + its own parameters + the allowlisted modules?
- [ ] Are extra trial fields promoted via `self.arg.update({...})`
      with non-colliding names?
- [ ] Did you export the new class from
      `sweetbean/stimulus/__init__.py`?
- [ ] Did you smoke-test by generating an `experiment.html`,
      opening it in a browser, completing one trial, and checking
      the JS console for `ReferenceError`s?
- [ ] Did you confirm the downloaded data JSON contains the
      `bean_*` keys you expected?
- [ ] If you intend the stimulus to be used in language-model
      simulations, did you set `l_template` and (if response-bearing)
      `response_template`?

If a checkbox can't be ticked, write down why in the PR / progress
doc — silent gaps are how the closure-scope footgun above bit us in
the first place.

## Reference stimuli to study

- `HtmlKeyboardResponse.py` — the simplest non-trivial stimulus.
  Read this first.
- `DefaultCategoryLearning.py` — the canonical "literals-only
  `FunctionVariable`" pattern, including the
  `self.arg.update({"feature_vector": ..., "feature_description": ...})`
  trick for promoting fields into trial data.
- `RatingResponse.py` — pre-renderable rating widget; the
  `render_rating_html` helper is the **Python-time** API and must
  not be referenced from inside a `FunctionVariable`.
