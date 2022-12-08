from typing import List
from sweetbean.primitives import Stimulus, TrialSequence


class TrialBlock:
    stimuli: List[Stimulus] = []
    sequence: TrialSequence = None

    def __init__(self, stimuli: List[Stimulus]):
        self.stimuli = stimuli

    def to_psych(self):
        res = '{timeline: ['
        for s in self.stimuli:
            res += s.to_psych() + ','
        res = res[:-1]
        res += f'], timeline_variables: []' \
               '}'
        return res


class Experiment:
    blocks: List[TrialBlock] = []
    def __init__(self, blocks: List[TrialBlock]):
        self.blocks = blocks

    def to_psych(self):
        res = 'jsPsych = initJsPsych();\n' \
              'trials = [\n'
        for b in self.blocks:
            res += b.to_psych()
            res += ','
        res = res[:-1] + ']\n'
        res += 'jsPsych.run(trials)'
        return res


