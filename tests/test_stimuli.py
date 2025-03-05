import asyncio
import importlib
import inspect
import os
import pkgutil
import sys

import pytest
from pyppeteer import launch

import sweetbean
from sweetbean import Block, Experiment
from sweetbean.stimulus.Stimulus import _BaseStimulus

# Stimuli we don't want to test or are abstract
EXCLUDES = {
    "SurveyStimulus",
    "_BaseStimulus",
    "_KeyboardResponseStimulus",
    "_Template_",
    "Generic",
}


# OPTIONAL: If you have a particularly heavy or unstable stimulus (like "Bandit") that
# you want to skip on CI, uncomment this snippet:
#
# SKIP_RESOURCE_INTENSIVE = os.getenv("CI") == "true"


async def run_experiment_in_browser(html_path: str):
    """Launch headless Chromium, load the HTML, check for errors, then close."""

    # Use system Chromium or Pyppeteer-downloaded Chromium
    executable_path = os.getenv("PYPPETEER_EXECUTABLE_PATH", None)
    print("Using Chromium path:", executable_path)

    # Launch with recommended flags to prevent random crashes in CI
    browser = await launch(
        headless=True,
        executablePath=executable_path,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
        ],
    )

    page = await browser.newPage()
    file_url = f"file://{os.path.abspath(html_path)}"
    console_errors = []

    async def capture_console(msg):
        if msg.type == "error":
            console_errors.append(msg.text)

    # Listen for console errors
    page.on("console", capture_console)

    # Go to the page with a generous timeout and waitUntil=networkidle2
    await page.goto(file_url, options={"timeout": 60000, "waitUntil": "networkidle2"})

    # Wait a moment if needed to stabilize heavy stimuli
    await page.waitForSelector("body")
    # await page.waitForTimeout(1000)  # 1-second extra wait for reliability

    # Basic checks
    title = await page.title()
    assert title == "My awesome experiment", f"Experiment title mismatch: {title}"
    assert not console_errors, f"JavaScript console errors found: {console_errors}"

    await browser.close()
    print(f"✅ {html_path} loaded successfully in browser with no console errors.")


async def compile_all_stimuli():
    """Aggregate test: compiles each stimulus, runs a headless check in one event loop."""

    # Dynamically load all stimuli modules
    stimuli_package = sweetbean.stimulus
    for _, module_name, _ in pkgutil.iter_modules(stimuli_package.__path__):
        importlib.import_module(f"sweetbean.stimulus.{module_name}")

    # Collect valid stimuli classes
    stimuli_list = []
    for module in sys.modules.values():
        if module and module.__name__.startswith("sweetbean.stimulus"):
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, _BaseStimulus) and cls.__name__ not in EXCLUDES:
                    stimuli_list.append(cls)

    print(f"\nFound stimuli: {[s.__name__ for s in stimuli_list]}\n")

    for stimulus_class in stimuli_list:
        print(f"Testing {stimulus_class.__name__}...")

        # (OPTIONAL) Skip a known resource hog on CI
        # if SKIP_RESOURCE_INTENSIVE and stimulus_class.__name__ == "Bandit":
        #     print("Skipping Bandit on CI to avoid crashes.")
        #     continue

        # Compile the experiment
        stimulus_instance = stimulus_class()
        block = Block([stimulus_instance])
        experiment = Experiment([block])
        experiment.to_html("basic.html")

        assert os.path.exists(
            "basic.html"
        ), f"{stimulus_class.__name__} failed to generate HTML."

        # Test in headless browser
        await run_experiment_in_browser("basic.html")

        # Clean up
        os.remove("basic.html")
        print(f"{stimulus_class.__name__} compiled and ran successfully.")


@pytest.mark.skipif(os.getenv("CI") == "true", reason="Too resource-intensive for CI")
def test_compile():
    """Pytest entry point: calls our async aggregator exactly once."""
    asyncio.run(compile_all_stimuli())


if __name__ == "__main__":
    # If someone runs this script directly, do the same single-run approach
    asyncio.run(compile_all_stimuli())
