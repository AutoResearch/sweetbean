def define_env(env):
    @env.macro
    def include_file(file_path):
        with open(file_path, "r") as file:
            return file.read()
