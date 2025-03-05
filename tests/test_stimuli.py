import asyncio
import importlib
import inspect
import os
import pkgutil
import sys

from pyppeteer import launch

import sweetbean
from sweetbean import Block, Experiment
from sweetbean.stimulus.Stimulus import _BaseStimulus

# Define the excluded stimuli
excludes = [
    "SurveyStimulus",
    "_BaseStimulus",
    "_KeyboardResponseStimulus",
    "_Template_",
    "Generic",
]

# Define the excluded stimuli
EXCLUDES = {
    "SurveyStimulus",
    "_BaseStimulus",
    "_KeyboardResponseStimulus",
    "_Template_",
    "Generic",
}


async def test_experiment_in_browser(html_path):
    """Ensure that generated experiments run correctly in a headless browser."""
    browser = await launch(
        headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"]
    )
    page = await browser.newPage()

    # Convert the file path to an absolute file:// URL
    file_url = f"file://{os.path.abspath(html_path)}"

    # List to capture console errors
    console_errors = []

    async def capture_console(msg):
        """Capture errors from the browser console."""
        if msg.type == "error":
            console_errors.append(msg.text)

    page.on("console", capture_console)  # Listen for console errors

    await page.goto(file_url)

    # Wait for the page to load
    await page.waitForSelector("body")

    # Ensure the page title is set
    assert (
        await page.title() == "My awesome experiment"
    ), "Experiment did not load correctly!"

    assert not console_errors, f"JavaScript console errors found: {console_errors}"

    await browser.close()
    print(f"✅ {html_path} loaded successfully in browser.")


def test_compile():
    # Dynamically load all modules in the 'sweetbean.stimulus' package
    stimuli_package = sweetbean.stimulus

    # Dynamically load all modules in the 'sweetbean.stimulus' package
    for _, module_name, _ in pkgutil.iter_modules(stimuli_package.__path__):
        importlib.import_module(f"sweetbean.stimulus.{module_name}")

    # Gather all subclasses of Stimulus from the loaded modules
    stimuli_list = []
    for module in sys.modules.values():
        if module and module.__name__.startswith("sweetbean.stimulus"):
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, _BaseStimulus) and cls.__name__ not in excludes:
                    stimuli_list.append(cls)

    # Debugging: Print the found stimuli
    print()
    print("Found stimuli:", stimuli_list)
    print()

    for stimulus in stimuli_list:
        # Log which stimulus is being tested
        print(f"Testing {stimulus.__name__}...")

        # Test each stimulus
        stimulus_instance = stimulus()  # Adjust if parameters are required
        trial_sequence = Block([stimulus_instance])
        experiment = Experiment([trial_sequence])
        experiment.to_html("basic.html")
        assert os.path.exists(
            "basic.html"
        ), f"{stimulus.__name__} failed to generate HTML."
        asyncio.run(test_experiment_in_browser("basic.html"))
        os.remove("basic.html")
        print(f"{stimulus.__name__} compiled successfully.")


if __name__ == "__main__":
    test_compile()
