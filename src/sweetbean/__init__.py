import shutil
import subprocess
import sys

from sweetbean.block import Block
from sweetbean.experiment import Experiment
from sweetbean.response_spec import (
    KeyboardPressResponseSpec,
    MouseClickResponseSpec,
    ResponseSpecUnion,
)
from sweetbean.stimulus_spec import (
    AssetStimulusSpec,
    RectangleSpec,
    SymbolStimulusSpec,
    StimulusSpecUnion,
    TextStimulusSpec,
    TrialSpec,
    build_html_from_files,
    build_prompt_schema_markdown,
    compile_trial,
    write_prompt_schema_markdown,
)


def check_java():
    """Ensure that Java is installed."""
    java_path = shutil.which("java")
    if java_path is None:
        sys.stderr.write(
            "\nError: Java is required but not found.\n"
            "   Please install Java using one of the following.\n"
        )
        sys.exit(1)


# Run the check immediately when the package is imported.
check_java()

__all__ = [
    "AssetStimulusSpec",
    "Block",
    "Experiment",
    "KeyboardPressResponseSpec",
    "MouseClickResponseSpec",
    "RectangleSpec",
    "ResponseSpecUnion",
    "SymbolStimulusSpec",
    "StimulusSpecUnion",
    "TextStimulusSpec",
    "TrialSpec",
    "build_html_from_files",
    "build_prompt_schema_markdown",
    "compile_trial",
    "write_prompt_schema_markdown",
]
