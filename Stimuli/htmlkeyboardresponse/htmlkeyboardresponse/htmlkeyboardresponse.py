from sweetbean import Block, Experiment
from sweetbean.stimulus import HtmlKeyboardResponse

stim = HtmlKeyboardResponse(
    duration=2000,
    stimulus="<p style='font-size:48px; color:pink'>Hello, World!</p>",
)

block = Block([stim])
experiment = Experiment([block])
experiment.to_html("htmlkeyboardresponse.html")
