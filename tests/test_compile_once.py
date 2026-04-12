"""Tests for Experiment.compile / to_js_string_from_template — compile once, swap timelines."""

from sweetbean.block import Block
from sweetbean.experiment import Experiment
from sweetbean.stimulus import Text
from sweetbean.variable import TimelineVariable


def _make_experiment(timelines):
    """Build an experiment with a single stimulus type, one block per timeline list."""
    stimulus = Text(text=TimelineVariable("word"))
    blocks = [Block([stimulus], tl) for tl in timelines]
    return Experiment(blocks)


def test_compile_returns_template_and_placeholder():
    """compile() should return a JS string with a recognizable timeline placeholder."""
    timelines = [[{"word": "hello"}, {"word": "world"}]]
    exp = _make_experiment(timelines)
    template = exp.compile(as_function=True, is_async=True)
    assert isinstance(template, str)
    assert "runExperiment" in template
    assert "TIMELINE_PLACEHOLDER_" in template


def test_to_js_string_from_template_matches_original():
    """Output of to_js_string_from_template must produce identical JS to to_js_string."""
    timelines_a = [[{"word": "a1"}, {"word": "a2"}], [{"word": "a3"}]]
    timelines_b = [[{"word": "b1"}, {"word": "b2"}], [{"word": "b3"}]]

    exp_a = _make_experiment(timelines_a)
    exp_b = _make_experiment(timelines_b)

    original_a = exp_a.to_js_string(as_function=True, is_async=True)
    original_b = exp_b.to_js_string(as_function=True, is_async=True)

    template = exp_a.compile(as_function=True, is_async=True)

    rebuilt_a = exp_a.to_js_string_from_template(template, timelines_a)
    rebuilt_b = exp_b.to_js_string_from_template(template, timelines_b)

    assert rebuilt_a == original_a
    assert rebuilt_b == original_b


def test_compile_is_faster_than_repeated_to_js_string():
    """to_js_string_from_template should skip the expensive per-block compile step."""
    import time

    n_subjects = 3
    per_subject = [{"word": f"w{i}"} for i in range(10)]
    all_timelines = [per_subject for _ in range(n_subjects)]

    experiments = [_make_experiment([tl]) for tl in all_timelines]

    t0 = time.perf_counter()
    for exp in experiments:
        exp.to_js_string(as_function=True, is_async=True)
    slow_elapsed = time.perf_counter() - t0

    template = experiments[0].compile(as_function=True, is_async=True)
    t0 = time.perf_counter()
    for tl in all_timelines:
        experiments[0].to_js_string_from_template(template, [tl])
    fast_elapsed = time.perf_counter() - t0

    assert fast_elapsed < slow_elapsed, (
        f"template path ({fast_elapsed:.4f}s) should be faster than "
        f"full compile ({slow_elapsed:.4f}s)"
    )


def test_template_reuse_across_different_block_counts():
    """Template built from 2 blocks should work with 2 different timeline lists."""
    tl1 = [{"word": "x"}, {"word": "y"}]
    tl2 = [{"word": "z"}]
    exp = _make_experiment([tl1, tl2])

    template = exp.compile(as_function=True, is_async=True)

    new_tl1 = [{"word": "p"}, {"word": "q"}]
    new_tl2 = [{"word": "r"}]
    result = exp.to_js_string_from_template(template, [new_tl1, new_tl2])

    assert "[{'word': 'p'}, {'word': 'q'}]" in result or '{"word": "p"}' in result or "p" in result
    assert "x" not in result
    assert "y" not in result
