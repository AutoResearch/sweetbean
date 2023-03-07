from sweetbean.stimulus import TextStimulus, MultiChoiceSurveyStimulus
from sweetbean.sequence import Block, Experiment

stim_1 = TextStimulus(
    text='Welcome! We show a survey. Press SPACE to continue',
    choices=[' '],
)

stim_2 = MultiChoiceSurveyStimulus(
    prompts=[{'How are you?': ['bad', 'good', 'fine']},
             {'What is your handedness?': ['left','right','other','prefer not to say']}]
)

trial_sequence = Block([stim_1, stim_2])
experiment = Experiment([trial_sequence])
experiment.to_html('multi_choice.html')
