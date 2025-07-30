import numpy as np
from .generators import BaseGenerator
from copy import deepcopy



class RegimeSwitchGenerator(BaseGenerator):
    def __init__(self, generator_classes, generator_params_list, switch_times):
        """
        Switches between generator instances at fixed switch times.

        Parameters:
        - generator_classes: list of generator classes (not instances)
        - generator_params_list: list of dicts with params for each generator
        - switch_times: list of time steps when regime should switch (sorted ascending)
        """
        assert len(generator_classes) == len(generator_params_list), "Classes and params length mismatch."
        self.generator_classes = generator_classes
        self.generator_params_list = generator_params_list
        self.switch_times = set(switch_times)

        self.current_step = 0
        self.current_gen_idx = 0
        self.current_generator = self._instantiate_generator(self.current_gen_idx, last_value=None)

    def _instantiate_generator(self, idx, last_value):
        params = deepcopy(self.generator_params_list[idx])
        if last_value is not None:
            params['start_value'] = last_value
        return self.generator_classes[idx](**params)

    def generate_value(self, last_value=None):
        if self.current_step in self.switch_times:
            self.current_gen_idx = (self.current_gen_idx + 1) % len(self.generator_classes)
            self.current_generator = self._instantiate_generator(self.current_gen_idx, last_value=last_value)

        self.current_step += 1
        return self.current_generator.generate_value(last_value)

    def reset(self):
        self.current_step = 0
        self.current_gen_idx = 0
        self.current_generator = self._instantiate_generator(self.current_gen_idx, last_value=None)



class MarkovSwitchGenerator(BaseGenerator):
    def __init__(self, generator_classes, generator_params_list, transition_matrix, initial_state=0):
        """
        A meta-generator that switches between generator instances according to a Markov chain.

        Parameters:
        - generator_classes: list of generator classes (not instances!)
        - generator_params_list: list of dicts with params for each generator
        - transition_matrix: Markov transition matrix, shape (n, n)
        - initial_state: index of starting generator
        """
        assert len(generator_classes) == len(generator_params_list), "Classes and params length mismatch."
        self.generator_classes = generator_classes
        self.generator_params_list = generator_params_list
        self.transition_matrix = transition_matrix
        self.initial_state = initial_state

        self.current_state = initial_state
        self.current_generator = self._instantiate_generator(self.current_state, last_value=None)

    def _instantiate_generator(self, state_idx, last_value):
        params = deepcopy(self.generator_params_list[state_idx])
        if last_value is not None:
            params['start_value'] = last_value
        return self.generator_classes[state_idx](**params)

    def generate_value(self, last_value=None):
        if last_value is None:
            # First call uses current generator state
            value = self.current_generator.generate_value()
        else:
            value = self.current_generator.generate_value(last_value)

        # Sample next state and re-instantiate generator if switched
        next_state = np.random.choice(len(self.generator_classes), p=self.transition_matrix[self.current_state])
        if next_state != self.current_state:
            self.current_state = next_state
            self.current_generator = self._instantiate_generator(self.current_state, last_value=value)

        return value

    def reset(self):
        self.current_state = self.initial_state
        self.current_generator = self._instantiate_generator(self.current_state, last_value=None)

