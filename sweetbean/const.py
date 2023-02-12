HTML_PREAMBLE = '<!DOCTYPE html>\n' \
                '<head>\n' \
                '<title>My awesome expmeriment</title>' \
                '<script src="https://unpkg.com/jspsych@7.3.1"></script>\n' \
                '<script src="https://unpkg.com/@jspsych/plugin-html-keyboard-response@1.1.2"></script>\n' \
                '<link href="https://unpkg.com/jspsych@7.3.1/css/jspsych.css" rel="stylesheet" type="text/css"/>\n' \
                '<style>\n' \
                'body {background: #000; color: #fff;}\n' \
                'div {font-size:36pt}' \
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