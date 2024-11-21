# add the stimuli to the __init__.py file

from sweetbean.stimulus._Stimulus import StimulusVar
from sweetbean.stimulus.ImageStimulus import ImageStimulus
from sweetbean.stimulus.ROS import (
    RandomDotPatternsStimulus,
    RandomObjectKinematogramStimulus,
    RDPStimulus,
    ROKStimulus,
)
from sweetbean.stimulus.SurveyStimulus import (
    LikertSurveyStimulus,
    MultiChoiceSurveyStimulus,
    SurveyStimulus,
    TextSurveyStimulus,
)
from sweetbean.stimulus.SymbolStimulus import SymbolStimulus
from sweetbean.stimulus.TextStimulus import (
    BlankStimulus,
    FeedbackStimulus,
    FixationStimulus,
    FlankerStimulus,
    StroopStimulus,
    TextStimulus,
)
from sweetbean.stimulus.VideoStimulus import VideoStimulus
