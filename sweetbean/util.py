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
           'body {background: #000; color: #fff}\n' \
           '</style>\n' \
           '</head>\n' \
           '<body></body>\n' \
           '<script>\n' \
           f'{text}' \
           '</script>\n' \
           '</html>'

    with open(out_path, 'w') as f:
        f.write(html)
