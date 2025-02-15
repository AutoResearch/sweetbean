# Stimuli

An overview of the stimuli that can be used in SweetBean experiments.

If you are using non-generic stimuli (see bellow), you will not need to import any jsPsych plugins manually and can use all features of SweetBean without any additional setup including running the experiment on language models and exporting stimuli image sequences.


## Generic Stimuli (only in pre-release)

The user can define generic jsPsych stimuli using the Generic Class and the arguments found in the [jsPsych documentation](https://www.jspsych.org//) or on [jsPsych contrib](https://github.com/jspsych/jspsych-contrib). This provides the user with the flexibility to use any jsPsych stimuli in their experiments. However, the user must ensure that the stimuli are imported to their script manually. For example, by adding the following line to the top of their generated html script (replacing `<plugin-name>` with the name of the plugin):

```html
<script src="https://unpkg.com/@jspsych/<plugin-name>"></script>
```

<span style:"color: red">Warning:</span> Generic stimuli do not support running experiments on language models or exporting stimuli image sequences.






