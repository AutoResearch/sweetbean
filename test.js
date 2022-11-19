jsPsych = initJsPsych();
trials = [
    {
        timeline: [{
            type: jsPsychHtmlKeyboardResponse, trial_duration: "500", stimulus: () => {
                return "<div style='color: " + "white" + "'>" + jsPsych.timelineVariable('fixation_shape') + '</div>'
            }, choices: [], on_finish: (data) => {
                data["correct"] = "" == data["response"]
            }
        }, {
            type: jsPsychHtmlKeyboardResponse, trial_duration: "2000", stimulus: "", response_ends_trial: () => {
                if ("j") {
                    return true;
                } else {
                    return true;
                }
            }, choices: ['j', 'f'], on_finish: (data) => {
                data["correct"] = "j" == data["response"]
            }
        }, {
            type: jsPsychHtmlKeyboardResponse, trial_duration: () => {
                let last_trial_correct = jsPsych.data.get().last(1).values()[0].correct;
                if ((true && last_trial_correct) || !last_trial_correct) {
                    return "2000"
                } else {
                    return 0
                }
            }, stimulus: () => {
                let last_trial_correct = jsPsych.data.get().last(1).values()[0].correct;
                if (last_trial_correct) {
                    if (true) {
                        if ("screen" == "message") {
                            return "<div class='feedback'>Correct!</div>";
                        } else if ("screen" == "screen") {
                            return "<div class='feedback-screen-green'></div>";
                        }
                    } else {
                        return ""
                    }
                } else {
                    let last_trial_response = jsPsych.data.get().last(1).values()[0].response;
                    if (last_trial_response) {
                        if ("screen" == "message") {
                            return "<div class='feedback'>Wrong!</div>";
                        } else if ("screen" == "screen") {
                            return "<div class='feedback-screen-red'></div>";
                        }
                    } else {
                        if ("screen" == "message") {
                            return "<div class='feedback'>Too slow!</div>";
                        } else if ("screen" == "screen") {
                            return "<div class='feedback-screen-red'></div>";
                        }
                    }
                }
            }, response_ends_trial: false
        }],
        timeline_variables: [{
            'task': 'word_reading',
            'word': 'red',
            'color': 'red',
            'correct': 'f',
            'soa': 2000,
            'direction': 'left',
            'congruency': 'congruent',
            'symbol': 'square',
            'fixation_shape': 'x'
        }, {
            'task': 'color_naming',
            'word': 'green',
            'color': 'green',
            'correct': 'j',
            'soa': 1000,
            'direction': 'right',
            'congruency': 'incocngruent',
            'symbol': 'circle',
            'fixation_shape': '+'
        }, {
            'task': 'word_reading',
            'word': 'green',
            'color': 'red',
            'correct': 'j',
            'soa': 500,
            'direction': 'right',
            'congruency': 'incongruent',
            'symbol': 'triangle',
            'fixation_shape': 'x'
        }, {
            'task': 'color_naming',
            'word': 'red',
            'color': 'green',
            'correct': 'f',
            'soa': 1500,
            'direction': 'left',
            'congruency': 'congruent',
            'symbol': 'square',
            'fixation_shape': '+'
        }, {
            'task': 'word_reading',
            'word': 'green',
            'color': 'red',
            'correct': 'j',
            'soa': 500,
            'direction': 'right',
            'congruency': 'incongruent',
            'symbol': 'triangle',
            'fixation_shape': 'x'
        }, {
            'task': 'color_naming',
            'word': 'red',
            'color': 'green',
            'correct': 'f',
            'soa': 1500,
            'direction': 'left',
            'congruency': 'congruent',
            'symbol': 'circle',
            'fixation_shape': '+'
        }]
    }]
jsPsych.run(trials)