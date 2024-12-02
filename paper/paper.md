---
title: 'SweetBean: A declarative language for behavioral experiments with human and artificial participants'
tags:
  - Python
  - online behavioral experiments
  - large-language model experiments
  - declarative language
  - synthetic participants
authors:
  - name: Younes Strittmatter
    orcid: 0000-0002-3414-2838
    corresponding: true
    affiliation: 1
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

`SweetBean` is an open-source, domain-specific declarative programming language built in Python, designed for the  synthesis of behavioral experiments. It allows researchers to specify experiments once and seamlessly compile them into a `jsPsych` experiment [@de2015jspsych] for conducting studies with human participants or text-based simulations with synthetic participants using large-language models. 

The `SweetBean` package seamlessly integrates with packages aimed at running online behavioral experiments, such as `AutoRA` [@AUTORA-MISSING] for automated research, participant recruitment, and data collection, and `SweetPea` [@musslick2020sweetpea] for experimental design. 

# Statement of need

The design and implementation of behavioral experiments often involve complex workflows, particularly when researchers aim to run the same experiments with both human participants and large-language models—a practice that is becoming increasingly common, for example, to train models to simulate human behavior [@demircan2024evaluating] or to support AI alignment research. While platforms like `jsPsych` offer powerful solutions for running online experiments, they require knowledge of *JavaScript*, which poses a significant barrier for researchers without programming expertise. Additionally, integrating synthetic participants, such as large-language models, often necessitates ad hoc solutions, leading to inefficiencies and errors due to the need for replicating the same experiment across different codebases.

`SweetBean` offers a *Python*-based, declarative programming language specifically designed for behavioral experiment design. Python’s accessibility and widespread use in the behavioral sciences make `SweetBean` an ideal tool for researchers and educators. By enabling users to specify experiments in a single, concise format, SweetBean simplifies workflows and ensures compatibility with both human and synthetic participants.

Beyond reducing technical barriers, `SweetBean` enhances reproducibility and collaboration by standardizing experiment specifications within a flexible and intuitive framework. This standardization not only saves time but also fosters more robust and scalable experimental workflows for the research community.

# References