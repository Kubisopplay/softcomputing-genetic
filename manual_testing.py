from game import *
from ai_player import *
from genetic import *


fb = FightBrain().load_state_dict(torch.load("fight_brain.pth"))
pb = PlaceBrainPos()

ai = AIPlayer(fb, pb)

human = Player()

game = Game()

game.player1 = ai

game.player2 = human

game.start_game()

