import pytest
import numpy as np
from tsg.meta_generators import RegimeSwitchGenerator, MarkovSwitchGenerator
from tsg.generators import BaseGenerator


class DummyGenerator(BaseGenerator):
    """
    Dummy generator that assigns a unique value on creation.
    Returns that constant value on each call.
    """
    counter = 0

    def __init__(self, start_value=0):
        # Each DummyGenerator instance has a unique value based on creation order
        self.value = start_value + DummyGenerator.counter
        DummyGenerator.counter += 1

    def generate_value(self, last_value=None):
        # Always return the assigned constant value
        return self.value

    def reset(self):
        # No state to reset for DummyGenerator
        pass

    @classmethod
    def reset_counter(cls):
        # Reset class-level counter between tests
        cls.counter = 0



# === REGIME SWITCH GENERATOR TESTS ===

def test_regime_switch_generator_switching_behavior():
    """
    Test that RegimeSwitchGenerator switches between generator instances 
    at correct switch times, creating new instances each time.
    """
    DummyGenerator.reset_counter()

    switch_times = [3, 6]
    regime_gen = RegimeSwitchGenerator(
        [DummyGenerator, DummyGenerator],  # Using DummyGenerator twice
        [{} for _ in range(2)],            # No constructor params
        switch_times=switch_times
    )

    values = [regime_gen.generate_value() for _ in range(8)]

    # Expectation:
    #   0-2 => First DummyGenerator instance (returns 0)
    #   3-5 => Second DummyGenerator instance (returns 1)
    #   6-7 => Third DummyGenerator instance (returns 2)
    expected = [0, 0, 0, 1, 1, 1, 2, 2]
    assert values == expected


def test_regime_switch_generator_reset():
    """
    Test that RegimeSwitchGenerator resets correctly and restarts with a new generator.
    """
    DummyGenerator.reset_counter()

    regime_gen = RegimeSwitchGenerator(
        [DummyGenerator, DummyGenerator],
        [{} for _ in range(2)],
        switch_times=[2]
    )

    # Generate values to trigger switching
    for _ in range(4):
        regime_gen.generate_value()

    # Reset generator - this should reset its internal state and create a new generator
    regime_gen.reset()

    after_reset_value = regime_gen.generate_value()

    # The value after reset should match the last created DummyGenerator instance (counter - 1)
    assert after_reset_value == DummyGenerator.counter - 1



# === MARKOV SWITCH GENERATOR TESTS ===

def test_markov_switch_generator_switches_and_creates_new_instances():
    """
    Test that MarkovSwitchGenerator switches correctly according to the transition matrix,
    and that new generator instances are created upon switching.
    """
    DummyGenerator.reset_counter()

    # Transition matrix with deterministic switching (always switches state)
    transition_matrix = [[0.0, 1.0], [1.0, 0.0]]

    markov_gen = MarkovSwitchGenerator(
        [DummyGenerator, DummyGenerator],
        [{} for _ in range(2)],
        transition_matrix=transition_matrix
    )

    # Call generate_value multiple times to force switches
    values = [markov_gen.generate_value() for _ in range(6)]

    # Should have created 7 instances: initial + one for each of 6 switches
    assert DummyGenerator.counter == 7
    assert all(isinstance(v, int) for v in values)


def test_markov_switch_generator_reset():
    """
    Test that MarkovSwitchGenerator resets correctly,
    resetting state and starting with a new instance.
    """
    DummyGenerator.reset_counter()

    # Transition matrix with equal switching probabilities
    transition_matrix = [[0.5, 0.5], [0.5, 0.5]]

    markov_gen = MarkovSwitchGenerator(
        [DummyGenerator, DummyGenerator],
        [{} for _ in range(2)],
        transition_matrix=transition_matrix
    )

    # Force into a different state manually
    markov_gen.current_state = 1

    # Reset should bring back to state 0 with a new generator
    markov_gen.reset()

    assert markov_gen.current_state == 0
    # Two instances total: one at init, one after reset
    assert DummyGenerator.counter == 2
    # The current generator returns the value of the second instance (which is 1)
    assert markov_gen.current_generator.generate_value() == 1
