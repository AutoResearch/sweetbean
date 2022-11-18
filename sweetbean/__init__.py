from typing import List
from sweetbean.primitives import Stimulus, TextStimulus, TrialSequence


class TrialBlock:
    stimuli: List[Stimulus] = []
    sequence: TrialSequence = None

    def __init__(self, stimuli: List[Stimulus], trial_sequence: TrialSequence):
        self.stimuli = stimuli
        for s in self.stimuli:
            s.splice_into_sequence(trial_sequence)
        self.sequence = trial_sequence

    def to_psych(self):
        res = '{timeline: ['
        for s in self.stimuli:
            res += s.to_psych() + ','
        res = res[:-1]
        res += f'], timeline_variables: {self.sequence.to_psych()}' \
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

