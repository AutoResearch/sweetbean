import os
import shutil
import time
from typing import Generic, List

from sweetbean.const import (
    AUTORA_APPENDIX,
    AUTORA_PREAMBLE,
    DEPENDENCIES,
    FUNCTION_APPENDIX,
    FUNCTION_PREAMBLE,
    HONEYCOMB_APPENDIX,
    HONEYCOMB_PREAMBLE,
    HTML_APPENDIX,
    HTML_PREAMBLE,
    TEXT_APPENDIX,
)
from sweetbean.parameter import CodeVariable
from sweetbean.stimulus import StimulusVar, TimelineVariable
from sweetbean.update_package_honeycomb import get_import, update_package


class Timeline:
    name = ""
    path = ""

    def __init__(self, name, path):
        self.name = name
        self.path = path


class Block(Generic[StimulusVar]):
    stimuli: List[StimulusVar] = []
    text_js = ""
    html_list: List[str] = []
    timeline = None

    def __init__(self, stimuli: List[StimulusVar], timeline=None):
        if timeline is None:
            timeline = []
        self.stimuli = stimuli
        self.timeline = timeline
        self.to_psych()
        self.to_html_list()

    def to_psych(self):
        self.text_js = "{timeline: ["
        for s in self.stimuli:
            self.text_js += s.text_js + ","
        self.text_js = self.text_js[:-1]
        if isinstance(self.timeline, Timeline):
            self.text_js += f"], timeline_variables: {self.timeline.name}" + "}"
        elif isinstance(self.timeline, CodeVariable):
            self.text_js += f"], timeline_variables: {self.timeline.name}" + "}"
        else:
            self.text_js += f"], timeline_variables: {self.timeline}" + "}"

    def to_html_list(self):
        for s in self.stimuli:
            text_js = (
                "{timeline: ["
                + s.text_js
                + f"], timeline_variables: {self.timeline}"
                + "}"
            )
            self.html_list.append(text_js)


class Experiment:
    blocks: List[Block] = []
    text_js = ""

    def __init__(self, blocks: List[Block]):
        self.blocks = blocks
        self.to_psych()

    def to_psych(self):
        self.text_js = "jsPsych = initJsPsych();\n"
        self.text_js += "trials = [\n"
        for b in self.blocks:
            self.text_js += b.text_js
            self.text_js += ","
        self.text_js = self.text_js[:-1] + "]\n"
        self.text_js += ";jsPsych.run(trials)"

    def to_honeycomb(
        self,
        path_package="./package.json",
        path_main="./src/timelines/main.js",
        backup=True,
    ):
        """
        This function can be run in a honeycomb package to set up the experiment for honeycomb
        Arguments:
            path_package: the path to the package.json file relative from where you run the script
            path_main: path to the main.js script relative from where you run this script
        """
        if path_main[-2:] != "js":
            raise TypeError("Unexpected file extension (main) use js instead!")
        if path_package[-4:] != "json":
            raise TypeError("Unexpected file extension (package) use json instead!")

        text = HONEYCOMB_PREAMBLE + "\n"
        for b in self.blocks:
            if b.timeline and isinstance(b.timeline, Timeline):
                text += f"const {b.timeline.name} = require(`{b.timeline.path}`)\n"
        text += "const trials = [\n"
        for b in self.blocks:
            text += b.text_js
            text += ","
        text = text[:-1] + "]\n"
        text += "return trials;}\n"
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
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                if not os.path.exists("backup"):
                    os.mkdir("backup")
                new_file_name = f"backup/{file_name}_{timestamp}{file_ext}"
                shutil.copy(path_main, new_file_name)
        with open(path_main, "w") as f:
            f.write(text)

    def to_html(self, path):
        html = HTML_PREAMBLE
        blocks = 0
        for b in self.blocks:
            if b.timeline and isinstance(b.timeline, Timeline):
                html += f'</script><script src="{b.timeline.path}">\n'
                blocks += 1
        if blocks > 0:
            html += "</script><script>\n"
        html += f"{self.text_js}" + HTML_APPENDIX

        with open(path, "w") as f:
            f.write(html)

    def to_autora(
        self,
        path_package="./package.json",
        path_main="./src/design/main.js",
        backup=True,
    ):
        """
        This function can be run in an autora template to set up the experiment for autora.
        Here, the condition should be an array of block timeline sequences and the observation
        is the full jsPsych data.
        Arguments:
            path_package: the path to the package.json file relative from where you run this script
            path_main: y-intercept of the linear model
        """
        if path_main[-2:] != "js":
            raise TypeError("Unexpected file extension (main) use js instead!")
        if path_package[-4:] != "json":
            raise TypeError("Unexpected file extension (package) use json instead!")

        text = AUTORA_PREAMBLE + "\n"
        text += "const trials = [\n"
        for b in self.blocks:
            text += b.text_js
            text += ","
        text = text[:-1] + "]\n"
        text += AUTORA_APPENDIX
        dep = {}
        for k in DEPENDENCIES:
            if text.find(k) != -1:
                text = get_import({k: DEPENDENCIES[k]}) + text
                dep.update(DEPENDENCIES[k])

        update_package(dep, path_package, backup)
        if backup:
            if os.path.exists(path_main):
                file_name, file_ext = os.path.splitext(os.path.basename(path_main))
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                if not os.path.exists("backup"):
                    os.mkdir("backup")
                new_file_name = f"backup/{file_name}_{timestamp}{file_ext}"
                shutil.copy(path_main, new_file_name)
        with open(path_main, "w") as f:
            f.write(text)

    def to_js_string(
        self,
        as_function=False,
        is_async=False,
    ):
        text = FUNCTION_PREAMBLE(is_async) if as_function else ""
        text += "const jsPsych = initJsPsych()\n"
        text += "const trials = [\n"
        for b in self.blocks:
            text += b.text_js
            text += ","
        text = text[:-1] + "]\n"
        text += FUNCTION_APPENDIX(is_async) if as_function else TEXT_APPENDIX(is_async)
        return text


def sequence_to_image(block, durations=None):
    try:
        import cv2
        import numpy as np
        from html2image import Html2Image
        from PIL import Image, ImageDraw, ImageFont, ImageOps
    except ImportError:
        print(
            "To use the sequence_to_image feature, please install opencv-python and html2image"
        )

    temp_file = "page_tmp"
    png_temp_file = "stimuli_sequence"
    k = 0
    for html in block.html_list:
        html_full = (
            HTML_PREAMBLE
            + "jsPsych = initJsPsych();trials = [\n"
            + html
            + "];jsPsych.run(trials)"
            + HTML_APPENDIX
        )
        with open(f"{temp_file}{k}.html", "w") as f:
            f.write(html_full)
        hti = Html2Image()
        hti.screenshot(
            html_file=f"{temp_file}{k}.html",
            save_as=f"{png_temp_file}{k}.png",
        )
        os.remove(f"{temp_file}{k}.html")
        k += 1

    images = [Image.open(f"{png_temp_file}{i}.png") for i in range(k)]

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
    result_img = Image.new("RGB", (width_cum, height_cum), "#fff")
    na = np.array(result_img)
    cv2.arrowedLine(
        na,
        (int(100 + width_steps[0] * 2.5), int(100 + height_steps[0] / 2)),
        (
            int(width_cum - 100 - width_steps[-1] * 0.5),
            int(height_cum - 100 - height_steps[-1] / 2),
        ),
        (20, 20, 20),
        20,
        tipLength=0.02,
    )
    result_img = Image.fromarray(na)

    pos_x = 100
    pos_y = 100
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the font file within the same directory
    font_path = os.path.join(current_dir, "arial.ttf")
    font = ImageFont.truetype(font_path, 256)
    for i in range(k):
        result_img.paste(images[i], (pos_x, pos_y))
        result_img_draw = ImageDraw.Draw(result_img)
        if (
            "duration" in block.stimuli[i].arg
            and block.stimuli[i].arg["duration"] is not None
            and not isinstance(block.stimuli[i].arg["duration"], TimelineVariable)
        ):
            duration = block.stimuli[i].arg["duration"]
        elif durations and i < len(durations):
            duration = durations[i]
        if duration is not None:
            result_img_draw.text(
                (
                    pos_x + 100 + int(3 * width_steps[i] / 2),
                    pos_y + int(height_steps[i] / 2),
                ),
                font=font,
                text=f"{duration}ms",
                fill=(0, 0, 0),
            )
        pos_x += width_steps[i]
        pos_y += height_steps[i]

    result_img.save(os.path.join("stimulus_timeline.png"))
    for i in range(k):
        os.remove(f"{png_temp_file}{i}.png")
