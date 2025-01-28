from game import Game, Map, Player, HitGrid
import torch
from ai_player import AIPlayer, FightBrain, PlaceBrainPos
import tqdm
import random

def score(game : Game):
    p1_score = game.player1.score
    p2_score = game.player2.score
    
    if any([x != 0 for row in game.player1.hit_grid.grid for x in row]):
        for row in game.player1.hit_grid.grid:
            for cell in row:
                if cell == -1:
                    p1_score -= 0.5
                elif cell == 1:
                    p1_score += 1
    else:
        p1_score = None
    
    if any([x != 0 for row in game.player2.hit_grid.grid for x in row]):
                
        for row in game.player2.hit_grid.grid:
            for cell in row:
                if cell == -1:
                    p2_score -= 0.5
                elif cell == 1:
                    p2_score += 1
                    
    else:
        p2_score = None
        
    game.player1.score = p1_score
    game.player2.score = p2_score
    game.player1.hit_grid = HitGrid(10)
    game.player2.hit_grid = HitGrid(10)
        
    
    

        
        
def fresh_ai():
    fb = FightBrain()
    pb_pos = PlaceBrainPos()
    for param in fb.parameters():
        param.data = torch.randn_like(param)* 0.1
    for param in pb_pos.parameters():
        param.data = torch.randn_like(param)* 0.1

    return AIPlayer(fb, pb_pos)


def mutate_ai(ai : AIPlayer, mutation_ratio = 0.05):
    fb = ai.fight_brain
    pb = ai.place_brain
    for param in fb.parameters():
        if random.random() < mutation_ratio:
            param.data += torch.randn_like(param)   * 0.1
    for param in pb.parameters():
        if random.random() < mutation_ratio:
            param.data += torch.randn_like(param)* 0.1
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



def epoch(population : list, mutation_rate = 0.50):
    
    victims = population.copy()
    for ai in victims:
        ai.score = -50
    
    
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
        
        score(game)
        
        winners.append(game.player1)
        winners.append(game.player2)
        
    for ai in winners:
        if ai.score is None:
            winners.remove(ai)
        ai.hit_grid = HitGrid(10)   
    second_wave = []
    
    while len(winners) > 1:
        
        p1 = random.choice(winners)
        winners.remove(p1)
        p2 = random.choice(winners)
        winners.remove(p2) 
        
        game = Game()
        game.player1 = p1
        game.player2 = p2
        game.play()
        
        score(game)
        
        second_wave.append(game.player1)
        second_wave.append(game.player2)
        
    winners = second_wave

    for ai in winners:
        if ai.score is None:
            winners.remove(ai)
    best = max(winners, key = lambda x: x.score)
    
    logs={
            "avg_score": sum([x.score for x in population])/len(population),
            "best_score": best.score
        }
    
    print(logs)
        
    new_population = []
    
    winners = sorted(winners, key = lambda x: x.score, reverse = True)
    
    for ai in winners[:15]:
        ai.grid = HitGrid(10)
        new_population.append(ai)
    
    for ai in winners[:25]:
        for i in range(1):
            new_population.append(mutate_ai(ai, mutation_rate))
        
        
    while len(new_population) < 50:
        new_population.append(fresh_ai())
        
    
        
    
    return new_population, logs


def genetic_algorithm():
    population = [fresh_ai() for i in range(100)]
    logs = []
    best = {}
    for i in range(100):
        population, log = epoch(population)

        best = max(population, key = lambda x: x.score).clone()
        if i % 25 == 0:
            
            best.save_brains(i)
        logs.append(log)
        

    import json
    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=4)
    
    
    return population, best

