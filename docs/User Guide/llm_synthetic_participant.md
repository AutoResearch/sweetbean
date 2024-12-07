# LLM - Synthetic Participant

SweetBean can be used to run experiments with Large Language Models (LLMs) as synthetic participants.

We specify the experiment as above:

```python
from sweetbean import Block, Experiment
from sweetbean.stimulus import Text
from sweetbean.variable import TimelineVariable, DataVariable, FunctionVariable

# TIMELINE
timeline = [
    {"color": "red", "word": "RED", "correct_key": "f"},
    {"color": "green", "word": "GREEN", "correct_key": "j"},
    {"color": "green", "word": "RED", "correct_key": "f"},
    {"color": "red", "word": "GREEN", "correct_key": "j"},
]

# EVENT SEQUENCE

color = TimelineVariable("color")
word = TimelineVariable("word")


def correct_key_fct(col):
    if col == "red":
        return "f"
    elif col == "green":
        return "j"


correct_key = FunctionVariable("correct", correct_key_fct, [color])

# Creating a data variable
correct = DataVariable("correct", 2)


# Predicates
def feedback_text_fct(was_correct):
    if was_correct:
        return "That was correct!"
    else:
        return "That was false!"


feedback_text = feedback_text_fct("feedback_text", feedback_text_fct, [correct])

# Using it in the stimulus
fixation = Text(1000, "+")

so_s = Text(400)
stroop = Text(2000, word, color, ["j", "f"], correct_key)
so_f = Text(300)
feedback = Text(800, feedback_text)

event_sequence = [fixation, so_s, stroop, so_f, feedback]

# BLOCK DESIGN

train_block = Block(event_sequence, timeline)
experiment = Experiment([train_block])
```

To test what the LLM "sees", we can run the experiment as chat on ourselves. If we set ``multiturn`` to true we will not see
the full chat history but only the last generated prompt.

```python
data = experiment.run_on_language(get_input=input)
```

We can run the experiment on any function that takes a string and returns a string. For example, on the
[centauer](https://marcelbinz.github.io/centaur) model:

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
    return pipe(input)[0]["generated_text"][len(input):]
```

Now, we can run the experiment on the model:

```python
data = experiment.run_on_language(get_input=generate)
```

**Note**: The `run_on_language` function will return a dictionary with the data from the experiment. Any model
(for example, using [OpenAI](https://platform.openai.com/docs/overview), [HuggingFace](https://huggingface.co/), [LLama](https://www.llama-api.com/), or [Google](https://console.cloud.google.com/apis/library) API) can be used as a synthetic participant. In addition to responses from the language model, [here](https://autoresearch.github.io/sweetbean/Use%20Case%20Tutorials/AI%20Alignment/Reinforcement%20Learning%20with%20Model%20Confidence/), you can find how to assess other metrics like certainty of the language model.

