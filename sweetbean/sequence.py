from sweetbean.stimulus import Stimulus
from sweetbean.parameter import *
from sweetbean.const import *
from sweetbean.update_package_honeycomb import *
import os
import shutil
import time


class Timeline:
    name = ''
    path = ''

    def __init__(self, name, path):
        self.name = name
        self.path = path


class Block:
    stimuli: List[Stimulus] = []
    text_js = ''
    html_list = []
    timeline = None

    def __init__(self, stimuli: List[Stimulus], timeline=None):
        if timeline is None:
            timeline = []
        self.stimuli = stimuli
        self.timeline = timeline
        self.to_psych()
        self.to_html_list()

    def to_psych(self):
        self.text_js = '{timeline: ['
        for s in self.stimuli:
            self.text_js += s.text_js + ','
        self.text_js = self.text_js[:-1]
        if isinstance(self.timeline, Timeline):
            self.text_js += f'], timeline_variables: {self.timeline.name}' + '}'
        else:
            self.text_js += f'], timeline_variables: {self.timeline}' + '}'

    def to_html_list(self):
        for s in self.stimuli:
            text_js = '{timeline: [' + s.text_js + f'], timeline_variables: {self.timeline}' + '}'
            self.html_list.append(text_js)


class Experiment:
    blocks: List[Block] = []
    text_js = ''

    def __init__(self, blocks: List[Block]):
        self.blocks = blocks
        self.to_psych()

    def to_psych(self):
        self.text_js = 'jsPsych = initJsPsych();\n'
        self.text_js += 'trials = [\n'
        for b in self.blocks:
            self.text_js += b.text_js
            self.text_js += ','
        self.text_js = self.text_js[:-1] + ']\n'
        self.text_js += ';jsPsych.run(trials)'

    def to_honeycomb(self, path_package='./package.json', path_main='./src/timelines/main.js', backup=True):
        """
        This function can be run in a honeycomb package to setup the experiment for honeycomb
        Arguments:
            path_package: the path to the package.json file relative from were you run the script
            path_main: y-intercept of the linear model
        """
        if path_main[-2:] != 'js':
            raise TypeError('Unexpected file extension (main) use js instead!')
        if path_package[-4:] != 'json':
            raise TypeError('Unexpected file extension (package) use json instead!')

        text = HONEYCOMB_PREAMBLE + '\n'
        for b in self.blocks:
            if b.timeline and isinstance(b.timeline, Timeline):
                text += f'const {b.timeline.name} = require(`{b.timeline.path}`)\n'
        text += 'const trials = [\n'
        for b in self.blocks:
            text += b.text_js
            text += ','
        text = text[:-1] + ']\n'
        text += 'return trials;}\n'
        text += HONEYCOMB_APPENDIX
        dep = {}
        for k in DEPENDENCIES:
            if text.find(k) != -1:
                text = get_import({k: DEPENDENCIES[k]}) + text
                dep.update(DEPENDENCIES[k])

        update_package(dep, path_package, backup)
        if backup:
            if os.path.exists(path_main):
                file_name, file_ext = os.path.splitext(os.path.basename(path_main))
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                if not os.path.exists('backup'):
                    os.mkdir('backup')
                new_file_name = f"backup/{file_name}_{timestamp}{file_ext}"
                shutil.copy(path_main, new_file_name)
        with open(path_main, 'w') as f:
            f.write(text)

    def to_html(self, path):
        html = HTML_PREAMBLE
        blocks = 0
        for b in self.blocks:
            if b.timeline and isinstance(b.timeline, Timeline):
                html += f'</script><script src="{b.timeline.path}">\n'
                blocks += 1
        if blocks > 0:
            html += '</script><script>\n'
        html += f'{self.text_js}' + HTML_APPENDIX

        with open(path, 'w') as f:
            f.write(html)


def sequence_to_image(block, durations=None):
    from html2image import Html2Image
    from PIL import Image, ImageOps, ImageFont, ImageDraw
    import numpy as np
    import cv2
    _dir = os.path.dirname(__file__)
    _dir_temp = os.path.join(_dir, 'temp')
    k = 0
    for html in block.html_list:
        html_full = HTML_PREAMBLE + 'jsPsych = initJsPsych();trials = [\n' + html + '];jsPsych.run(trials)' + HTML_APPENDIX
        with open(os.path.join(_dir_temp, f'page_tmp_jxqqlo{k}.html'), 'w') as f:
            f.write(html_full)
        hti = Html2Image()
        hti.screenshot(html_file=os.path.join(_dir_temp, f'page_tmp_jxqqlo{k}.html'),
                       save_as=f'page_tmp_jxqqlo{k}.png')
        os.remove(os.path.join(_dir_temp, f'page_tmp_jxqqlo{k}.html'))
        k += 1

    images = [Image.open(f'page_tmp_jxqqlo{i}.png') for i in range(k)]

    width_cum = 200
    height_cum = 200
    width_steps = []
    height_steps = []
    for i in range(k):
        color = "#aaa"
        border = (20, 20, 20, 20)
        images[i] = ImageOps.expand(images[i], border=border, fill=color)
        width, height = images[i].size
        width_step = int(width - width / 3)
        height_step = int(height - height / 5)
        width_steps.append(width_step)
        height_steps.append(height_step)
        width_cum += width_step
        height_cum += height_step

    width_last, height_last = images[-1].size
    width_cum += int(width_last / 3 + width_last)
    height_cum += int(height_last / 5)
    result_img = Image.new('RGB', (width_cum, height_cum), "#fff")
    na = np.array(result_img)
    cv2.arrowedLine(na, (int(100 + width_steps[0] * 2.5), int(100 + height_steps[0] / 2)),
                    (int(width_cum - 100 - width_steps[-1] * .5), int(height_cum - 100 - height_steps[-1] / 2)),
                    (20, 20, 20), 20, tipLength=.02)
    result_img = Image.fromarray(na)

    pos_x = 100
    pos_y = 100
    font = ImageFont.truetype(os.path.join(_dir, 'arial.ttf'), 128)
    for i in range(k):
        result_img.paste(images[i], (pos_x, pos_y))
        result_img_draw = ImageDraw.Draw(result_img)
        if 'duration' in block.stimuli[i].arg and block.stimuli[i].arg['duration'] is not None and not isinstance(
                block.stimuli[i].arg['duration'], TimelineVariable):
            duration = block.stimuli[i].arg['duration']
        elif durations and i < len(durations):
            duration = durations[i]
        if duration is not None:
            result_img_draw.text((pos_x + 100 + int(3 * width_steps[i] / 2), pos_y + int(height_steps[i] / 2)),
                                 font=font, text=f'{duration}ms', fill=(0, 0, 0))
        pos_x += width_steps[i]
        pos_y += height_steps[i]

    result_img.save(os.path.join('stimulus_timeline.png'))
    for i in range(k):
        os.remove(f'page_tmp_jxqqlo{i}.png')
