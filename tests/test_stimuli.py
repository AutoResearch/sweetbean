import importlib
import os
import pkgutil

import sweetbean
from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus._Stimulus import Stimulus  # Base Stimulus class for comparison

# Define the excluded stimuli
excludes = [
    "Stimulus",
    "SurveyStimulus",
]


def test_compile():
    # Dynamically load all modules in the 'sweetbean.stimulus' package
    stimuli_package = sweetbean.stimulus
    for _, module_name, _ in pkgutil.iter_modules(stimuli_package.__path__):
        importlib.import_module(f"sweetbean.stimulus.{module_name}")

    # Gather all subclasses of Stimulus
    stimuli_list = [
        cls
        for cls in globals().values()
        if isinstance(cls, type)
        and issubclass(cls, Stimulus)
        and cls.__name__ not in excludes
    ]

    for stimulus in stimuli_list:
        try:
            # Log which stimulus is being tested
            print(f"Testing {stimulus.__name__}...")

            # Test each stimulus
            stimulus_instance = stimulus()  # Adjust if parameters are required
            trial_sequence = Block([stimulus_instance])
            experiment = Experiment([trial_sequence])
            experiment.to_html("basic.html")
            print(f"{stimulus.__name__} compiled successfully.")
        except Exception as e:
            print(f"Error testing {stimulus.__name__}: {e}")
        finally:
            # Clean up generated files
            if os.path.exists("basic.html"):
                os.remove("basic.html")
            else:
                raise FileNotFoundError("basic.html not created.")
