import json
from collections import defaultdict
from typing import Any, Iterable

import pandas as pd

DEFAULT_BOT_DETECTION_KEY = "bot_detection"


def process(stimulus_data, n_stims, idx=None):
    """
    Process list of stimulus to list of trials. For example, if the stimulus sequence is
    [Fixation, Text, Feedback] a list of all stimuli will be processed so that
    Fixation, Text and Feedback are bundled into one trial.
    Arguments:
        stimulus_data: the list of stimulus data
        n_stims: the number of stimuli in a sequence (3 in the above example)
    """
    if len(stimulus_data) % n_stims != 0:
        print("Stimulus data could not be processed.")
        return []

    len_timeline = len(stimulus_data) // n_stims

    if idx is not None:
        res = [{"exp_id": idx} for _ in range(len_timeline)]
    else:
        res = [{} for _ in range(len_timeline)]
    for i, stim_dict in enumerate(stimulus_data):
        stim_index = i % n_stims
        for k, v in stim_dict.items():
            new_key = f"{k}.{stim_index}"
            res[i // n_stims][new_key] = v
    return res


def _list_of_dicts_to_dataframe(data):
    col_dict = defaultdict(list)
    for row in data:
        for key, value in row.items():
            col_dict[key].append(value)
    return col_dict


def process_autora(data, n_stims, as_dict=True):
    """
    Process data when using AutoRA experiment runner (https://autoresearch.github.io/autora/)
    Arguments:
        data: the data to process
        n_stims: the number of stimuli in a sequence (3 in the above example)
        as_dict: whether to return a dictionary (can be used for pandas dataframe)
    """
    res = []
    for idx, subj_d in enumerate(data):
        try:
            _subj_d = subj_d
            if type(subj_d) == str:
                _subj_d = json.loads(subj_d)
            d = _subj_d["trials"]
            processed = process(d, n_stims, idx)
            res += processed
        except Exception as e:
            print(f"ERROR with: {subj_d}, {e}")
    if as_dict:
        _as_dict = {}
        try:
            _as_dict = _list_of_dicts_to_dataframe(res)
        except Exception as e:
            print(f"ERROR with: {res}, {e}")
        return _as_dict
    return res


# ---------------------------------------------------------------------------
# Online quality-control / participant-report pipeline.
#
# These helpers turn the raw observations returned by an autora firebase /
# firebase-prolific runner into:
#   1. a per-trial DataFrame (one row per trial, all subjects),
#   2. a per-subject quality report (one row per subject) with drop flags,
#   3. a (kept_trials, dropped_trials) split based on the report.
#
# They are deliberately experiment-agnostic: the caller picks which columns
# matter for their canonical schema and which response values count as valid
# choice-trial responses. The point is that any sweetbean experiment using
# this helper gets the same audit trail (incl. prolific_pid, bot-detection
# signals, single-key / strict-alternation / fast-RT checks) without
# re-implementing it.
# ---------------------------------------------------------------------------


def _normalize_observation_envelope(obs: Any) -> dict:
    """Normalise one item of an `observations` list into a uniform envelope.

    Accepted inputs:
        * A JSON string with ``{"trials": [...]}`` (the legacy
          firebase-runner shape).
        * A dict with at least a ``trials`` key.
        * A dict that wraps a string / dict observation under ``obs`` /
          ``observation`` plus optional ``prolific_pid`` / ``pId`` /
          ``slot_key`` siblings — the shape produced by the patched
          firebase-prolific runner that joins ``autora_meta.pId``.

    Returns a dict with keys ``trials`` (list), ``prolific_pid``
    (str | None), and ``slot_key`` (str | None).
    """
    if isinstance(obs, str):
        parsed = json.loads(obs)
        return {
            "trials": parsed.get("trials", []) if isinstance(parsed, dict) else [],
            "prolific_pid": None,
            "slot_key": None,
        }
    if isinstance(obs, dict):
        inner = obs.get("obs") or obs.get("observation")
        if inner is not None:
            if isinstance(inner, str):
                inner = json.loads(inner)
            trials = (
                inner.get("trials", []) if isinstance(inner, dict) else []
            )
            return {
                "trials": trials,
                "prolific_pid": obs.get("prolific_pid") or obs.get("pId"),
                "slot_key": obs.get("slot_key") or obs.get("key"),
            }
        return {
            "trials": obs.get("trials", []),
            "prolific_pid": obs.get("prolific_pid") or obs.get("pId"),
            "slot_key": obs.get("slot_key") or obs.get("key"),
        }
    raise TypeError(
        f"Unsupported observation type: {type(obs).__name__}"
    )


def _flatten_bot_detection(
    trial: dict, key: str = DEFAULT_BOT_DETECTION_KEY
) -> dict:
    """Flatten ``trial[key]`` (the BotDetection summary dict) into top-level
    ``<key>_<field>`` columns. One level of nested dicts (e.g.
    ``browser_flags``, ``rt_analysis``) is unfolded as
    ``<key>_<field>_<sub>``. The original nested dict is dropped.
    """
    bd = trial.get(key)
    if not isinstance(bd, dict):
        return trial
    out = {k: v for k, v in trial.items() if k != key}
    for k, v in bd.items():
        if isinstance(v, dict):
            for subk, subv in v.items():
                out[f"{key}_{k}_{subk}"] = subv
        else:
            out[f"{key}_{k}"] = v
    return out


def parse_autora_observations(
    observations: Iterable[Any],
    *,
    flatten_bot_detection: bool = True,
    bot_detection_key: str = DEFAULT_BOT_DETECTION_KEY,
) -> "pd.DataFrame":
    """Flatten autora-collected observations into a one-row-per-trial frame.

    `subject_id` is assigned by input order (0-indexed). `prolific_pid`
    and `slot_key` are pulled from the envelope when present (the patched
    firebase-prolific runner). `bot_detection.<field>` is unfolded to
    ``bot_detection_<field>`` columns when `flatten_bot_detection=True`
    (the default).

    No filtering is applied here — that is the job of
    :func:`participant_quality_report` + :func:`split_by_quality`.
    """
    rows: list[dict] = []
    for subject_id, obs in enumerate(observations):
        env = _normalize_observation_envelope(obs)
        for trial in env["trials"]:
            row = dict(trial)
            row["subject_id"] = subject_id
            row["prolific_pid"] = env["prolific_pid"]
            row["slot_key"] = env["slot_key"]
            if flatten_bot_detection:
                row = _flatten_bot_detection(row, key=bot_detection_key)
            rows.append(row)
    return pd.DataFrame(rows)


def _strict_alternation_rate(responses: list) -> float:
    """Fraction of consecutive flips in the response sequence.

    1.0 = strictly alternating (a,b,a,b,...). 0.0 = constant. Returns 0.0
    for sequences shorter than 2.
    """
    if len(responses) < 2:
        return 0.0
    flips = sum(
        1 for i in range(1, len(responses)) if responses[i] != responses[i - 1]
    )
    return flips / (len(responses) - 1)


def participant_quality_report(
    trials_df: "pd.DataFrame",
    *,
    subject_col: str = "subject_id",
    response_col: str = "bean_response",
    rt_col: str = "bean_rt",
    valid_responses: set | None = None,
    single_key_threshold: float = 0.95,
    min_mean_rt_ms: float = 1200.0,
    alternation_threshold: float = 0.95,
    drop_on_bot_flag: bool = True,
    drop_on_suspicious_browser: bool = True,
    drop_on_honeypot_filled: bool = True,
) -> "pd.DataFrame":
    """Per-subject quality report with drop flags.

    The report has one row per subject and includes ``prolific_pid`` /
    ``slot_key`` (when available on the trials frame) so that downstream
    code can pay every recruited participant — including those marked as
    `drop=True` — and correlate drops with their Prolific id.

    Drop signals (any one true → ``drop=True``, with the specific reason
    appended to ``drop_reason``):
        * suspicious_browser (BotDetection)
        * honeypot (BotDetection)
        * bot_flag (BotDetection composite)
        * single_key — `dominant_response_rate >= single_key_threshold`
        * fast_rt    — `mean_rt_ms < min_mean_rt_ms`
        * strict_alternation — `strict_alternation_rate >= alternation_threshold`

    `valid_responses`, if given, restricts response-based stats (single-key
    rate, alternation rate, mean RT) to trials whose `response_col` value is
    in the set — i.e. screens out instructions / consent / feedback rows.
    """
    columns = [
        subject_col, "prolific_pid", "slot_key",
        "n_trials", "n_valid_trials",
        "dominant_response", "dominant_response_rate",
        "strict_alternation_rate", "mean_rt_ms",
        "is_suspicious_browser", "honeypot_filled", "bot_flag",
        "focus_loss_count", "total_blur_duration_ms",
        "drop_suspicious_browser", "drop_honeypot", "drop_bot_flag",
        "drop_single_key", "drop_fast_rt", "drop_strict_alternation",
        "drop", "drop_reason",
    ]
    if trials_df.empty or subject_col not in trials_df.columns:
        return pd.DataFrame(columns=columns)

    rows: list[dict] = []
    for subject_id, sub in trials_df.groupby(subject_col, sort=True):
        n_trials = int(len(sub))
        if valid_responses is not None and response_col in sub.columns:
            valid = sub[sub[response_col].isin(valid_responses)]
        else:
            valid = sub
        n_valid = int(len(valid))

        if n_valid > 0 and response_col in valid.columns:
            counts = valid[response_col].value_counts(dropna=True)
            if not counts.empty:
                dominant_response = counts.index[0]
                dominant_response_rate = float(counts.iloc[0]) / max(1, n_valid)
            else:
                dominant_response = None
                dominant_response_rate = 0.0
            alt_rate = _strict_alternation_rate(list(valid[response_col].values))
        else:
            dominant_response = None
            dominant_response_rate = 0.0
            alt_rate = 0.0

        if rt_col in valid.columns and n_valid > 0:
            rts = pd.to_numeric(valid[rt_col], errors="coerce").dropna()
            mean_rt_ms = float(rts.mean()) if not rts.empty else None
        else:
            mean_rt_ms = None

        # BotDetection summary fields are cumulative — the last row has the
        # most up-to-date snapshot.
        last = sub.iloc[-1]
        is_susp = bool(last.get("bot_detection_is_suspicious_browser", False) or False)
        is_honeypot = bool(last.get("bot_detection_honeypot_filled", False) or False)
        is_bot_flag = bool(last.get("bot_detection_bot_flag", False) or False)
        focus_loss = int(last.get("bot_detection_focus_loss_count", 0) or 0)
        blur_ms = int(last.get("bot_detection_total_blur_duration_ms", 0) or 0)

        prolific_pid = None
        if "prolific_pid" in sub.columns:
            pids = sub["prolific_pid"].dropna().unique()
            if len(pids) > 0:
                prolific_pid = pids[0]
        slot_key = None
        if "slot_key" in sub.columns:
            sks = sub["slot_key"].dropna().unique()
            if len(sks) > 0:
                slot_key = sks[0]

        drop_susp = bool(drop_on_suspicious_browser and is_susp)
        drop_hp = bool(drop_on_honeypot_filled and is_honeypot)
        drop_bot = bool(drop_on_bot_flag and is_bot_flag)
        drop_single_key = dominant_response_rate >= float(single_key_threshold)
        drop_fast_rt = mean_rt_ms is not None and mean_rt_ms < float(min_mean_rt_ms)
        drop_alt = alt_rate >= float(alternation_threshold)

        reasons: list[str] = []
        if drop_susp: reasons.append("suspicious_browser")
        if drop_hp: reasons.append("honeypot")
        if drop_bot: reasons.append("bot_flag")
        if drop_single_key: reasons.append("single_key")
        if drop_fast_rt: reasons.append("fast_rt")
        if drop_alt: reasons.append("strict_alternation")

        rows.append({
            subject_col: subject_id,
            "prolific_pid": prolific_pid,
            "slot_key": slot_key,
            "n_trials": n_trials,
            "n_valid_trials": n_valid,
            "dominant_response": dominant_response,
            "dominant_response_rate": dominant_response_rate,
            "strict_alternation_rate": alt_rate,
            "mean_rt_ms": mean_rt_ms,
            "is_suspicious_browser": is_susp,
            "honeypot_filled": is_honeypot,
            "bot_flag": is_bot_flag,
            "focus_loss_count": focus_loss,
            "total_blur_duration_ms": blur_ms,
            "drop_suspicious_browser": drop_susp,
            "drop_honeypot": drop_hp,
            "drop_bot_flag": drop_bot,
            "drop_single_key": drop_single_key,
            "drop_fast_rt": drop_fast_rt,
            "drop_strict_alternation": drop_alt,
            "drop": bool(reasons),
            "drop_reason": ",".join(reasons),
        })

    return pd.DataFrame(rows, columns=columns)


def split_by_quality(
    trials_df: "pd.DataFrame",
    report_df: "pd.DataFrame",
    *,
    subject_col: str = "subject_id",
) -> tuple["pd.DataFrame", "pd.DataFrame"]:
    """Split `trials_df` into ``(kept, dropped)`` based on `report_df.drop`.

    The dropped frame gets a `drop_reason` column propagated from the
    report so per-trial audit records carry the reason for exclusion.
    """
    if (
        report_df.empty
        or "drop" not in report_df.columns
        or subject_col not in trials_df.columns
    ):
        return trials_df.copy(), trials_df.iloc[0:0].copy()
    dropped_subj = set(report_df.loc[report_df["drop"], subject_col].tolist())
    kept = trials_df[~trials_df[subject_col].isin(dropped_subj)].copy()
    dropped = trials_df[trials_df[subject_col].isin(dropped_subj)].copy()
    if not dropped.empty and "drop_reason" in report_df.columns:
        reason_map = (
            report_df.set_index(subject_col)["drop_reason"].to_dict()
        )
        dropped["drop_reason"] = dropped[subject_col].map(reason_map)
    return kept, dropped
