from typing import List
from sweetbean.primitives import Stimulus, TrialSequence
import os
from PIL import Image, ImageOps, ImageDraw, ImageFont
import cv2
import numpy as np


class TrialBlock:
    stimuli: List[Stimulus] = []
    sequence: TrialSequence = None

    def __init__(self, stimuli: List[Stimulus]):
        self.stimuli = stimuli

    def to_psych(self):
        res = '{timeline: ['
        for s in self.stimuli:
            res += s.to_psych() + ','
        res = res[:-1]
        res += f'], timeline_variables: []' \
               '}'
        return res

    def to_image(self):
        _dir = os.path.dirname(__file__)
        for i in range(len(self.stimuli)):
            self.stimuli[i].to_img(f's_{i}')
        images = [Image.open(os.path.join(_dir, f's_{i}_screenshot.png')) for i in range(len(self.stimuli))]

        width_cum = 200
        height_cum = 200
        width_steps = []
        height_steps = []
        for i in range(len(images)):
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
        font = ImageFont.truetype('arial.ttf', 128)
        for i in range(len(self.stimuli)):
            result_img.paste(images[i], (pos_x, pos_y))
            result_img_draw = ImageDraw.Draw(result_img)
            result_img_draw.text((pos_x + 100 + int(3 * width_steps[i] / 2), pos_y + int(height_steps[i] / 2)),
                                 f'{self.stimuli[i]._duration}ms',
                                 font=font, fill=(0, 0, 0))
            pos_x += width_steps[i]
            pos_y += height_steps[i]

        # result_img = result_img.resize((1920, 1080))

        result_img.save(os.path.join(_dir, 'stimulus_timeline.png'))
        for i in range(len(self.stimuli)):
            os.remove(os.path.join(_dir, f's_{i}_screenshot.png'))


class Experiment:
    blocks: List[TrialBlock] = []

    def __init__(self, blocks: List[TrialBlock]):
        self.blocks = blocks

    def to_psych(self):
        res = 'jsPsych = initJsPsych();\n' \
              'trials = [\n'
        for b in self.blocks:
            res += b.to_psych()
            res += ','
        res = res[:-1] + ']\n'
        res += ';jsPsych.run(trials)'
        return res
