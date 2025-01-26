from game import Map, Player, Ship, ship_types
import torch
import copy

#zrobić CNNkę zamiast tego

def map_to_tensor(grid):
    tensor = torch.zeros(10, 10)
    for i in range(10):
        for j in range(10):
            tensor[i][j] = grid[i][j]
    tensor = tensor.flatten()
    return tensor

class FightBrain(torch.nn.Module):
    
    def __init__(self):
        super().__init__()
        self.conv =torch.nn.Conv2d(1, 1, 5, padding = 2)
        self.model = torch.nn.Sequential(
            torch.nn.ReLU(),
            torch.nn.Softmax(1)
        )
        
    
    def forward(self, x):
        return self.model(self.conv.forward(x))
            
            
            
            
class PlaceBrainPos(torch.nn.Module):
    
    def __init__(self):
        super().__init__()
        self.conv = torch.nn.Conv2d(1,1,5, padding = 2)
        self.model = torch.nn.Sequential(
            torch.nn.ReLU(),
            torch.nn.Softmax(1)
        )
        
    def forward(self, x):
        return self.model(self.conv.forward(x))
    
    


name_2_class = {
    "destroyer": torch.tensor([1, 0, 0, 0]),
    "submarine": torch.tensor([0, 1, 0, 0]),
    "cruiser": torch.tensor([0, 0, 1, 0]),
    "battleship": torch.tensor([0, 0, 0, 1]),
} # I know there might be a btter way to do this, but deadlines are deadlines
class AIPlayer(Player):
    
    def __init__(self, fb, pb):
        super().__init__()
        self.fight_brain = fb
        self.place_brain =  pb

        self.score = -50

    def find_working_rotation(self, ship, x, y, map):
        for rot in range(4):
            if map.place_ship(ship, x, y, rot, True):
                return rot
        return None
    def place_ship(self, ship, map):
        grid = map.get_ship_grid()
        tensor = map_to_tensor(grid)
        tensor = tensor.unflatten(0,(1,10,10))
        pos = self.place_brain(tensor)
        pos = pos.flatten()
        
        is_set = False
        sorted_pos = pos.argsort(descending = True)
        for i in range(100):
            x, y = sorted_pos[i] // 10, sorted_pos[i] % 10
            x = x.item()
            y = y.item()
            rot = self.find_working_rotation(ship, x, y, map)
            if rot is not None:
                break
        if rot is None:
            for x in range(10):
                for y in range(10):
                    for rot in range(4):
                        if map.place_ship(ship, x, y, rot, True):
                            return map.place_ship(ship, x, y, rot)

        return map.place_ship(ship, x, y, rot)
        
    def shoot(self, hit_grid, map):
        tensor_hit = map_to_tensor(hit_grid.grid)
        tensor_hit = tensor_hit.unflatten(0,(1,10,10))
        pos = self.fight_brain(tensor_hit)
        pos = pos.flatten()
        sorted_pos = pos.argsort(descending = True)
        success = False
        for i in range(100):
            x, y = sorted_pos[i] // 10, sorted_pos[i] % 10
            x = x.item()
            y = y.item()
            if hit_grid.grid[y][x] == 0:
                success = True
                break
        if not success:
            for x in range(10):
                for y in range(10):
                    if hit_grid.grid[y][x] == 0:
                        return map.hit(x, y), x, y
        return map.hit(x, y), x, y
        

    def save_brains(self, path):
        torch.save(self.fight_brain.state_dict(), f"epochs/fight_brain_{path}.pth")
        torch.save(self.place_brain.state_dict(), f"epochs/place_brain_{path}.pth")

        
    def clone(self):
        return copy.deepcopy(self)


import random
class RandomPlayer(Player):
    
    def __init__(self):
        super().__init__()
        
    def place_ship(self, ship, map):
        success = False
        while not success:
            
            x = random.randint(0, 9)
            y = random.randint(0, 9)
            rot = random.randint(0, 3)
            success = map.place_ship(ship, x, y, rot)
            
        return success
        
    def shoot(self, map : Map):
        failsafe = 0
        while True:
            x = random.randint(0, 9)
            y = random.randint(0, 9)
            failsafe += 1
            if self.hit_grid.grid[x][y] == 0:
                return map.hit(x,y), x, y
            if failsafe > 1000:
                raise Exception("RandomPlayer stuck in loop")
            
        
