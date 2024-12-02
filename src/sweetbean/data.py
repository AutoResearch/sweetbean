def process_js(js_data):
    """
    Process the data from a SweetBean generated jsPsych experiment.
    """
    res = []
    for d in js_data:
        res_dict = {}
        for key, value in d.items():
            if key in ["rt", "stimulus", "type", "response"]:
                res_dict[key] = value
            if key.startswith("bean_"):
                res_dict[key[5:]] = value
        res.append(res_dict)
    return res


def get_n_responses(data):
    """
    Get the number of responses in the data.
    """
    n = 0
    for d in data:
        if "response" in d and d["response"] is not None:
            n += 1
    return n


def until_response(data, n):
    """
    Get the data until the nth response.
    (This is helpful, for example, to get the data up a certain point
    and then run the rest of the experiment with `run_on_language`)
    """
    i = 0
    for idx, d in enumerate(data):
        if "response" in d and d["response"] is not None:
            i += 1
        if i > n:
            return data[:idx]
