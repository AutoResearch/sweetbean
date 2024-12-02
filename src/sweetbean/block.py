import asyncio
import io
from typing import Any, List

from PIL import Image
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
        # self.to_js()

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

    def to_image(self):
        data = []
        shared_variables = {}
        for s in self.stimuli:
            _shared_variables = s.return_shared_variables()
            for s_key in _shared_variables:
                shared_variables[s_key] = _shared_variables[s_key].value
        if not self.timeline:
            timeline = [{}]
        else:
            timeline = self.timeline
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
                s._prepare_args_l(t, data, shared_variables)
                s.to_js_from_prepared()
                html += s.js
                html += "];\n"
                html += "jsPsych.run(trials);"
                html += HTML_APPENDIX
                image = asyncio.run(render_html_to_image(html, f"s_{k}.png"))
                duration = s.arg["duration"] if "duration" in s.arg else 0
                images.append(image)
                durations.append(duration)
                k += 1
        return images, durations


async def render_html_to_image(html_content):
    # Launch headless browser
    browser = await launch(
        headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"]
    )
    page = await browser.newPage()

    # Set the HTML content directly
    await page.setContent(html_content)

    # Wait for JavaScript to execute
    await asyncio.sleep(2)

    # Take a screenshot and store it in memory
    screenshot_bytes = await page.screenshot({"fullPage": True})

    # Close the browser
    await browser.close()

    # Create an Image object using PIL
    image = Image.open(io.BytesIO(screenshot_bytes))

    # Optionally save the image
    # if output_image:
    #     image.save(output_image)
    #     print(f"Screenshot saved at: {output_image}")

    return image
