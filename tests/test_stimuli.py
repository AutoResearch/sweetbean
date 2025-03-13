import asyncio
import importlib
import os
import pkgutil
import platform
import sys

import pytest
from pyppeteer import launch

import sweetbean
from sweetbean import Block, Experiment
from sweetbean.stimulus.Stimulus import _BaseStimulus

EXCLUDES = {
    "SurveyStimulus",
    "_BaseStimulus",
    "_Survey",
    "_KeyboardResponseStimulus",
    "_Template_",
    "Generic",
}

SKIP = {
    "Video": "Requires a video file",
}


def get_stimuli_list():
    """Return all valid stimulus classes from sweetbean.stimulus."""
    stimuli_package = sweetbean.stimulus
    # Dynamically import modules
    for _, module_name, _ in pkgutil.iter_modules(stimuli_package.__path__):
        importlib.import_module(f"sweetbean.stimulus.{module_name}")

    found = []
    for module in sys.modules.values():
        if module and module.__name__.startswith("sweetbean.stimulus"):
            for name, cls in getattr(module, "__dict__", {}).items():
                if (
                    isinstance(cls, type)
                    and issubclass(cls, _BaseStimulus)
                    and cls.__name__ not in EXCLUDES
                ):
                    found.append(cls)

    print("Collected stimuli:", [set(cls.__name__ for cls in found)])
    return list(set(found))


# Collect the stimuli classes once
ALL_STIMULI = get_stimuli_list()


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

    file_url = f"file://{os.path.abspath(html_path)}"
    console_errors = []

    def capture_console(msg):
        if msg.type == "error":
            console_errors.append(msg.text)

    page.on("console", capture_console)

    await page.goto(file_url, options={"timeout": 60000, "waitUntil": "networkidle2"})
    await page.waitForSelector("body")

    title = await page.title()
    assert title == "My awesome experiment", f"Title mismatch: {title}"

    filtered = [
        err
        for err in console_errors
        if "ERR_CERT_VERIFIER_CHANGED" not in err
        and "ERR_SOCKET_NOT_CONNECTED" not in err
    ]

    assert not filtered, f"JS console errors found: {filtered}"

    await browser.close()
    print(f"✅ {html_path} loaded successfully.")


@pytest.mark.parametrize("stimulus_class", ALL_STIMULI, ids=lambda cls: cls.__name__)
def test_compile_stimulus(stimulus_class):
    """Test each stimulus in its own test."""
    # (Optional) skip known heavy stimulus in CI
    # if os.getenv("CI") and stimulus_class.__name__ == "Bandit":
    #     pytest.skip("Skipping Bandit on CI to avoid crashes.")
    # 1) Compile the experiment
    stimulus_instance = stimulus_class()
    experiment = Experiment([Block([stimulus_instance])])
    html_path = "basic.html"
    experiment.to_html(html_path)

    assert os.path.exists(html_path), f"{stimulus_class.__name__} didn't create HTML!"

    # 2) Run the HTML in browser
    if os.getenv("CI") and (
        platform.system() == "Linux" or platform.system() == "Windows"
    ):
        print("Skipping browser test on CI Ubuntu do to limited resources on GitHub.")
    else:
        if stimulus_class.__name__ not in SKIP:
            asyncio.run(run_experiment_in_browser(html_path))
        else:
            print(
                f"Skipping {stimulus_class.__name__} due to: {SKIP[stimulus_class.__name__]}"
            )

    # 3) Cleanup
    os.remove(html_path)


if __name__ == "__main__":
    print([s.__name__ for s in ALL_STIMULI])
    for s in ALL_STIMULI:
        test_compile_stimulus(s)
