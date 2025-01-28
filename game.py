



ship_types = {
    "destroyer": 1,
    "submarine": 2,
    "cruiser": 3,
    "battleship": 4,
}

class Ship:
    def __init__(self, type, x, y, rot):
        self.type = type
        self.x = x
        self.y = y
        self.rot = rot
        self.hp = ship_types[type]
        self.max_hp = ship_types[type]
        self.sunk = False
        self.hit_loc = [False] * ship_types[type]   
    
    def hit(self, x, y):
        loc = self.translate_to_loc(x, y)
        if loc is not False:
            if self.hit_loc[loc] == True:
                return False
            self.hit_loc[loc] = True
            self.hp = self.max_hp - sum(self.hit_loc)
            if self.hp == 0:
                self.sunk = True
            return True
        else:
            return False
    
    def translate_to_loc(self, x, y):
        if x < 0 or x > 9 or y < 0 or y > 9:
            return False
        else:
            if self.rot == 0 and y == self.y:
                if x >= self.x and x < self.x + self.max_hp :
                    return x - self.x
                else:
                    return False
            elif self.rot == 1 and x == self.x:
                if y >= self.y and y < self.y + self.max_hp :
                    return y - self.y 
                else:
                    return False
            elif self.rot == 2 and y == self.y:
                if x <= self.x and x > self.x - self.max_hp  :
                    return self.x - x 
                else:
                    return False
            elif self.rot == 3 and x == self.x:
                if y <= self.y and y > self.y - self.max_hp :
                    return self.y - y
                else:
                    return False
        

class Map:
    
    def __init__(self, size):
        self.grid = [[None for i in range(size)] for j in range(size)]
        self.ships = []
        
    
    def place_ship(self, ship, x ,y,rot, mock = False):
        def get_locations(ship):
            if ship.rot == 0:
                return [(ship.x + i, ship.y) for i in range(ship.max_hp)]
            elif ship.rot == 1:
                return [(ship.x, ship.y + i) for i in range(ship.max_hp)]
            elif ship.rot == 2:
                return [(ship.x - i, ship.y) for i in range(ship.max_hp)]
            elif ship.rot == 3:
                return [(ship.x, ship.y - i) for i in range(ship.max_hp)]
        def check_surroundings(map,x, y):
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if x + i < 0 or x + i > 9 or y + j < 0 or y + j > 9:
                        continue
                    if j == 0 and i == 0:
                        continue
                    if map[y + j][x + i] is not None:
                        return False
            return True
        ship = Ship(ship, x, y, rot)
        for x, y in get_locations(ship):
            if x < 0 or x > 9 or y < 0 or y > 9:
                return False
            if self.grid[y][x] is not None:
                return False
            if not check_surroundings(self.grid, x, y):
                return False
            
        if not mock:
            for x, y in get_locations(ship):
                self.grid[y][x] = ship
            
            self.ships.append(ship)
        return True
    
    

    
    def hit(self, x, y):
        if self.grid[y][x] is not None:
            return self.grid[y][x].hit(x, y)
        else:
            return False    
        
    
    def check_win(self):
        for ship in self.ships:
            if ship.sunk == False:
                return False
        return True
    
    
    def print_map(self):
        for i in range(10):
            for j in range(10):
                if self.grid[i][j] is not None:
                    if self.grid[i][j].hit_loc[self.grid[i][j].translate_to_loc(j, i)]:
                        print("X", end = " ")
                    else:
                        print("O", end = " ")
                else:
                    print("-", end = " ")
            print()
            
    def get_ship_grid(self):
        grid = [[0 for i in range(10)] for j in range(10)]
        for ship in self.ships:
            if ship.rot == 0:
                for i,loc in enumerate(ship.hit_loc):
                    if loc:
                        grid[ship.y][ship.x + i] = -1
                    else:
                        grid[ship.y][ship.x + i] = 1
            elif ship.rot == 1:
                for i,loc in enumerate(ship.hit_loc):
                    if loc:
                        grid[ship.y + i][ship.x] = -1
                    else:
                        grid[ship.y + i][ship.x] = 1
            elif ship.rot == 2:
                for i,loc in enumerate(ship.hit_loc):
                    if loc:
                        grid[ship.y][ship.x - i] = -1
                    else:
                        grid[ship.y][ship.x - i] = 1
            elif ship.rot == 3:
                for i,loc in enumerate(ship.hit_loc):
                    if loc:
                        grid[ship.y - i][ship.x] = -1
                    else:
                        grid[ship.y - i][ship.x] = 1
            
        return grid
        
        
class HitGrid:
    
    def __init__(self, size):
        self.grid = [[0 for i in range(size)] for j in range(size)]
        
    def hit(self, x, y, effect):
        if effect:
            self.grid[y][x] = 1
        else:
            self.grid[y][x] = -1
        
    def print_grid(self):
        for i in range(10):
            for j in range(10):
                print(self.grid[i][j], end = " ")
            print()
    
    
class Player:
    
    def __init__(self):
        self.turn = False
        self.ships = []
        self.hit_grid = HitGrid(10)
        
        
    def place_ship(self, type, map):
        x = int(input("Enter x coordinate: "))
        y = int(input("Enter y coordinate: "))
        rot = int(input("Enter rotation: "))
        return map.place_ship(type, x, y, rot)
    
    def shoot(self, map):
        x = int(input("Enter x coordinate: "))
        y = int(input("Enter y coordinate: "))
        efect = map.hit(x, y)
        if efect:
            print("Hit!")
            self.hit_grid.hit(x, y)
        else:
            print("Miss!")
        map.print_map()
        return efect, x, y
        
    
class Game:
    
    def __init__(self):
        self.map1 = Map(10)
        self.map2 = Map(10)
        self.turn_number = 0
        self.winner = None
        self.loser = None
        self.game_over = False
        self.ship_types = {
            "destroyer": 1,
            "submarine": 2,
            "cruiser": 3,
            "battleship": 4,
        }
        self.ship_numbers = {
            "destroyer": 4,
            "submarine": 3,
            "cruiser": 2,
            "battleship": 1,
        }
        self.player1 = None
        self.player2 = None
        self.walkover = False
    
    def start_game(self):
        for ship in self.ship_numbers:
            for i in range(self.ship_numbers[ship]):
                cutoff1 = 0
                effect = False
                while not effect:
                    effect = self.player1.place_ship(ship, self.map1)
                    cutoff1 += 1
                    if cutoff1 > 100:
                        self.game_over = True
                        self.walkover = True
                        break
                cutoff2 = 0
                effect = False
                while not effect:
                    effect = self.player2.place_ship(ship, self.map2)
                    cutoff2 += 1
                    if cutoff2 > 100:
                        self.game_over = True
                        self.walkover = True
                        break
            if self.game_over:
                if cutoff1 > 100 and cutoff2 > 100:
                    self.loser = [self.player1, self.player2]
                elif cutoff1 > 100:
                    self.loser = self.player1
                    self.winner = self.player2
                else:
                    self.loser = self.player2
                    self.winner = self.player1


        
    def check_win(self):
        if self.map1.check_win():
            self.winner = self.player2
            self.loser = self.player1
            self.game_over = True
        elif self.map2.check_win():
            self.winner = self.player1
            self.loser = self.player2
            self.game_over = True
        if  all(x != 0 for row in self.player1.hit_grid.grid for x in row) and any(ship.hp > 0 for ship in self.map2.ships):
            self.game_over = True
            self.player1.score += -100
        if all(x != 0 for row in self.player2.hit_grid.grid for x in row) and any(ship.hp > 0 for ship in self.map1.ships):
            self.game_over = True
            self.player2.score += -100
        
        
        
        
    def turn(self):
        effect, x, y = self.player1.shoot( self.player1.hit_grid,self.map2)
        if effect == True:
            self.player1.hit_grid.grid[y][x] = 1
        else:
            self.player1.hit_grid.grid[y][x] = -1
        
        effect, x, y = self.player2.shoot(self.player2.hit_grid, self.map1)
        if effect == True:
            self.player2.hit_grid.grid[y][x] = 1
        else:
            self.player2.hit_grid.grid[y][x] = -1
        
        self.check_win()
        self.turn_number += 1
        
    def print_maps(self):
        print("Player 1's map:")
        self.map1.print_map()
        print("Player 2's map:")
        self.map2.print_map()
        
        
    def play(self, debug = False):
        self.start_game()
        while not self.game_over:
            self.turn()
            if debug:
                self.print_maps()
                input()
            if self.turn_number > 1000:
                self.game_over = True
        
        