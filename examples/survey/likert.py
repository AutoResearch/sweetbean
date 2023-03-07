from sweetbean.stimulus import TextStimulus, LikertSurveyStimulus
from sweetbean.sequence import Block, Experiment

stim_1 = TextStimulus(
    text='Welcome! We show a survey. Press SPACE to continue',
    choices=[' '],
)

stim_2 = LikertSurveyStimulus(
    prompts=[{'How are you feeling?': [-2, -1, 0, 1, 2]},
             {'Do you like this tool?': [0, 1, 3]}]
)

stim_3 = TextStimulus(
    text='Rate the following animals on a scale from 1-5 on their cuteness.',
    choices=[' ']
)

stim_4 = LikertSurveyStimulus.from_scale(
    prompts=['bunny', 'shark', 'spider', 'cat', 'dog'],
    scale=[1, 2, 3, 4, 5]
)

trial_sequence = Block([stim_1, stim_2, stim_3, stim_4])
experiment = Experiment([trial_sequence])
experiment.to_html('likert.html')
