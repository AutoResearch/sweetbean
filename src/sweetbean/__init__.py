import shutil
import subprocess
import sys

from sweetbean.block import Block
from sweetbean.experiment import Experiment


def check_java():
    """Ensure that Java 19+ is installed."""
    java_path = shutil.which("java")
    if java_path is None:
        sys.stderr.write(
            "\n❌ Error: Java is required but not found.\n"
            "   Please install Java 19+ using one of the following:\n"
            "   - macOS: brew install openjdk@19\n"
            "   - Ubuntu/Debian: sudo apt install openjdk-19-jdk\n"
            "   - Windows: Download Java from https://jdk.java.net/archive/\n"
        )
        sys.exit(1)

    try:
        output = subprocess.run(
            ["java", "-version"],
            stdout=subprocess.PIPE,  # Use PIPE explicitly
            stderr=subprocess.PIPE,  # Redirect stderr explicitly
            text=True,
        )
        version_line = output.stderr.splitlines()[
            0
        ]  # Java prints version info to stderr
        version = version_line.split('"')[1]
        major_version = int(version.split(".")[0])

        if major_version < 19:
            sys.stderr.write(
                f"\n❌ Error: Java 19+ is required. Found Java {major_version}.\n"
            )
            sys.exit(1)

    except Exception as e:
        sys.stderr.write(f"\n❌ Error: Java is required but could not be checked: {e}\n")
        sys.exit(1)


# Run the check immediately when the package is imported.
check_java()
