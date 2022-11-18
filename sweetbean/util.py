def create_html(in_path: str = '', out_path: str = ''):
    with open(in_path) as f:
        text = f.read()

    html = '<!DOCTYPE html>\n' \
           '<head>\n' \
           '<title>My awesome expmeriment</title>' \
           '<script src="https://unpkg.com/jspsych@7.3.1"></script>\n' \
           '<script src="https://unpkg.com/@jspsych/plugin-html-keyboard-response@1.1.2"></script>\n' \
           '<link href="https://unpkg.com/jspsych@7.3.1/css/jspsych.css" rel="stylesheet" type="text/css"/>\n' \
           '<style>\n' \
           'body {background: #000; color: #fff;}\n' \
           'div {font-size:24pt}' \
           '.sweetbean-square {width:10vw; height:10vw}' \
           '.sweetbean-circle {width:10vw; height:10vw; border-radius:50%}' \
           '.sweetbean-triangle {width:0; height: 0; border-left: 5vw solid transparent; border-right: 5vw solid transparent}' \
           '.feedback-screen-red {position:absolute; left:0; top:0; width:100vw; height: 100vh; background: red}' \
           '.feedback-screen-green {position:absolute; left:0; top: 0; width:100vw; height: 100vh; background: green}' \
           '</style>\n' \
           '</head>\n' \
           '<body></body>\n' \
           '<script>\n' \
           f'{text}' \
           '</script>\n' \
           '</html>'

    with open(out_path, 'w') as f:
        f.write(html)
