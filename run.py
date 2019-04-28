#!/usr/bin/python


"""

This tests that all the PLE games launch, except for doom; we
explicitly check that it isn't defined.


"""


import nose
import numpy as np
import unittest
import os

NUM_STEPS=150

class NaiveAgent():
    def __init__(self, actions):
        self.actions = actions
    def pickAction(self, reward, obs):
        return self.actions[np.random.randint(0, len(self.actions))]


class MyTestCase(unittest.TestCase):

    def run_a_game(self,game):
        from ple import PLE
        p =  PLE(game,display_screen=True)
        agent = NaiveAgent(p.getActionSet())
        p.init()
        reward = p.act(p.NOOP)
        for i in range(NUM_STEPS):
            obs = p.getScreenRGB()
            reward = p.act(agent.pickAction(reward,obs))
        input()

    def test_new(self):
        from ple.games.newgame import newgame
        game = newgame()
        self.run_a_game(game)

if __name__ == "__main__":
    nose.runmodule()
    os.system("pause")
