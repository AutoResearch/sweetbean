from sweetbean.stimulus import TextStimulus, SymbolStimulus, TextSurveyStimulus
from sweetbean import TrialBlock, Experiment


stim_1 = TextStimulus(
    text='Welcome! We show a survey. Press SPACE to continue',
    choices=[' '],
)

stim_2 = TextSurveyStimulus(
    prompts=['How old are you?', 'What is your gender?', 'What is your handedness?']
)


trial_sequence = TrialBlock([stim_1, stim_2])
experiment = Experiment([trial_sequence])
experiment.to_html('index.html')

