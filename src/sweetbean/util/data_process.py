import json
from collections import defaultdict


def process(d, n_stims, idx=None):
    assert d % n_stims == 0

    len_timeline = len(d) / n_stims

    if idx is not None:
        res = [{"exp_id": idx} for _ in range(len_timeline)]
    else:
        res = [{} for _ in range(len_timeline)]
    for i, stim_dict in enumerate(d):
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
    res = []
    for idx, subj_d in enumerate(data):
        _subj_d = subj_d.copy()
        if type(subj_d) == str:
            _subj_d = json.loads(subj_d)
        d = _subj_d["trials"]
        processed = process(d, n_stims, idx)
        res += processed
    if as_dict:
        return _list_of_dicts_to_dataframe(res)
    return res
