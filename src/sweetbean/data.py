def process_js(js_data):
    res = []
    for d in js_data:
        res_dict = {}
        for key, value in d.items():
            if key in ["rt", "stimulus", "type"]:
                res_dict[key] = value
            if key.startswith("bean_"):
                res_dict[key[5:]] = value
        res.append(res_dict)
    return res
