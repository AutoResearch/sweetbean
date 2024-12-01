from typing import Any, List

from sweetbean.variable import CodeVariable


class Block:
    stimuli: List[Any] = []
    js = ""
    timeline = None

    def __init__(self, stimuli, timeline=None):
        if timeline is None:
            timeline = []
        self.stimuli = stimuli
        self.timeline = timeline
        # self.to_js()

    def to_js(self):
        self.js = "{timeline: ["
        for s in self.stimuli:
            s.to_js()
            self.js += s.js + ","
        self.js = self.js[:-1]
        if isinstance(self.timeline, CodeVariable):
            self.js += f"], timeline_variables: {self.timeline.name}" + "}"
        else:
            self.js += f"], timeline_variables: {self.timeline}" + "}"
