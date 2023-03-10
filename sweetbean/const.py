HTML_PREAMBLE = '<!DOCTYPE html>\n' \
                '<head>\n' \
                '<title>My awesome expmeriment</title>' \
                '<script src="https://unpkg.com/jspsych@7.3.1"></script>\n' \
                '<script src="https://unpkg.com/@jspsych/plugin-html-keyboard-response@1.1.2"></script>\n' \
                '<script src="https://unpkg.com/@jspsych/plugin-survey-text@1.1.2"></script>\n' \
                '<script src="https://unpkg.com/@jspsych/plugin-survey-multi-choice@1.1.2"></script>\n' \
                '<script src="https://unpkg.com/@jspsych/plugin-survey-likert@1.1.2"></script>\n' \
                '<script src="https://unpkg.com/@jspsych/plugin-survey-likert@1.1.2"></script>\n' \
                '<link href="https://unpkg.com/jspsych@7.3.1/css/jspsych.css" rel="stylesheet" type="text/css"/>\n' \
                '<script src="https://unpkg.com/@jspsych/plugin-image-keyboard-response@1.1.2"></script>\n' \
                '<script src="https://unpkg.com/@jspsych/plugin-video-keyboard-response@1.1.2"></script>\n' \
                'body {background: #000; color: #fff;}\n' \
                'div {font-size:36pt; line-height:40pt}' \
                '.sweetbean-square {width:10vw; height:10vw}' \
                '.sweetbean-circle {width:10vw; height:10vw; border-radius:50%}' \
                '.sweetbean-triangle {width:10vw; height:10vw; clip-path:polygon(50% 0, 0 100%, 100% 100%)}' \
                '.feedback-screen-red {position:absolute; left:0; top:0; width:100vw; height: 100vh; background: red}' \
                '.feedback-screen-green {position:absolute; left:0; top: 0; width:100vw; height: 100vh; background: green}' \
                '</style>\n' \
                '</head>\n' \
                '<body></body>\n' \
                '<script>\n'
HTML_APPENDIX = '</script>\n' \
                '</html>'

HONEYCOMB_PREAMBLE = 'import \'jspsych/css/jspsych.css\'\n' \
                     'const jsPsychOptions = {}\n' \
                     'function buildTimeline(jsPsych) {\n' \
                     'console.log(jsPsych.version())\n' \

HONEYCOMB_APPENDIX = 'export { jsPsychOptions, buildTimeline }'

JSPSYCH = {'jspsych': '7.3.1'}

DEPENDENCIES = {
    'jsPsychHtmlKeyboardResponse': {'@jspsych/plugin-html-keyboard-response': '1.1.2'},
    'jsPsychSurveyText': {'@jspsych/plugin-survey-text': '1.1.2'},
    'jsPsychSurveyMultiChoice': {'@jspsych/plugin-survey-multi-choice': '1.1.2'},
    'jsPsychSurveyLikert': {'@jspsych/plugin-survey-likert': '1.1.2'},
    'jsPsychImageKeyboardResponse': {'@jspsych/plugin-image-keyboard-response': '1.1.2'},
    'jsPsychVideoKeyboardResponse': {'@jspsych/plugin-video-keyboard-respons': '1.1.2'}
}
