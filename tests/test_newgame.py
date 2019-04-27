#!/usr/bin/python
import nose
import numpy as np
import unittest

class NaiveAgent():
    def __init__(self, actions):
        self.actions = actions
    def pickAction(self, reward, obs):
        return self.actions[np.random.randint(0, len(self.actions))]

class MyTestCase(unittest.TestCase):

    def run_a_game(self,game):
        from ple import PLE
        p =  PLE(game)
        agent = NaiveAgent(p.getActionSet())
        p.init()
        reward = p.act(p.NOOP)
        for i in range(50):
            obs = p.getScreenRGB()
            reward = p.act(agent.pickAction(reward,obs)) 

    def test_newgame(self):
        from ple.games.newgame import newgame
        game = newgame()
        self.run_a_game(game)    

    def test_noaffordance(self):
        from ple.games.noaffordance import noaffordance
        game = noaffordance()
        self.run_a_game(game)   

    def test_nosemantics(self):
        from ple.games.nosemantics import nosemantics
        game = nosemantics()
        self.run_a_game(game)    

    def test_nosimilarity(self):
        from ple.games.nosimilarity import nosimilarity
        game = nosimilarity()
        self.run_a_game(game)  

    def test_originalGame(self):
        from ple.games.originalgame import originalGame
        game = originalGame()
        self.run_a_game(game)  

if __name__ == "__main__":
    nose.runmodule()
    #unittest.main()
