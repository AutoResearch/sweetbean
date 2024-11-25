# SweetBean

SweetBean is an
open-source [domain-specific programming language](https://en.wikipedia.org/wiki/Domain-specific_language) in Python,
designed for the declarative specification of stimuli sequences and the synthesis of online [jsPsych](https://www.jspsych.org/) behavioral experiments. With SweetBean,
researchers can conveniently specify experiments once and then compile them into a jsPsych experiment for **human participants** or text-based experiment for **synthetic
participants** (e.g., large-language models).

## Why SweetBean?

In recent years, crowd-sourced online experiments have gained immense popularity across behavioral sciences like
cognitive psychology, social psychology, and behavioral economics. These experiments offer several advantages, such as:

- Faster data collection: gather large datasets in a fraction of the time required for in-person studies at the lab.
- Increased accessibility: access participants from diverse populations globally.

Despite these benefits, the process of designing and implementing online experiments remains time-consuming and
error-prone. Existing tools like [jsPsych](https://www.jspsych.org/latest/) have made strides in simplifying this
process, but there's still a need for a more intuitive solution, in particular for researchers who don't have a background in programming in Java Script. We address this need with SweetBean.

- Declarative language in Python: easily specify the structure and flow of experiments, even with minimal programming experience.
- Synthetic participant support: Integrate [large-language models as synthetic participants](https://www.sciencedirect.com/science/article/pii/S1364661323000980) for pilot studies, generating synthetic data
  to test hypotheses or fine-tune models.

## Overview

- [Quickstart Guide](Quickstart%20Guide/index.md) A quick start guide to get you started with SweetBean.
- [User Guide](User%20Guide/index.md) An overview of SweetBean features.
- [Stimuli](Stimuli/index.md) An overview of the different stimuli that can be used in SweetBean.
- [Code References](reference/sweetbean/) A reference guide to the different classes and functions in SweetBean.

## SweetBean is Growing

![word-cloud](img/word-cloud.png){:.center}
Our philosophy is rooted in continuous evolution and user-driven development. The initial set of features was based on a
word cloud to identify frequently used features of behavioral experiments, but we are always adding new features and stimuli based on the needs of
our team and collaborators. If you have any suggestions or feature requests, please feel free to reach out to us via
e-mail ([ystrittmatter@princeton.edu](mailto: ystrittmatter@princeton.edu)) or create an issue on our GitHub repository
([https://github.com/AutoResearch/sweetbean/issues](https://github.com/AutoResearch/sweetbean/issues)). We are
constantly seeking feedback and looking for ways to improve the language.

### Coming Soon

{{ include_file('docs/Announcement.md') }}

## Discover More from Our Suite of Tools

SweetBean is just one part of a powerful set of tools designed to streamline and enhance your research process. It can be used as a standalone product but is most powerful when used in conjunction with our other tools:

- [SweetPea](https://sweetpea.ai/): A Python toolbox for the automated generation of **counterbalanced experimental design** similar syntax to SweetBean. Create complex counterbalanced sequences with SweetPea and then use SweetBean to implement them in online experiments.

- [AutoRA](https://autoresearch.github.io/autora/): A Python platform for **automated behavioral research**, helping you design, execute and analyze behavioral experiments in a closed loop. Experiments created with SweetBean can be implemented via AutoRA to collect data from real participants. Even if you are not planning to automate your research in a closed loop, AutoRA can help you to set up and run experiments without the need of a server and collect data from real participants via [Prolific](https://www.prolific.com/).

## About

This project is in active development by
the [Autonomous Empirical Research Group](https://musslick.github.io/AER_website/Research.html), Lead
Designer [Younes Strittmatter](https://younesstrittmatter.github.io/), led
by [Sebastian Musslick](https://smusslick.com).

This research program was supported by Schmidt Science Fellows, in partnership with the Rhodes Trust, as well as the
Carney BRAINSTORM program at Brown University.

