from sweetbean import Block, Experiment
from sweetbean.stimulus import HtmlChoice

choice = HtmlChoice(
    duration=2000,
    html_array=["<button>Yes</button>", "<button>No</button>"],
    values=[1, 0],
    time_after_response=300,
)

block = Block([choice])

# Create HTML file of the experiment
experiment = Experiment([block])
experiment.to_html("htmlChoice.html")
