import asyncio
import io
import math
import random
from typing import Any, List

from PIL import Image, ImageDraw, ImageFont
from pyppeteer import launch

from sweetbean._const import HTML_APPENDIX, HTML_PREAMBLE
from sweetbean.variable import CodeVariable


class Block:
    """
    A block of stimuli (for example, an instruction, training, or test block)
    """

    stimuli: List[Any] = []
    js = ""
    timeline = None

    def __init__(self, stimuli, timeline=None):
        """
        Arguments:
            stimuli: a list of stimuli
            timeline: a list of dictionaries with the name of the timeline variables
        """
        if timeline is None:
            timeline = []
        self.stimuli = stimuli
        self.timeline = timeline

    def to_js(self):
        self.js = "{timeline: ["
        for s in self.stimuli:
            s.to_js()
            self.js += s.js + ","
        self.js = self.js[:-1]
        if isinstance(self.timeline, CodeVariable):
            self.js += f"], timeline_variables: {self.timeline.name}" + "}"
        else:
            self.js += f"], timeline_variables: {self.timeline}" + "}"

    def to_image(self, path, data, sequence=True, timeline_idx="random", zoom_factor=3):
        """
        Create an image of the stimuli sequence of the block
        Arguments:
            path: the path to save the image
            data: if needed data can be passed in for the stimuli
                (for example, correct if the sequence contains a feedback stimulus)
            sequence: if True, the images are combined into one image else they are
                stored separately
            timeline_idx: the index of the timeline element to use, if "random" a random
                timeline element is chosen, if none, the whole timeline is shown
            zoom_factor: the factor by which the images are zoomed (can be a list if
                different zoom factors for each stimulus are needed)

        """

        data_in = []
        shared_variables = {}
        for s in self.stimuli:
            _shared_variables = s.return_shared_variables()
            for s_key in _shared_variables:
                shared_variables[s_key] = _shared_variables[s_key].value
        if not self.timeline:
            timeline = [{}]
        else:
            timeline = self.timeline

        if timeline_idx == "random":
            timeline = [timeline[random.randint(0, len(timeline) - 1)]]
        elif timeline_idx is not None:
            timeline = [timeline[timeline_idx]]

        k = 0
        images = []
        durations = []
        for t in timeline:
            for s in self.stimuli:
                if s.arg["duration"] == 0:
                    continue
                html = HTML_PREAMBLE
                html += "jsPsych = initJsPsych();\n"
                html += "trials = [\n"
                s._prepare_args_l(t, data_in, shared_variables)
                s.to_js_for_image()
                html += s.js
                html += "];\n"
                html += "jsPsych.run(trials);"
                html += HTML_APPENDIX
                image = asyncio.run(render_html_to_image(html))
                duration = s.l_args["duration"] if "duration" in s.l_args else 0
                images.append(image)
                durations.append(duration)
                if data and k < len(data):
                    data_in.append(data[k])
                k += 1

        if not sequence:
            if path:
                for idx, i in enumerate(images):
                    i.save(f"{path}/stimulus_{idx}.png")
                return
            return images, durations
        result_image = create_stimulus_sequence(
            images, durations, zoom_factor=zoom_factor
        )
        if path:
            result_image.save(path)
            return
        return result_image


async def render_html_to_image(html_content):
    # Launch headless browser
    browser = await launch(
        headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"]
    )
    page = await browser.newPage()

    await page.setViewport({"width": 1920, "height": 1080})

    # Set the HTML content directly
    await page.setContent(html_content)

    # Wait for JavaScript to execute
    await asyncio.sleep(5)

    # Take a screenshot and store it in memory
    screenshot_bytes = await page.screenshot({"fullPage": False})

    # Close the browser
    await browser.close()

    # Create an Image object using PIL
    image = Image.open(io.BytesIO(screenshot_bytes))

    return image


def create_stimulus_sequence(
    images,
    timings,
    overlap_x=0.05,
    overlap_y=0.5,
    zoom_factor=2.5,
    arrow_color=(0, 0, 0),
    font_path=None,
):
    if not hasattr(zoom_factor, "__iter__"):
        zoom_factor = [zoom_factor] * len(images)
    if len(images) != len(timings):
        raise ValueError("The number of images and timings must be the same.")

    # Determine the size of each image (assuming all images are the same size)
    img_width, img_height = images[0].size

    # Calculate overlap in pixels
    x_overlap = img_width * overlap_x
    y_overlap = img_height * overlap_y

    # Calculate positions for each image
    positions = []
    for idx in range(len(images)):
        x = int(idx * (img_width - x_overlap)) + int(
            img_width * 0.25
        )  # Extra space for arrow and text
        y = int(idx * (img_height - y_overlap)) + int(
            img_height * 0.25
        )  # Extra space for arrow and text
        positions.append((x, y))

    # Calculate total canvas size
    last_x, last_y = positions[-1]
    total_width = (
        last_x + img_width + int(img_width * 0.25)
    )  # Extra space for arrow and text
    total_height = (
        last_y + img_height + int(img_height * 0.5)
    )  # Extra space for arrow and text

    font_size = int(images[0].size[0] * 0.1)  # 10% of the image height
    font_size = max(10, font_size)

    # Create a new image with white background
    canvas = Image.new("RGB", (total_width, total_height), "white")
    draw = ImageDraw.Draw(canvas)

    # Optional: Load a custom font
    if font_path is not None:
        font = ImageFont.truetype(font_path, size=font_size)
    else:
        font = ImageFont.load_default(size=font_size)

    zoom_idx = 0
    # Paste images onto the canvas
    for img, (x, y) in zip(images, positions):
        # Calculate new dimensions for zooming
        width, height = img.size
        crop_width = int(width / zoom_factor[zoom_idx])
        crop_height = int(height / zoom_factor[zoom_idx])
        zoom_idx += 1

        # Define the cropping box around the center
        left = (width - crop_width) // 2
        upper = (height - crop_height) // 2
        right = left + crop_width
        lower = upper + crop_height

        # Crop and resize the image back to its original size
        cropped_img = img.crop((left, upper, right, lower)).resize(
            (width, height), Image.LANCZOS
        )

        # Paste the zoomed image onto the canvas
        canvas.paste(cropped_img, (x, y), cropped_img if img.mode == "RGBA" else None)

    # Draw a diagonal arrow below the images
    arrow_start = (positions[0][0], positions[0][1] + img_height)
    arrow_end = (positions[-1][0], positions[-1][1] + img_height)
    draw.line([arrow_start, arrow_end], fill=arrow_color, width=font_size // 15)

    # Calculate angle for arrowhead
    angle = math.atan2(arrow_end[1] - arrow_start[1], arrow_end[0] - arrow_start[0])
    arrowhead_length = font_size // 2
    arrowhead_angle = math.pi / 12  # 30 degrees

    # Points for the arrowhead
    arrowhead_p1 = (
        arrow_end[0] - arrowhead_length * math.cos(angle - arrowhead_angle),
        arrow_end[1] - arrowhead_length * math.sin(angle - arrowhead_angle),
    )
    arrowhead_p2 = (
        arrow_end[0] - arrowhead_length * math.cos(angle + arrowhead_angle),
        arrow_end[1] - arrowhead_length * math.sin(angle + arrowhead_angle),
    )

    # Draw the arrowhead
    draw.polygon([arrow_end, arrowhead_p1, arrowhead_p2], fill=arrow_color)

    # Add timings next to the arrow
    for idx, timing in enumerate(timings):
        # Calculate position along the arrow
        if len(timings) > 1:
            frac = idx / (len(timings) - 1)
        else:
            frac = 0
        text_x = arrow_start[0] + frac * (arrow_end[0] - arrow_start[0])
        text_y = (
            arrow_start[1] + frac * (arrow_end[1] - arrow_start[1]) + font_size
        )  # Slightly below the arrow
        text = f"{timing} ms" if timing is not None else "Until\nresponse"
        align = "left" if timing is not None else "center"
        print(align)
        bbox = draw.textbbox(
            (0, 0), text, font=font, align=align
        )  # Top-left corner for measurement
        text_width = bbox[2] - bbox[0]

        # Use the width and height for centering
        draw.text(
            (text_x - text_width / 2, text_y),
            text,
            fill="black",
            font=font,
            align=align,
        )

    return canvas
