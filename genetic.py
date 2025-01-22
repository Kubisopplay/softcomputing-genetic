from game import Game, Map, Player, HitGrid
import torch
from ai_player import AIPlayer, FightBrain, PlaceBrainPos
import tqdm
import random

def score(game : Game):
    if game.winner is not None:
        if game.walkover == False:
            #print("We have a winner!")
            game.winner.score = 100 - game.turn_number
        return game.winner
    else:
        if len(game.map1.ships) <10 or len(game.map2.ships) < 10:
            p1_score = len(game.map1.ships) - 10    
            p2_score = len(game.map2.ships) - 10
            game.player1.score = p1_score
            game.player2.score = p2_score
        else:
            p1_score = 20 - sum([ship.hp for ship in game.map2.ships])
            p2_score = 20 -sum([ship.hp for ship in game.map1.ships])
            game.player1.score = p1_score
            game.player2.score = p2_score   
        if p1_score > p2_score:
            return game.player1
        elif p2_score > p1_score:
            return game.player2
        else:
            return None
        
        
def fresh_ai():
    fb = FightBrain()
    pb_pos = PlaceBrainPos()
    for param in fb.parameters():
        param.data = torch.randn_like(param)
    for param in pb_pos.parameters():
        param.data = torch.randn_like(param)

    return AIPlayer(fb, pb_pos)


def mutate_ai(ai : AIPlayer, mutation_ratio = 0.05):
    fb = ai.fight_brain
    pb = ai.place_brain
    for param in fb.parameters():
        if random.random() < mutation_ratio:
            param.data += torch.randn_like(param)
    for param in pb.parameters():
        if random.random() < mutation_ratio:
            param.data += torch.randn_like(param)
    ai.hit_grid = HitGrid(10)
    return ai

def crossover_ai(ai1 : AIPlayer, ai2 : AIPlayer):
    fb1 = ai1.fight_brain
    pb1 = ai1.place_brain
    fb2 = ai2.fight_brain
    pb2 = ai2.place_brain
    fbc = FightBrain()
    pbc = PlaceBrainPos()
    
    for param in fbc.parameters():
        if random.random() < 0.5:
            param.data = fb1.state_dict()[param]
        else:
            param.data = fb2.state_dict()[param]
    for param in pbc.parameters():
        if random.random() < 0.5:
            param.data = pb1.state_dict()[param]
        else:
            param.data = pb2.state_dict()[param]
    
    
    
    
    return AIPlayer(fbc, pbc)


import multiprocessing as mp
def epoch(population : list, mutation_rate = 0.05):
    
    victims = population.copy()

    winners = []
    
    processes = []
    while len(victims) > 1:
        
        p1 = random.choice(victims)
        victims.remove(p1)
        p2 = random.choice(victims)
        victims.remove(p2) 
        
        game = Game()
        game.player1 = p1
        game.player2 = p2
        game.play()
        
        winner = score(game)
        if winner is not None:
            winners.append(winner)

        
    new_population = []
    
    winners = sorted(winners, key = lambda x: x.score, reverse = True)
    
    for ai in winners[:10]:
        ai.grid = HitGrid(10)
        new_population.append(ai)
    
    for ai in winners[:30]:
        for i in range(5):
            new_population.append(mutate_ai(ai, mutation_rate))
        
    for i in range(20):
        new_population.append(fresh_ai())
    while len(new_population) < 200:
        winner = random.choice(winners)
        winner2 = random.choice(winners)
        while winner == winner2 and len(winners) > 1:
            winner2 = random.choice(winners)
       # new_population.append(crossover_ai(winner, winner2))
        new_population.append(mutate_ai(winner))
        
    
        
    
    return new_population


def genetic_algorithm():
    population = [fresh_ai() for i in range(100)]
    best = {}
    for i in range(100):
        population = epoch(population)
        
        best[i] = max(population, key = lambda x: x.score).clone()
        best[i].save_brains(i)
        print(best[i], best[i].score)
    
    return population, best

