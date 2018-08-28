import random
import constants as const

class GameMap(object):
    def __init__(self, wall_tex, food_tex, big_food_tex, maptype):
        self.grid = []
        self.position_to_idx_dict = {}
        self.maptype = maptype

        self.create_map()

        self.wall_texture     = wall_tex
        self.food_texture     = food_tex
        self.big_food_texture = big_food_tex

        self.spawn_food = True
        self.big_food_spawned = False
        self.big_food_timer = 0
        self.big_food_idx   = (-1, -1)

    def create_map(self):
        pos = (0,0)
        max_i = int(const.HEIGHT / const.STEPSIZE)
        max_j = int(const.WIDTH / const.STEPSIZE)
        for i in range(max_i):
            row = []
            for j in range(max_j):
                if (i == 0 or i == max_i-1 or j == 0 or j == max_j-1):
                    if self.maptype == 1:
                        row.append("w")
                    elif self.maptype == 2 \
                    and (i < int(max_i/3) or i > int(max_i/3)*2) \
                    and (j < int(max_j/3) or j > int(max_j/3)*2):
                        row.append("w")
                    else:
                        row.append("")
                else:
                    row.append("")
                self.position_to_idx_dict[pos] = (i, j)
                pos = (pos[0] + const.STEPSIZE, pos[1])
            self.grid.append(row)
            pos = (0, pos[1] + const.STEPSIZE)

    def draw(self, screen):
        for position, idx in self.position_to_idx_dict.items():
            row, col = idx
            tile = self.grid[row][col]
            if tile == "w":
                screen.blit(self.wall_texture, position)
            elif tile == "f":
                screen.blit(self.food_texture, position)
            elif tile == "bf_draw":
                screen.blit(self.big_food_texture, position)

    def update(self, snake, spawn_big_food):
        illegal_positions = []
        for pos in snake.positions:
            illegal_positions.append(self.position_to_idx_dict[pos])
        loop_counter = 0
        while self.spawn_food:
            i = random.randint(1, const.HEIGHT / const.STEPSIZE -1)
            j = random.randint(1, const.WIDTH / const.STEPSIZE -1)
            if self.grid[i][j] == "" and (i, j) not in illegal_positions:
                self.grid[i][j] = "f"
                self.spawn_food = False
            if loop_counter > 5:
                break
            loop_counter += 1
        loop_counter = 0
        while spawn_big_food:
            self.big_food_spawned = True
            self.big_food_timer = const.BIG_FOOD_TIME
            i = random.randint(1, const.HEIGHT / const.STEPSIZE -2)
            j = random.randint(1, const.WIDTH / const.STEPSIZE -2)
            if  self.grid[i][j]     == "" and (i, j)     not in illegal_positions \
            and self.grid[i+1][j]   == "" and (i+1, j)   not in illegal_positions \
            and self.grid[i][j+1]   == "" and (i, j+1)   not in illegal_positions \
            and self.grid[i+1][j+1] == "" and (i+1, j+1) not in illegal_positions:
                self.grid[i][j]     = "bf_draw"
                self.grid[i+1][j]   = "bf"
                self.grid[i][j+1]   = "bf"
                self.grid[i+1][j+1] = "bf"
                spawn_big_food = False
                self.big_food_idx = (i, j)
            if loop_counter > 5:
                break
            loop_counter += 1

    def big_food_eaten(self, row, col):
        self.big_food_timer = 0
        self.big_food_spawned = False
        if row == -1:
            i, j = self.big_food_idx
            self.grid[i][j]     = ""
            self.grid[i+1][j]   = ""
            self.grid[i][j+1]   = ""
            self.grid[i+1][j+1] = ""
        else:
            for i in range(row-1, row+2):
                if i >= len(self.grid):
                    break
                for j in range(col-1, col+2):
                    if j >= len(self.grid[0]):
                        break
                    if self.grid[i][j].startswith("bf"):
                        self.grid[i][j] = ""

    def export_map(self, dest_path):
        with open(dest_path, "w") as f:
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    if len(self.grid[i][j]) > 0:
                        f.write(self.grid[i][j])
                    else:
                        f.write(" ")
                f.write("\n")

    def import_map(self, map_path):
        try:
            with open(map_path, "r") as f:
                i = j = 0
                for line in f:
                    j = 0
                    for c in line[:-1]:
                        if c != " ":
                            self.grid[i][j] = c
                        else:
                            self.grid[i][j] = ""
                        j += 1
                    i += 1
        except:
            pass