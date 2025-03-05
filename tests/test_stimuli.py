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

# Excluded Stimuli
EXCLUDES = {
    "SurveyStimulus",
    "_BaseStimulus",
    "_KeyboardResponseStimulus",
    "_Template_",
    "Generic",
}


async def run_experiment_in_browser(html_path):
    """Ensure that generated experiments run correctly in a headless browser."""
    executable_path = os.getenv("PYPPETEER_EXECUTABLE_PATH", None)

    browser = await launch(
        headless=True,
        executablePath=executable_path,
        args=["--no-sandbox", "--disable-setuid-sandbox"],
    )
    page = await browser.newPage()

    file_url = f"file://{os.path.abspath(html_path)}"
    console_errors = []

    async def capture_console(msg):
        if msg.type == "error":
            console_errors.append(msg.text)

    page.on("console", capture_console)
    await page.goto(file_url)
    await page.waitForSelector("body")

    # Check title
    assert (
        await page.title()
    ) == "My awesome experiment", "Experiment did not load correctly!"
    assert not console_errors, f"JavaScript console errors found: {console_errors}"

    await browser.close()
    print(f"✅ {html_path} loaded successfully in browser.")


async def compile_all_stimuli():
    """Gathers all stimuli, compiles them, and runs the browser test in a single event loop."""

    # Dynamically load all modules in the 'sweetbean.stimulus' package
    stimuli_package = sweetbean.stimulus
    for _, module_name, _ in pkgutil.iter_modules(stimuli_package.__path__):
        importlib.import_module(f"sweetbean.stimulus.{module_name}")

    # Gather all valid stimuli classes
    stimuli_list = []
    for module in sys.modules.values():
        if module and module.__name__.startswith("sweetbean.stimulus"):
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, _BaseStimulus) and cls.__name__ not in EXCLUDES:
                    stimuli_list.append(cls)

    print(f"\nFound stimuli: {[s.__name__ for s in stimuli_list]}\n")

    for stimulus_class in stimuli_list:
        print(f"Testing {stimulus_class.__name__}...")

        # Instantiate, compile, test in browser
        stimulus_instance = stimulus_class()
        trial_sequence = Block([stimulus_instance])
        experiment = Experiment([trial_sequence])
        experiment.to_html("basic.html")

        assert os.path.exists(
            "basic.html"
        ), f"{stimulus_class.__name__} failed to generate HTML."

        # Run the test in a single event loop
        await run_experiment_in_browser("basic.html")

        os.remove("basic.html")
        print(f"{stimulus_class.__name__} compiled successfully!")


def test_compile():
    """Pytest entry point -- calls our async aggregator exactly once."""
    asyncio.run(compile_all_stimuli())


if __name__ == "__main__":
    # If someone runs this script directly
    asyncio.run(compile_all_stimuli())
