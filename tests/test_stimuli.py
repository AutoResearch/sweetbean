import asyncio
import importlib
import os
import pkgutil
import sys

import pytest
from pyppeteer import launch

import sweetbean
from sweetbean import Block, Experiment
from sweetbean.stimulus.Stimulus import _BaseStimulus

EXCLUDES = {
    "SurveyStimulus",
    "_BaseStimulus",
    "_KeyboardResponseStimulus",
    "_Template_",
    "Generic",
}


# ----- 1. Browser helper function -------------------------------- #


async def run_experiment_in_browser(html_path: str):
    """Launch headless Chromium, load the HTML, check for errors, then close."""
    executable_path = os.getenv("PYPPETEER_EXECUTABLE_PATH", None)
    print("Using Chromium path:", executable_path)

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

    file_url = f"file://{html_path}"
    console_errors = []

    def capture_console(msg):
        if msg.type == "error":
            console_errors.append(msg.text)

    page.on("console", capture_console)

    # Generous timeout, wait for network to be idle
    await page.goto(file_url, options={"timeout": 60000, "waitUntil": "networkidle2"})

    # If needed, wait for a selector or short sleep
    await page.waitForSelector("body")
    # await asyncio.sleep(1)

    title = await page.title()
    assert (
        title == "My awesome experiment"
    ), f"Experiment did not load correctly! Title: {title}"
    assert not console_errors, f"JavaScript console errors found: {console_errors}"

    await browser.close()
    print(f"✅ {html_path} loaded successfully in browser with no console errors.")


# ----- 2. Pytest fixture collecting stimuli ------------------------ #


@pytest.fixture(scope="session")
def all_stimuli():
    """Collects all valid stimuli classes from sweetbean.stimulus."""
    stimuli_package = sweetbean.stimulus
    for _, module_name, _ in pkgutil.iter_modules(stimuli_package.__path__):
        importlib.import_module(f"sweetbean.stimulus.{module_name}")

    stimuli_list = []
    for module in sys.modules.values():
        if module and module.__name__.startswith("sweetbean.stimulus"):
            for name, cls in getattr(module, "__dict__", {}).items():
                if (
                    isinstance(cls, type)
                    and issubclass(cls, _BaseStimulus)
                    and cls.__name__ not in EXCLUDES
                ):
                    stimuli_list.append(cls)
    return stimuli_list


# ----- 3. Parametrized test: one test per stimulus ---------------- #


@pytest.mark.parametrize("stimulus_class", [])
def test_compile_stimulus(stimulus_class):
    """Compile and test a single stimulus in a headless browser."""

    # (Optional) skip known resource hogs in CI:
    # if os.getenv("CI") == "true" and stimulus_class.__name__ == "Bandit":
    #     pytest.skip("Skipping Bandit on CI to avoid crashes.")

    # 1) Create the experiment
    stimulus_instance = stimulus_class()
    block = Block([stimulus_instance])
    experiment = Experiment([block])
    html_path = "basic.html"
    experiment.to_html(html_path)

    assert os.path.exists(
        html_path
    ), f"{stimulus_class.__name__} failed to generate HTML."

    # 2) Run in a single event loop for this test
    asyncio.run(run_experiment_in_browser(html_path))

    # 3) Clean up
    os.remove(html_path)


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(session, config, items):
    """Dynamically inject the stimuli_list into the parametrize decorator."""
    # Find our test_compile_stimulus item
    for item in items:
        if item.name == "test_compile_stimulus":
            # Retrieve the fixture
            stimuli_list_fixture = session._fixturemanager.getfixturedefs(
                "all_stimuli", item.fspath, item.nodeid
            )[0]
            # Evaluate the fixture to get the stimuli_list
            all_stims = stimuli_list_fixture.cached_result
            if not all_stims:
                all_stims = []
            # Parametrize test_compile_stimulus with each stimulus class
            item.add_marker(pytest.mark.parametrize("stimulus_class", all_stims))
            break
