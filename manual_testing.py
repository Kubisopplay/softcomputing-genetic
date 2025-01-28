from game import *
from ai_player import *
from genetic import *

testmap = Map(10)

testmap.place_ship("battleship", 0, 0, 0)

testmap.place_ship("battleship", 0, 2, 1)

testmap.place_ship("battleship", 8, 2, 2)

testmap.place_ship("battleship", 8,8,3)

testmap.print_map()