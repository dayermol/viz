"""A basic T and L visual search experiment.

Author - Colin Quirk (cquirk@uchicago.edu)

Repo: https://github.com/colinquirk/PsychopyVisualSearch

T and L search is a common attention paradigm. Unlike other visual search tasks, this task
forces participants to search serially, resulting in increasing RT with set size
(e.g. Wolfe, Cave, Franzel, 1989). If this file is run directly, the defaults at the top of the
page will be used. To make simple changes, you can adjust any of these values. For more in depth
changes you will need to overwrite the methods yourself.

Note: this code relies on my templateexperiments module. You can get it from
https://github.com/colinquirk/templateexperiments and either put it in the same folder as this
code or give the path to psychopy in the preferences.

Classes:
TLTask -- The class that runs the experiment.
    See 'print TLTask.__doc__' for simple class docs or help(TLTask) for everything.
"""

import errno
import json
import os
import random
import sys
import time

import numpy as np

import psychopy.core
import psychopy.event
import psychopy.visual

import template

# Things you probably want to change
exp_name = 'VisualSearch'

number_of_trials_per_block = 10
number_of_blocks = 2

set_sizes = [2, 6, 10, 14, 18]

instruct_text = [
    ('Welcome to the experiment. Press space to begin.'),
    ('In this experiment you will see a set of faces and will be asked yes/no questions.\n\n'
     'You will first see a target face and then an array of faces.\n\n'
     'After seeing the array of faces, you will be asked whether \n\n'
     'The "T" can appear in any orientation.\n\n'
     'Once you find the "T", press the arrow key associated with the top of the "T".\n\n'
     'For example, if the "T" looks normal, you would press the up arrow key.\n\n'
     'If the top of the T is pointed to the left, you would press the left arrow key.\n\n'
     'You will get breaks in between blocks.\n\n'
     'Press space to continue.'),
]

data_directory = os.path.join(os.getcwd(), 'data')
# Feel free to hardcode to your system if this file will be imported
stim_path = os.path.join(os.getcwd(), 'stimuli/visual')

# Things you probably don't need to change, but can if you want to
stim_size = 1.5 # visual degrees, used for X and Y
#originally size 1, changed to 1.5, 7/6/23

possible_orientations = ['left', 'up', 'right', 'down']
keys = ['left', 'up', 'right', 'down']  # keys indexes should match with possible_orientations

allowed_deg_from_fix = 6
# minimum euclidean distance between centers of stimuli in visual angle
# min_distance should be greater than stim_size
min_distance = 2
max_per_quad = None  # int or None for totally random displays

iti_time = 1  # seconds
response_time_limit = None  # None or int in seconds

distance_to_monitor = 90  # cm

# data_fields must match input to send_data
data_fields = [
    'Subject',
    'Block',
    'Trial',
    'Timestamp',
    'SetSize',
    'RT',
    'CRESP',
    'RESP',
    'ACC',
    'LocationTested',
    'Locations',
    'Rotations',
    'Stimuli'
]

gender_options = [
    'Male',
    'Female',
    'Other/Choose Not To Respond',
]

hispanic_options = [
    'Yes, Hispanic or Latino/a',
    'No, not Hispanic or Latino/a',
    'Choose Not To Respond',
]

race_options = [
    'American Indian or Alaskan Native',
    'Asian',
    'Pacific Islander',
    'Black or African American',
    'White / Caucasian',
    'More Than One Race',
    'Choose Not To Respond',
]

# Add additional questions here
questionaire_dict = {
    'Age': 0,
    'Gender': gender_options,
    'Hispanic:': hispanic_options,
    'Race': race_options,
}


# This is the logic that runs the experiment
# Change anything below this comment at your own risk
class TLTask(template.BaseExperiment):
    """The class that runs the visual search experiment.

    Parameters:
    allowed_deg_from_fix -- The maximum distance in visual degrees the stimuli can appear from
        fixation
    data_directory -- Where the data should be saved.
    instruct_text -- The text to be displayed to the participant at the beginning of the
        experiment.
    iti_time -- The number of seconds in between a response and the next trial.
    keys -- The keys to be used for making a response. Should match possible_orientations.
    max_per_quad -- The number of stimuli allowed in each quadrant. If None, displays are
        completely random. Useful for generating more "spread out" displays
    min_distance -- The minimum distance in visual degrees between stimuli.
    number_of_blocks -- The number of blocks in the experiment.
    number_of_trials_per_block -- The number of trials within each block.
    possible_orientations -- A list of strings possibly including "left", "up", "right", or "down"
    questionaire_dict -- Questions to be included in the dialog.
    response_time_limit -- How long in seconds the participant has to respond.
    set_sizes -- A list of all the set sizes. An equal number of trials will be shown for each set
        size.
    stim_path -- A string containing the path to the stim folder
    stim_size -- The size of the stimuli in visual angle.
    Additional keyword arguments are sent to template.BaseExperiment().

    Methods:
    chdir -- Changes the directory to where the data will be saved.
    display_break -- Displays a screen during the break between blocks.
    display_blank -- Displays a blank screen.
    display_search -- Displays the search array.
    generate_locations -- Helper function that generates locations for make_trial
    get_response -- Waits for a response from the participant.
    make_block -- Creates a block of trials to be run.
    make_trial -- Creates a single trial.
    run_trial -- Runs a single trial.
    run -- Runs the entire experiment.
    send_data -- Updates the experiment data with the information from the last trial.
    """

    def __init__(self, number_of_trials_per_block=number_of_trials_per_block,
                 number_of_blocks=number_of_blocks, set_sizes=set_sizes, stim_size=stim_size,
                 possible_orientations=possible_orientations, keys=keys, stim_path=stim_path,
                 allowed_deg_from_fix=allowed_deg_from_fix, min_distance=min_distance,
                 max_per_quad=max_per_quad, instruct_text=instruct_text, iti_time=iti_time,
                 data_directory=data_directory, questionaire_dict=questionaire_dict,
                 response_time_limit=response_time_limit, **kwargs):

        self.number_of_trials_per_block = number_of_trials_per_block
        self.number_of_blocks = number_of_blocks

        self.set_sizes = set_sizes

        self.stim_size = stim_size

        self.possible_orientations = possible_orientations
        self.keys = keys

        self.response_time_limit = response_time_limit

        if len(self.keys) != len(self.possible_orientations):
            raise ValueError('Length of keys and possible_orientations must be equal.')

        self.allowed_deg_from_fix = allowed_deg_from_fix
        self.min_distance = min_distance
        self.max_per_quad = max_per_quad

        self.instruct_text = instruct_text

        self.iti_time = iti_time

        self.data_directory = data_directory
        self.questionaire_dict = questionaire_dict

        self.BF1A_stim_path = os.path.join(stim_path, 'BF1A.jpg')
        self.BF1H_stim_path = os.path.join(stim_path, 'BF1H.jpg')
        self.BF2A_stim_path = os.path.join(stim_path, 'BF2A.jpg')
        self.BF2H_stim_path = os.path.join(stim_path, 'BF2H.jpg')
        self.BM1A_stim_path = os.path.join(stim_path, 'BM1A.jpg')
        self.BM1H_stim_path = os.path.join(stim_path, 'BM1H.jpg')
        self.BM2A_stim_path = os.path.join(stim_path, 'BM2A.jpg')
        self.BM2H_stim_path = os.path.join(stim_path, 'BM2H.jpg')
        self.WF1A_stim_path = os.path.join(stim_path, 'WF1A.jpg')
        self.WF1A_stim_path = os.path.join(stim_path, 'WF1H.jpg')
        self.WF2A_stim_path = os.path.join(stim_path, 'WF2A.jpg')
        self.WF2H_stim_path = os.path.join(stim_path, 'WF2H.jpg')
        self.WM1A_stim_path = os.path.join(stim_path, 'WM1A.jpg')
        self.WM1H_stim_path = os.path.join(stim_path, 'WM1H.jpg')
        self.WM2A_stim_path = os.path.join(stim_path, 'WM2A.jpg')
        self.WM2H_stim_path = os.path.join(stim_path, 'WM2H.jpg')

        self.trials_per_set_size = number_of_trials_per_block / len(set_sizes)

        if self.trials_per_set_size % 1 != 0:
            raise ValueError('number_of_trials_per_block must be divisible by len(set_sizes).')

        self.trials_per_set_size = int(self.trials_per_set_size)

        super().__init__(**kwargs)

    def chdir(self):
        """Changes the directory to where the data will be saved."""

        try:
            os.makedirs(self.data_directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        os.chdir(self.data_directory)

    def make_block(self):
        """Makes a block of trials.

        Returns a shuffled list of trials created by self.make_trial.
        """
        trial_list = []

        for set_size in self.set_sizes:
            for _ in range(self.trials_per_set_size):
                trial = self.make_trial(set_size)
                trial_list.append(trial)

        random.shuffle(trial_list)

        return trial_list

    @staticmethod
    def _which_quad(loc):
        """Checks which quad a location is in.

        This method is used by generate_locations to ensure the max_per_quad condition is followed.

        Parameters:
        loc -- A list of two values (x,y) in visual angle.
        """
        if loc[0] < 0 and loc[1] < 0:
            return 0
        elif loc[0] >= 0 and loc[1] < 0:
            return 1
        elif loc[0] < 0 and loc[1] >= 0:
            return 2
        else:
            return 3

    def _too_close(self, attempt, locs):
        """Checks that an attempted location is valid.

        This method is used by generate_locations to ensure the min_distance condition is followed.

        Parameters:
        attempt -- A list of two values (x,y) in visual angle.
        locs -- A list of previous successful attempts to be checked.
        """
        if np.linalg.norm(np.array(attempt)) < self.min_distance:
            return True  # Too close to center

        for loc in locs:
            if np.linalg.norm(np.array(attempt) - np.array(loc)) < self.min_distance:
                return True  # Too close to another square

        return False

    def generate_locations(self, set_size):
        """Creates the locations for a trial. A helper function for self.make_trial.

        Returns a list of acceptable locations (as multiple [x, y] lists).

        Parameters:
        set_size -- The number of stimuli for this trial.
        """
        if self.max_per_quad is not None:
            # quad boundries (x1, x2, y1, y2)
            quad_count = [0, 0, 0, 0]

        locs = []
        counter = 0
        while len(locs) < set_size:
            counter += 1
            if counter > 1000:
                raise ValueError('Timeout -- Cannot generate locations with given values.')

            attempt = [random.uniform(-self.allowed_deg_from_fix, self.allowed_deg_from_fix)
                       for _ in range(2)]

            if self._too_close(attempt, locs):
                continue

            if self.max_per_quad is not None:
                quad = self._which_quad(attempt)

                if quad_count[quad] < self.max_per_quad:
                    quad_count[quad] += 1
                    locs.append(attempt)
            else:
                locs.append(attempt)

        return locs

    def make_trial(self, set_size):
        """Creates a single trial dict. A helper function for self.make_block.

        Returns the trial dict with the following fields:
            - set_size
            - cresp
            - locations
            - rotations
            - stimuli
            - test_location

        Stimuli and rotations are randomly generated.

        Parameters:
        set_size -- The number of stimuli for this trial.
        """
        test_location = random.randint(0, set_size - 1)

        locs = self.generate_locations(set_size)

        ori_idx = [random.randint(0, len(self.possible_orientations) - 1) for _ in range(set_size)]
        oris = [self.possible_orientations[i] for i in ori_idx]

        replacement_orientations = {
            'left': 270,
            'up': 0,
            'right': 90,
            'down': 180
        }

        oris = [replacement_orientations[ori] for ori in oris]
        cresp = self.keys[ori_idx[test_location]]

        stims = [random.choice(['BF1A', 'BF1H', 'BF2A', 'BF2H', 'BM1A', 'BM1H', 'BM2A', 'BM2H', 'WF1A', 'WF1H', 'WF2A', 'WF2H', 'WM1A', 'WM1H', 'WM2A', 'WM2H']) for _ in range(set_size)]
        stims[test_location] = [random.choice(['BF1A', 'BF1H', 'BF2A', 'BF2H', 'BM1A', 'BM1H', 'BM2A', 'BM2H', 'WF1A', 'WF1H', 'WF2A', 'WF2H', 'WM1A', 'WM1H', 'WM2A', 'WM2H'])]

        trial = {
            'set_size': set_size,
            'cresp': cresp,
            'locations': locs,
            'rotations': oris,
            'stimuli': stims,
            'test_location': test_location,
        }

        return trial

    def display_break(self):
        """Displays a break screen in between blocks."""

        break_text = 'Please take a short break. Press space to continue.'
        self.display_text_screen(text=break_text, bg_color=[204, 255, 204], wait_for_input=False)
        time.sleep(2)
        self.display_text_screen(text=break_text, bg_color=[204, 255, 204])

    def post_trial_hook(self, data):
        """post trial hook w/ yes/no question"""

        break_text = 'Was the target face present? Yes or no'
        self.display_text_screen(text=break_text, bg_color=[204, 255, 204], wait_for_input=False)
        time.sleep(2)
        self.display_text_screen(text=break_text, bg_color=[204, 255, 204])

    def display_blank(self, wait_time):
        """Displays a blank screen. A helper function for self.run_trial.

        Parameters:
        wait_time -- The amount of time the blank should be displayed for.
        """

        self.experiment_window.flip()

        psychopy.core.wait(wait_time)

    def display_search(self, coordinates, rotations, stimuli):
        """Displays the search array.

        Parameters:
        coordinates -- A list of lists containing x,y coordinates in visual degrees
        rotations -- a list of rotations (int 0 - 360) to apply to the images
        stimuli -- A list of "T", "L1" and "L2" describing which image file to load
        """
        for pos, ori, stim in zip(coordinates, rotations, stimuli):
            if stim == "BF1A":
                path = self.BF1A_stim_path
            elif stim == "BF1H":
                path = self.BF1H_stim_path
            else:
                path = self.BF2A_stim_path

            psychopy.visual.ImageStim(self.experiment_window, image=path, pos=pos, ori=ori,
                                      size=self.stim_size).draw()

        self.experiment_window.flip()

    def get_response(self, allow_quit=True):
        """Waits for a response from the participant. A helper function for self.run_trial.

        Returns the pressed key and the reaction time.

        Parameters:
        allow_quit -- If True, adds "Q" to the acceptable key list and quits on Q press.
        """

        rt_timer = psychopy.core.MonotonicClock()

        keys = self.keys
        if allow_quit:
            keys += ['q']

        resp = None
        if self.response_time_limit is not None:
            resp = psychopy.event.waitKeys(
                maxWait=self.response_time_limit, keyList=keys, timeStamped=rt_timer)
        else:
            resp = psychopy.event.waitKeys(keyList=keys, timeStamped=rt_timer)

        if resp is None:
            return None, None

        if 'q' in resp[0]:
            self.quit_experiment()

        return resp[0][0], resp[0][1]*1000  # key and rt in milliseconds

    def send_data(self, data):
        """Updates the experiment data with the information from the last trial.

        This function is seperated from run_trial to allow additional information to be added
        afterwards.

        Parameters:
        data -- A dict where keys exist in data_fields and values are to be saved.
        """
        self.update_experiment_data([data])

    def run_trial(self, trial, block_num, trial_num):
        """Runs a single trial.

        Returns the data from the trial after getting a participant response.

        Parameters:
        trial -- The dictionary of information about a trial.
        block_num -- The number of the block in the experiment.
        trial_num -- The number of the trial within a block.
        """
        self.display_blank(self.iti_time)
        self.display_search(trial['locations'], trial['rotations'], trial['stimuli'])

        resp, rt = self.get_response()
        self.experiment_window.flip()

        acc = 1 if resp == trial['cresp'] else 0

        data = {
            'Subject': self.experiment_info['Subject Number'],
            'Block': block_num,
            'Trial': trial_num,
            'Timestamp': psychopy.core.getAbsTime(),
            'SetSize': trial['set_size'],
            'RT': rt,
            'CRESP': trial['cresp'],
            'RESP': resp,
            'ACC': acc,
            'LocationTested': trial['test_location'],
            'Locations': json.dumps(trial['locations']),
            'Rotations': json.dumps(trial['rotations']),
            'Stimuli': str(trial['stimuli']),  # avoids double quotes issues
        }

        return data

    def run(self, setup_hook=None, before_first_trial_hook=None, pre_block_hook=None,
            pre_trial_hook=None, post_trial_hook=post_trial_hook, post_block_hook=None,
            end_experiment_hook=None):
        """Runs the entire experiment.

        This function takes a number of hooks that allow you to alter behavior of the experiment
        without having to completely rewrite the run function. While large changes will still
        require you to create a subclass, small changes like adding a practice block or
        performance feedback screen can be implimented using these hooks. All hooks take in the
        experiment object as the first argument. See below for other parameters sent to hooks.

        Parameters:
        setup_hook -- takes self, executed once the window is open.
        before_first_trial_hook -- takes self, executed after instructions are displayed.
        pre_block_hook -- takes self, block list and block num
            Executed immediately before block start.
            Can optionally return an altered block list.
        pre_trial_hook -- takes self, trial dict, block num, trial num
            Executed immediately before trial start.
            Can optionally return an altered trial dict.
        post_trial_hook -- takes self and the trial data, executed immediately after trial end.
            Can optionally return altered trial data to be stored.
        post_block_hook -- takes self, executed at end of block before break screen (including
            last block).
        end_experiment_hook -- takes self, executed immediately before end experiment screen.
        """

        self.chdir()

        ok = self.get_experiment_info_from_dialog(self.questionaire_dict)

        if not ok:
            print('Experiment has been terminated.')
            sys.exit(1)

        self.save_experiment_info()
        self.open_csv_data_file()
        self.open_window(screen=0)
        self.display_text_screen('Loading...', wait_for_input=False)

        if setup_hook is not None:
            setup_hook(self)

        for instruction in self.instruct_text:
            self.display_text_screen(text=instruction)

        if before_first_trial_hook is not None:
            before_first_trial_hook(self)

        for block_num in range(self.number_of_blocks):
            block = self.make_block()

            if pre_block_hook is not None:
                tmp = pre_block_hook(self, block, block_num)
                if tmp is not None:
                    block = tmp

            for trial_num, trial in enumerate(block):

                if pre_trial_hook is not None:
                    tmp = pre_trial_hook(self, trial, block_num, trial_num)
                    if tmp is not None:
                        trial = tmp

                data = self.run_trial(trial, block_num, trial_num)

                if post_trial_hook is not None:
                    tmp = post_trial_hook(self, data)
                    if tmp is not None:
                        data = tmp

                self.send_data(data)

            self.save_data_to_csv()

            if post_block_hook is not None:
                post_block_hook(self)

            if block_num + 1 != self.number_of_blocks:
                self.display_break()

        if end_experiment_hook is not None:
            end_experiment_hook(self)

        self.display_text_screen(
            'The experiment is now over, please get your experimenter.',
            bg_color=[0, 0, 255], text_color=[255, 255, 255])

        self.quit_experiment()


if __name__ == "__main__":
    exp = TLTask(
        # BaseExperiment parameters
        experiment_name=exp_name,
        data_fields=data_fields,
        monitor_distance=distance_to_monitor,
        # Custom parameters go here
    )

    exp.run()
