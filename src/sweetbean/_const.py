HTML_PREAMBLE = (
    "<!DOCTYPE html>\n"
    "<head>\n"
    "<title>My awesome experiment</title>\n"
    "<!-- Serve this file over http(s); opening via file:// often breaks video/media. -->\n"
    '<script src="https://unpkg.com/jspsych@7.3.1"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-html-keyboard-response@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-survey-text@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-survey-multi-choice@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-survey-likert@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-html-slider-response@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-survey-likert@1.1.2"></script>\n'
    '<link href="https://unpkg.com/jspsych@7.3.1/css/jspsych.css" rel="stylesheet"'
    ' type="text/css"/>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-image-keyboard-response@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych/plugin-video-keyboard-response@1.1.2"></script>\n'
    '<script src="https://unpkg.com/@jspsych-contrib/plugin-rok@1.1.1"></script>\n'
    '<script src="https://unpkg.com/@jspsych-contrib/plugin-html-choice@1.0.0"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/sweetbean@0.0.6/dist/runtime-script.js"></script>\n'
    '<script src="https://unpkg.com/@sweet-jspsych/plugin-rsvp@0.2.5/dist/index.browser.min.js">'
    "</script>\n"
    '<script src="https://unpkg.com/@sweet-jspsych/plugin-symbol@0.4.6/dist/index.browser.min.js">'
    "</script>\n"
    "<script "
    'src="https://unpkg.com/@sweet-jspsych/plugin-foraging@0.2.1/dist/index.browser.min.js">'
    "</script>\n"
    "<script "
    'src="https://unpkg.com/@sweet-jspsych/plugin-gabor-array@0.1.1/dist/index.browser.min.js">'
    "</script>\n"
    '<link href="https://cdn.jsdelivr.net/npm/sweetbean@0.0.6/dist/style/main.css" '
    'rel="stylesheet" type="text/css"/>\n'
    '<link href="https://cdn.jsdelivr.net/npm/sweetbean@0.0.6/dist/style/bandit.css" '
    'rel="stylesheet" type="text/css"/>\n'
    "<style>\n"
    "html,body{height:100%;margin:0;overflow:hidden;}\n"
    "/* Slider layout: maximize stimulus while keeping slider + Continue on screen. */\n"
    ".jspsych-display-element{width:100%!important;}\n"
    ".jspsych-content-wrapper{width:100%!important;}\n"
    ".jspsych-content{width:100%!important;max-width:100%!important;}\n"
    "#jspsych-html-slider-response-wrapper{\n"
    "  margin:0!important;\n"
    "  display:flex!important;\n"
    "  flex-direction:column!important;\n"
    "  width:100%!important;\n"
    "  height:min(calc(100vh - 88px), calc(100dvh - 88px))!important;\n"
    "  min-height:0!important;\n"
    "}\n"
    "#jspsych-html-slider-response-stimulus{\n"
    "  flex:1 1 auto!important;\n"
    "  width:100%!important;\n"
    "  min-height:0!important;\n"
    "  overflow:hidden!important;\n"
    "  display:flex!important;\n"
    "}\n"
    "#jspsych-html-slider-response-stimulus > div{\n"
    "  flex:1 1 auto!important;\n"
    "  min-height:0!important;\n"
    "  height:100%!important;\n"
    "  max-height:100%!important;\n"
    "}\n"
    ".jspsych-html-slider-response-container{\n"
    "  flex:0 0 auto!important;\n"
    "  margin:0 auto 0.5em auto!important;\n"
    "}\n"
    "#jspsych-html-slider-response-next{\n"
    "  display:block!important;\n"
    "  margin:0.5em auto 0 auto!important;\n"
    "}\n"
    "</style>\n"
    # Auto-fit machinery. window.__sb_fit__(enabled) scales #jspsych-content
    # to fill (but not overflow) the viewport when enabled, or restores
    # natural layout + scrolling when disabled. Stimuli emit on_load with
    # their fit_to_viewport flag (default True; InformedConsent etc. opt
    # out). Uses CSS `zoom` so layout box shrinks/grows with the rendered
    # output (avoids transform-scale's layout-vs-paint divergence).
    "<script>\n"
    "window.__sb_fit__=function(enabled){\n"
    "  if(enabled===undefined){enabled=true;}\n"
    "  var apply=function(){\n"
    "    var root=document.getElementById('jspsych-content');\n"
    "    if(!root)return;\n"
    "    if(!enabled){\n"
    "      root.style.zoom='';\n"
    "      document.documentElement.style.overflow='auto';\n"
    "      document.body.style.overflow='auto';\n"
    "      return;\n"
    "    }\n"
    "    document.documentElement.style.overflow='hidden';\n"
    "    document.body.style.overflow='hidden';\n"
    "    root.style.zoom='';\n"
    "    var rect=root.getBoundingClientRect();\n"
    "    if(rect.width===0||rect.height===0)return;\n"
    "    var sx=(window.innerWidth*0.95)/rect.width;\n"
    "    var sy=(window.innerHeight*0.92)/rect.height;\n"
    "    var s=Math.min(sx,sy);\n"
    "    s=Math.max(0.4,Math.min(2.5,s));\n"
    "    if(Math.abs(s-1)>0.01){root.style.zoom=s.toFixed(3);}\n"
    "  };\n"
    "  requestAnimationFrame(apply);\n"
    "};\n"
    "var __sb_resize_t__=null;\n"
    "window.addEventListener('resize',function(){\n"
    "  clearTimeout(__sb_resize_t__);\n"
    "  __sb_resize_t__=setTimeout(function(){\n"
    "    var root=document.getElementById('jspsych-content');\n"
    "    if(root&&root.style.zoom!==''){window.__sb_fit__(true);}\n"
    "  },120);\n"
    "});\n"
    "</script>\n"
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
    "jsPsychHtmlSliderResponse": {"@jspsych/plugin-html-slider-response": "1.1.2"},
    "jsPsychRok": {"'@jspsych-contrib/plugin-rok": "1.1.1"},
    "jsPsychImageKeyboardResponse": {
        "@jspsych/plugin-image-keyboard-response": "1.1.2"
    },
    "jsPsychVideoKeyboardResponse": {
        "@jspsych/plugin-video-keyboard-response": "1.1.2"
    },
    "jsPsychHtmlChoice": {"@jspsych-contrib/plugin-html-choice": "1.0.0"},
    "jsPsychRSVP": {"@sweet-jspsych/plugin-rsvp": "0.2.4"},
    "jsPsychSymbol": {"@sweet-jspsych/plugin-symbol": "0.4.6"},
    "jsPsychForaging": {"@sweet-jspsych/plugin-foraging": "0.2.1"},
    "jsPsychGaborArray": {"@sweet-jspsych/plugin-gabor-array": "0.1.1"},
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
