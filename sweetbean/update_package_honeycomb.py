import json
import os
import shutil
import time


def update_package(dependencies, path, backup):
    if os.path.exists(path):
        with open(path, "r") as f:
            p_obj = json.load(f)
            for key in dependencies:
                p_obj["dependencies"][key] = dependencies[key]
            json_object = json.dumps(p_obj, indent=2)
            if backup:
                file_name, file_ext = os.path.splitext(os.path.basename(path))
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                if not os.path.exists("backup"):
                    os.mkdir("backup")
                new_file_name = f"backup/{file_name}_{timestamp}{file_ext}"
                shutil.copy(path, new_file_name)
            with open(path, "w") as f_out:
                f_out.write(json_object)


def get_import(dependency):
    for k in dependency:
        for k_ in dependency[k]:
            return f"import {k} from '{k_}'\n"
