HTML_PREAMBLE = (
    "<!DOCTYPE html>\n"
    "<head>\n"
    "<title>My awesome experiment</title>"
    '<script src="https://unpkg.com/jspsych@7.3.1"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-html-keyboard-response@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-survey-text@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-survey-multi-choice@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-survey-likert@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-survey-likert@1.1.2"></script>\n'
    '<link href="https://unpkg.com/jspsych@7.3.1/css/jspsych.css" rel="stylesheet"'
    ' type="text/css"/>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-image-keyboard-response@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-video-keyboard-response@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych-contrib/plugin-rok@1.1.1"></script>\n'
    '<script src="https://unpkg.com/@jspsych-contrib/plugin-html-choice@1.0.0"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/sweetbean@0.0.6/dist/runtime-script.js"></script>\n'
    '<link href="https://cdn.jsdelivr.net/npm/sweetbean@0.0.6/dist/style/main.css" '
    'rel="stylesheet" type="text/css"/>\n'
    '<link href="https://cdn.jsdelivr.net/npm/sweetbean@0.0.6/dist/style/bandit.css" '
    'rel="stylesheet" type="text/css"/>\n'
    "</head>\n"
    "<body></body>\n"
    "<script>\n"
)
HTML_APPENDIX = "</script>\n</html>"

JSPSYCH = {"jspsych": "7.3.1"}

DEPENDENCIES = {
    "jsPsychHtmlKeyboardResponse": {"@jspsych/plugin-html-keyboard-response": "1.1.2"},
    "jsPsychSurveyText": {"@jspsych/plugin-survey-text": "1.1.2"},
    "jsPsychSurveyMultiChoice": {"@jspsych/plugin-survey-multi-choice": "1.1.2"},
    "jsPsychSurveyLikert": {"@jspsych/plugin-survey-likert": "1.1.2"},
    "jsPsychRok": {"'@jspsych-contrib/plugin-rok": "1.1.1"},
    "jsPsychImageKeyboardResponse": {
        "@jspsych/plugin-image-keyboard-response": "1.1.2"
    },
    "jsPsychVideoKeyboardResponse": {
        "@jspsych/plugin-video-keyboard-response": "1.1.2"
    },
    "jsPsychHtmlChoice": {"@jspsych-contrib/plugin-html-choice": "1.0.0"},
}

AUTORA_PREAMBLE = (
    "import 'jspsych/css/jspsych.css'\nconst main = async (id, condition) => {\n"
    "const jsPsych = initJsPsych()\n"
)

AUTORA_APPENDIX = (
    "await jsPsych.run(trials)\nconst observation = jsPsych.data.get()\n"
    "return await observation\n}\nexport default main\n"
)


def FUNCTION_PREAMBLE(is_async):
    async_string = ""
    if is_async:
        async_string = "async "
    return f"{async_string}function runExperiment() " + (
        "{\n" "document.body.style.backgroundColor = 'black';\n"
    )


def FUNCTION_APPENDIX(is_async):
    async_string = ""
    if is_async:
        async_string = "await "
    return (
        f"{async_string}jsPsych.run(trials)\nconst observation = jsPsych.data.get()\n"
        + f"return {async_string}observation\n"
        + "}"
    )


def TEXT_APPENDIX(is_async):
    async_string = ""
    if is_async:
        async_string = "await "
    return f"{async_string}jsPsych.run(trials)\n"
