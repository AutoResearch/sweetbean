jsPsych = initJsPsych();
trials = [
    {
        timeline: [{
            type: jsPsychHtmlKeyboardResponse, trial_duration: "400", stimulus: () => {
                let symbol = () => {
                    if ((jsPsych.timelineVariable('task') === "word_naming")) {
                        return "square"
                    }
                    if ((jsPsych.timelineVariable('task') === "color_naming")) {
                        return "triangle"
                    }
                };
                let color = "white";
                let symbol_class = symbol();
                let c = "sweetbean-" + symbol_class;
                return "<div class='" + c + "' style=" + "'background: " + (symbol() == "triangle" ? "transparent" : color) + (symbol() == "triangle" ? "; border-bottom: solid 10vw " + color : "") + "'></div>"
            }, choices: []
        }, {
            type: jsPsychHtmlKeyboardResponse,
            trial_duration: "500",
            stimulus: "<div>+</div>",
            response_ends_trial: false
        }, {
            type: jsPsychHtmlKeyboardResponse, trial_duration: "2000", stimulus: () => {
                let color = jsPsych.timelineVariable('color');
                let text = jsPsych.timelineVariable('word');
                return "<div style='color: " + color + "'>" + text + '</div>'
            }, choices: ['j', 'n', 'd', 'f'], on_finish: (data) => {
                let correct = () => {
                    if ((jsPsych.timelineVariable('response') === "red")) {
                        return "j"
                    }
                    if ((jsPsych.timelineVariable('response') === "green")) {
                        return "n"
                    }
                    if ((jsPsych.timelineVariable('response') === "yellow")) {
                        return "d"
                    }
                    if ((jsPsych.timelineVariable('response') === "blue")) {
                        return "f"
                    }
                }
                data["correct"] = correct() == data["response"]
            }
        }, {type: jsPsychHtmlKeyboardResponse, trial_duration: "400", stimulus: "", choices: []}],
        timeline_variables: []
    }]
jsPsych.run(trials)