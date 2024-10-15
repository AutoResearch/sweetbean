const jsPsych = initJsPsych()
const trials = [{
    timeline: [{
        type: jsPsychHtmlKeyboardResponse, trial_duration: () => {
            let duration = 800;
            return duration
        }, stimulus: () => {
            let text = "+";
            let color = "white";
            return "<div style='color: " + color + "'>" + text + "</div>"
        }, choices: () => {
            let choices = [];
            return choices
        }, on_finish: (data) => {
            data["bean_type"] = 'jsPsychHtmlKeyboardResponse';
            let duration = 800;
            data["bean_duration"] = duration;
            let text = "+";
            data["bean_text"] = text;
            let color = "white";
            data["bean_color"] = color;
            let choices = [];
            data["bean_choices"] = choices;
            let correct_key = "";
            data["bean_correct_key"] = correct_key;
            data["bean_correct"] = correct_key == data["response"]
        }
    }, {
        type: jsPsychHtmlKeyboardResponse, trial_duration: () => {
            let duration = 400;
            return duration
        }, stimulus: () => {
            let text = "";
            let color = "white";
            return "<div style='color: " + color + "'>" + text + "</div>"
        }, choices: () => {
            let choices = [];
            return choices
        }, on_finish: (data) => {
            data["bean_type"] = 'jsPsychHtmlKeyboardResponse';
            let duration = 400;
            data["bean_duration"] = duration;
            let text = "";
            data["bean_text"] = text;
            let color = "white";
            data["bean_color"] = color;
            let choices = [];
            data["bean_choices"] = choices;
            let correct_key = "";
            data["bean_correct_key"] = correct_key;
            data["bean_correct"] = correct_key == data["response"]
        }
    }, {
        type: jsPsychRok, trial_duration: () => {
            let duration = 2000;
            return duration
        }, number_of_oobs: () => {
            let number_of_oobs = [jsPsych.timelineVariable('S1'), jsPsych.timelineVariable('S2'),];
            return number_of_oobs
        }, number_of_apertures: () => {
            let number_of_apertures = 2;
            return number_of_apertures
        }, coherent_movement_direction: () => {
            let coherent_movement_direction = 0;
            return coherent_movement_direction
        }, coherence_movement: () => {
            let coherence_movement = 0;
            return coherence_movement
        }, coherence_orientation: () => {
            let coherence_orientation = 0;
            return coherence_orientation
        }, oob_color: () => {
            let oob_color = "white";
            return oob_color
        }, background_color: () => {
            let background_color = "grey";
            return background_color
        }, movement_speed: () => {
            let movement_speed = 0;
            return movement_speed
        }, aperture_position_left: () => {
            let aperture_position_left = 50;
            return aperture_position_left
        }, aperture_position_top: () => {
            let aperture_position_top = 50;
            return aperture_position_top
        }, stimulus_type: () => {
            let stimulus_type = 1;
            return stimulus_type
        }, correct_choice: () => {
            let correct_key = "";
            return [correct_key]
        }, choices: () => {
            let choices = ["y", "n",];
            return choices
        }, on_finish: (data) => {
            data["bean_type"] = 'jsPsychRok';
            let duration = 2000;
            data["bean_duration"] = duration;
            let number_of_oobs = [jsPsych.timelineVariable('S1'), jsPsych.timelineVariable('S2'),];
            data["bean_number_of_oobs"] = number_of_oobs;
            let number_of_apertures = 2;
            data["bean_number_of_apertures"] = number_of_apertures;
            let coherent_movement_direction = 0;
            data["bean_coherent_movement_direction"] = coherent_movement_direction;
            let coherence_movement = 0;
            data["bean_coherence_movement"] = coherence_movement;
            let coherence_orientation = 0;
            data["bean_coherence_orientation"] = coherence_orientation;
            let oob_color = "white";
            data["bean_oob_color"] = oob_color;
            let background_color = "grey";
            data["bean_background_color"] = background_color;
            let movement_speed = 0;
            data["bean_movement_speed"] = movement_speed;
            let aperture_position_left = 50;
            data["bean_aperture_position_left"] = aperture_position_left;
            let aperture_position_top = 50;
            data["bean_aperture_position_top"] = aperture_position_top;
            let stimulus_type = 1;
            data["bean_stimulus_type"] = stimulus_type;
            let choices = ["y", "n",];
            data["bean_choices"] = choices;
            let correct_key = "";
            data["bean_correct_key"] = correct_key;
            data["bean_correct"] = data["correct"]
        }
    }, {
        type: jsPsychHtmlKeyboardResponse, trial_duration: () => {
            let duration = 1000;
            return duration
        }, stimulus: () => {
            let text = "";
            let color = "white";
            return "<div style='color: " + color + "'>" + text + "</div>"
        }, choices: () => {
            let choices = [];
            return choices
        }, on_finish: (data) => {
            data["bean_type"] = 'jsPsychHtmlKeyboardResponse';
            let duration = 1000;
            data["bean_duration"] = duration;
            let text = "";
            data["bean_text"] = text;
            let color = "white";
            data["bean_color"] = color;
            let choices = [];
            data["bean_choices"] = choices;
            let correct_key = "";
            data["bean_correct_key"] = correct_key;
            data["bean_correct"] = correct_key == data["response"]
        }
    }],
    timeline_variables: [{'S1': 74.0, 'S2': 75.0}, {'S1': 74.0, 'S2': 75.0}, {'S1': 75.0, 'S2': 75.0}, {
        'S1': 74.0,
        'S2': 74.0
    }, {'S1': 74.0, 'S2': 74.0}, {'S1': 74.0, 'S2': 75.0}, {'S1': 75.0, 'S2': 75.0}, {
        'S1': 74.0,
        'S2': 74.0
    }, {'S1': 75.0, 'S2': 75.0}, {'S1': 75.0, 'S2': 74.0}]
}]
runExperiment = jsPsych.run(trials)