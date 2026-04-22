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
