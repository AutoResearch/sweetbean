from typing import List
from sweetbean.stimulus import Stimulus
from sweetbean.parameter import TimelineVariable
from sweetbean.const import *
from html2image import Html2Image
import os
from PIL import Image, ImageOps, ImageFont, ImageDraw
import numpy as np
import cv2


class TrialBlock:
    stimuli: List[Stimulus] = []
    text_js = ''
    html_list = []

    def __init__(self, stimuli: List[Stimulus], timeline=[]):
        self.stimuli = stimuli
        self.timeline = timeline
        self.to_psych()
        self.to_html_list()

    def to_psych(self):
        self.text_js = '{timeline: ['
        for s in self.stimuli:
            self.text_js += s.text_js + ','
        self.text_js = self.text_js[:-1]
        self.text_js += f'], timeline_variables: {self.timeline}' + '}'

    def to_html_list(self):
        for s in self.stimuli:
            text_js = '{timeline: [' + s.text_js + f'], timeline_variables: {self.timeline}' + '}'
            self.html_list.append(text_js)

    # def to_image(self):
    #     _dir = os.path.dirname(__file__)
    #     for i in range(len(self.stimuli)):
    #         self.stimuli[i].to_img(f's_{i}')
    #     images = [Image.open(os.path.join(_dir, f's_{i}_screenshot.png')) for i in range(len(self.stimuli))]
    #
    #     width_cum = 200
    #     height_cum = 200
    #     width_steps = []
    #     height_steps = []
    #     for i in range(len(images)):
    #         color = "#aaa"
    #         border = (20, 20, 20, 20)
    #         images[i] = ImageOps.expand(images[i], border=border, fill=color)
    #         width, height = images[i].size
    #         width_step = int(width - width / 3)
    #         height_step = int(height - height / 5)
    #         width_steps.append(width_step)
    #         height_steps.append(height_step)
    #         width_cum += width_step
    #         height_cum += height_step
    #
    #     width_last, height_last = images[-1].size
    #     width_cum += int(width_last / 3 + width_last)
    #     height_cum += int(height_last / 5)
    #     result_img = Image.new('RGB', (width_cum, height_cum), "#fff")
    #     na = np.array(result_img)
    #     cv2.arrowedLine(na, (int(100 + width_steps[0] * 2.5), int(100 + height_steps[0] / 2)),
    #                     (int(width_cum - 100 - width_steps[-1] * .5), int(height_cum - 100 - height_steps[-1] / 2)),
    #                     (20, 20, 20), 20, tipLength=.02)
    #     result_img = Image.fromarray(na)
    #
    #     pos_x = 100
    #     pos_y = 100
    #     font = ImageFont.truetype('arial.ttf', 128)
    #     for i in range(len(self.stimuli)):
    #         result_img.paste(images[i], (pos_x, pos_y))
    #         result_img_draw = ImageDraw.Draw(result_img)
    #         result_img_draw.text((pos_x + 100 + int(3 * width_steps[i] / 2), pos_y + int(height_steps[i] / 2)),
    #                              f'{self.stimuli[i]._duration}ms',
    #                              font=font, fill=(0, 0, 0))
    #         pos_x += width_steps[i]
    #         pos_y += height_steps[i]
    #
    #
    #     result_img.save(os.path.join(_dir, 'stimulus_timeline.png'))
    #     for i in range(len(self.stimuli)):
    #         os.remove(os.path.join(_dir, f's_{i}_screenshot.png'))


class Experiment:
    blocks: List[TrialBlock] = []
    text_js = ''

    def __init__(self, blocks: List[TrialBlock]):
        self.blocks = blocks
        self.to_psych()

    def to_psych(self):
        self.text_js = 'jsPsych = initJsPsych();\n' \
                       'trials = [\n'
        for b in self.blocks:
            self.text_js += b.text_js
            self.text_js += ','
        self.text_js = self.text_js[:-1] + ']\n'
        self.text_js += ';jsPsych.run(trials)'

    def to_html(self, path):
        html = HTML_PREAMBLE + f'{self.text_js}' + HTML_APPENDIX

        with open(path, 'w') as f:
            f.write(html)


def sequence_to_image(trialBlock, durations=None):
    _dir = os.path.dirname(__file__)
    _dir_temp = os.path.join(_dir, 'temp')
    k = 0
    for html in trialBlock.html_list:
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
        if 'duration' in trialBlock.stimuli[i].arg and trialBlock.stimuli[i].arg['duration'] is not None and not isinstance(trialBlock.stimuli[i].arg['duration'], TimelineVariable):
            duration = trialBlock.stimuli[i].arg['duration']
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
