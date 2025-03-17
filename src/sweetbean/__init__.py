import shutil
import subprocess
import sys

from sweetbean.block import Block
from sweetbean.experiment import Experiment


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
