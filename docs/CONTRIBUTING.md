# Contributor Guide

The SweetBean project is a living project that is always looking for contributors. You can contribute to the project in many ways, for example, but not limited to:

## Reporting Issues

If you find a bug or have a feature request, please don't hesitate to open an issue on the [GitHub Issues](https://github.com/AutoResearch/sweetbean/issues").

## Contributing Code or Documentation

If you want to contribute code, please follow the steps below:

1. Fork the repository.
2. Make your changes.
3. Create a pull request.

## Code

Every part of the codebase is open for contributions. But there are some areas where contributions are especially welcome and easy to make:

### New Stimuli

If you want to implement a new stimulus, you can do so by creating a new class in the `sweetbean/stimulus` directory. You can use the existing template that is available in the `sweetbean/stimulus/_Template_.py` file as guidance. 

The most straight forward stimuli to implement are [jsPsych](https://github.com/jspsych/jsPsych) or [jsPsych-contrib](https://github.com/jspsych/jspsych-contrib) stimuli. Be aware, that SweetBean uses jsPsych 7.3.0 as a backend for the web-based experiments. If you want to implement other stimuli, this is also possible but requires more work. You would first need to implement a stimulus compatible with jsPsych in JavaScript and then create the SweetBean wrapper for it.

### Add Features to Existing Stimuli

In some of the stimuli not all features are implemented. For example, some stimuli don't provide support for running them as language experiments. You can add this feature to the existing stimuli.

## Documentation

Some parts of the documentation are incomplete. You can help by adding more examples or by adding docstrings to the codebase.

### Examples and Use Cases

You can add simple examples that showcase a single stimulus in the `docs\Stimuli` folder. If you want to showcase a more complex use case, you can add a new folder in the `docs\Use Case Tutorials` directory.

## Providing Data and Experiment Examples

If you use SweetBean in your research, consider sharing the raw SweetBean data with us and the community in this [repository](https://github.com/AutoResearch/sweetbean-database). But be aware that your data might be used to train machine learning models. For example, to improve the models that are used as synthetic participants in SweetBean or for coming features such as automatic documentation of the experiment.

## Feedback

If you have any feedback, questions or suggestions you can also reach out to the developers via e-mail: [ystrittmatter@princeton.edu](mailto:ystrittmatter@princeton.edu)