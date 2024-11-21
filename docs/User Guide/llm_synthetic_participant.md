# LLM - Synthetic Participant

SweetBean can be used to run experiments with Large Language Models (LLMs) as synthetic participants.

We specify the experiment as above:

```python
from sweetbean.sequence import Block, Experiment
from sweetbean.stimulus import TextStimulus
from sweetbean.parameter import TimelineVariable, DataVariable, DerivedLevel, DerivedParameter

# TIMELINE
timeline = [
    {"color": "red", "word": "RED", "correct_key": "f"},
    {"color": "green", "word": "GREEN", "correct_key": "j"},
    {"color": "green", "word": "RED", "correct_key": "f"},
    {"color": "red", "word": "GREEN", "correct_key": "j"},
]

# EVENT SEQUENCE

color = TimelineVariable("color", ["red", "green"])
word = TimelineVariable("word", ["RED", "GREEN"])


def is_correct_f(color):
    return color == "red"


def is_correct_j(color):
    return not is_correct_f(color)


j_key = DerivedLevel("j", is_correct_j, [color])
f_key = DerivedLevel("f", is_correct_f, [color])

correct_key = DerivedParameter("correct", [j_key, f_key])

# Creating a data variable
correct = DataVariable("correct", [True, False])


# Predicates
def is_correct(correct):
    return correct


def is_false(correct):
    return not correct


# Derived Levels
correct_feedback = DerivedLevel("correct", is_correct, [correct], 2)
false_feedback = DerivedLevel("false", is_false, [correct], 2)

# Derived Parameter
feedback_text = DerivedParameter("feedback_text", [correct_feedback, false_feedback])

# Using it in the stimulus
fixation = TextStimulus(1000, "+")

so_s = TextStimulus(400)
stroop = TextStimulus(2000, word, color, ["j", "f"], correct_key)
so_f = TextStimulus(300)
feedback = TextStimulus(800, feedback_text)

event_sequence = [fixation, so_s, stroop, so_f, feedback]

# BLOCK DESIGN

train_block = Block(event_sequence, timeline)
experiment = Experiment([train_block])
```

To test what the LLM "sees", we can run the experiment as chat on ourselves. If we set multitude to true we will not see
the full chat history but only the last generated prompt.

```python
data = experiment.run_on_language(get_input=input, multiturn=True)
```

We can run the experiment on any function that takes a string and returns a string. For example, on the
[centauer]() model:

```bash
pip install unsloth "xformers==0.0.28.post2"
```

We then define a function that generates the next token given a prompt:

```python
from unsloth import FastLanguageModel
import transformers

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="marcelbinz/Llama-3.1-Centaur-8B-adapter",
    max_seq_length=32768,
    dtype=None,
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)

pipe = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    trust_remote_code=True,
    pad_token_id=0,
    do_sample=True,
    temperature=1.0,
    max_new_tokens=1,
)


def generate(input):
    return pipe(input)[0]["generated_text"]
```

To make the process more robust, we also add a function that parses the response and compares the output to the
correct key:

```python
def parse_response(response, correct_key):
    return correct_key in response
```

Now, we can run the experiment on the model:

```python
data = experiment.run_on_language(get_input=generate, multiturn=False)
```

**Note**: The `run_on_language` function will return a dictionary with the data from the experiment. Any model
(for example,
using [OpenAI](https://platform.openai.com/docs/overview), [HuggingFace](https://huggingface.co/), [LLama](https://www.llama-api.com/)
or [Google](https://console.cloud.google.com/apis/library) Api) can be used as a synthetic participant.

