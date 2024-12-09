---
title: 'SweetBean: A declarative language for behavioral experiments with human and artificial participants'
tags:
  - Python
  - online behavioral experiments
  - large language model experiments
  - declarative language
  - synthetic participants
authors:
  - name: Younes Strittmatter
    orcid: 0000-0002-3414-2838
    corresponding: true
    affiliation: "1, 3"
  - name: Sebastian Musslick
    orcid: 0000-0002-8896-639X
    affiliation: "2, 3"
affiliations:
  - name: Princeton University, USA
    index: 1
  - name: Osnabrück University, Germany
    index: 2
  - name: Brown University, USA
    index: 3
date: 13 August 2017
bibliography: paper.bib

---

# Summary

`sweetbean` is an open-source, domain-specific declarative programming language built in Python, designed to simplify the synthesis of web-based behavioral experiments. It allows researchers to specify a behavioral experiment in declarative form as a sequence events. Once specified, `sweetbean` can compile the experiment into a `jsPsych` experiment [@de2015jspsych] for web-based behavioral study with human participants. In addition, `sweetbean` can generate prompts for conducting the same experiment with a large language model (LLM), enabling automated alignment of LLMs with human behavior.

The `sweetbean` package integrates with other tools that automate aspects of behavioral research, such as `sweetpea` [@musslick2020sweetpea] for automating experimental design, or `autora` [@autora2024] for running closed-loop behavioral research studies. Together, these tools form an ecosystem for advancing behavioral research through automation.

# Statement of need

The generation and execution of web-based experiments is a common task in the behavioral sciences. However, the process of designing and implementing such experiments can difficult, especially if researchers don't have a background in web development.  While platforms like `jsPsych` offer powerful solutions for running online experiments, they require knowledge of *JavaScript*, which poses a significant barrier for researchers without programming expertise.  Other platforms, like `PsychoPy` [@peirce2019psychopy2], have made significant strides in addressing this issue by creating `PsychJS` which allows the translation of experiments created with in Python code or the `PsychoPy Builder` into JavaScript for online deployment.  However, `PsychoPy` is not specifically tailored for creating online JavaScript experiments, which can sometimes result in compatibility issues and unsupported `PsychoPy` components.  `sweetbean` aims to simplify the process of generating online experiments by providing a high-level, declarative language for specifying experiments in Python. By abstracting away the details of web development, `sweetbean` allows researchers to focus on the specification of the experiment itself, rather than the implementation details.

Another challenge in behavioral research is the integration of LLMs into the experimental workflow. LLMs have the potential to simulate human behavior in a variety of tasks, making them valuable simulators for behavioral experiments [@dillion2023can; manning2024automated; binz2024centaur]. Accordingly, researchers are increasingly interested in aligning the behavior of LLMs with human participants, calling for the development of tools that facilitate this alignment. `sweetbean` addresses this challenge by providing a way to generate prompts for LLMs based on the same experiment specification used for human participants. This allows researchers to easily compare the behavior of LLMs to human participants, to align LLMs with human behavior, and to use LLMs to generate synthetic behavioral data for training or evaluation purposes.

Beyond reducing technical barriers and facilitating alignment between machines and humans, `sweetbean` enhances reproducibility and collaboration by standardizing experiment specifications within a flexible and intuitive framework. This standardization not only saves time but also provides more robust and scalable experimental workflows for the behavioral research community.

# Acknowledgements
Y. S. and S.M. were supported by the Carney BRAINSTORM program at Brown University, as well as the National Science Foundation (2318549). S. M. also received support from Schmidt Science Fellows, in partnership with the Rhodes Trust.

# References