#!/usr/env/bin python3

# TODO:
# - Snake tail
# - Map type select
# - Solve curve bug (curves wrong way when turning into passable wall)

import random
import pygame

STEPSIZE = 50
WIDTH = 1450
HEIGHT = 900
UPDATE_FREQ = 100
BIG_FOOD_FREQ = 30000
BIG_FOOD_TIME = 2500
START_SIZE = 10
LIFESAVER_TIME_FACTOR = 0.75

# Map types:
# 0: No walls
# 1: Surrounded by walls
# 2: Walls with gaps
MAP_TYPE = 0

class Snake(object):
    def __init__(self, startpos, snakebits):
        self.positions = [startpos]
        self.size = START_SIZE
        self.alive = True
        self.dead_next_move = 0
        self.direction = (1, 0)

        # Textures
        self.hor_tex    = snakebits[0]
        self.ver_tex    = snakebits[1]
        self.curves = {
            "upleft"    : snakebits[2],
            "upright"   : snakebits[3],
            "downright" : snakebits[4],
            "downleft"  : snakebits[5]
        }
        self.head_up    = snakebits[6]
        self.head_down  = snakebits[7]
        self.head_left  = snakebits[8]
        self.head_right = snakebits[9]
        self.tail_up    = snakebits[10]
        self.tail_down  = snakebits[11]
        self.tail_left  = snakebits[12]
        self.tail_right = snakebits[13]

    def update(self, gamemap, direction_input):
        if direction_input != (-1, -1):
            self.direction = direction_input

        head = self.positions[-1]
        new_head = (head[0] + self.direction[0] * STEPSIZE, head[1] + self.direction[1] * STEPSIZE)
        try:
            row, col = gamemap.position_to_idx_dict[new_head]
        except KeyError:
            if self.direction[0] == 1:
                new_head = (0, new_head[1])
            elif self.direction[0] == -1:
                new_head = (WIDTH - STEPSIZE, new_head[1])
            elif self.direction[1] == 1:
                new_head = (new_head[0], 0)
            elif self.direction[1] == -1:
                new_head = (new_head[0], HEIGHT - STEPSIZE)

            row, col = gamemap.position_to_idx_dict[new_head]

        self.positions.append(new_head)
        
        tile = gamemap.grid[row][col]
        if tile == "w" or new_head in self.positions[1:-1]:
            self.alive = False
        elif tile == "f":
            self.size += 1
            gamemap.grid[row][col] = ""
            gamemap.spawn_food = True
        elif tile.startswith("bf"):
            self.size += 5
            gamemap.big_food_eaten(row, col)

        if len(self.positions) > self.size:
            self.positions = self.positions[1:]

        self.dead_next_move = 0
        # Check if next move would kill without direction change
        try:
            next_pos = (new_head[0] + self.direction[0] * STEPSIZE, new_head[1] + self.direction[1] * STEPSIZE)
            i, j = gamemap.position_to_idx_dict[next_pos]
            if gamemap.grid[i][j] == "w" or next_pos in self.positions[1:]:
                self.dead_next_move = 1
        except:
            pass

    def draw(self, screen):
        for i in range(len(self.positions)):
            tex = ""
            if i == 0 and len(self.positions) > 1:
                if self.positions[i+1][0] > self.positions[i][0]:
                    if self.positions[i+1][0] - STEPSIZE > self.positions[i][0]:
                        tex = self.tail_left
                    else:
                        tex = self.tail_right
                elif self.positions[i+1][0] < self.positions[i][0]:
                    if self.positions[i+1][0] + STEPSIZE < self.positions[i][0]:
                        tex = self.tail_right
                    else:
                        tex = self.tail_left
                elif self.positions[i+1][1] > self.positions[i][1]:
                    if self.positions[i+1][1] - STEPSIZE > self.positions[i][1]:
                        tex = self.tail_up
                    else:
                        tex = self.tail_down
                else:
                    if self.positions[i+1][1] + STEPSIZE < self.positions[i][1]:
                        tex = self.tail_down
                    else:
                        tex = self.tail_up
            elif i < len(self.positions)-1:
                if self.positions[i-1][0] == self.positions[i+1][0]:
                    tex = self.ver_tex
                elif self.positions[i-1][1] == self.positions[i+1][1]:
                    tex = self.hor_tex
                else:
                    tex = self.get_curve(i)
            else:
                if self.direction[0] == 1:
                    tex = self.head_right
                elif self.direction[0] == -1:
                    tex = self.head_left
                elif self.direction[1] == 1:
                    tex = self.head_down
                elif self.direction[1] == -1:
                    tex = self.head_up
            if tex != "":
                screen.blit(tex,  self.positions[i])

    def get_curve(self, idx):
        curve = ""
        # Vertical
        if self.positions[idx-1][1] < self.positions[idx][1]:
            if self.positions[idx-1][1] + STEPSIZE == self.positions[idx][1]:
                curve += "up"
            else:
                curve += "down"
        elif self.positions[idx+1][1] < self.positions[idx][1]:
            if self.positions[idx+1][1] + STEPSIZE == self.positions[idx][1]:
                curve += "up"
            else:
                curve += "down"
        elif self.positions[idx-1][1] > self.positions[idx][1]:
            if self.positions[idx-1][1] - STEPSIZE == self.positions[idx][1]:
                curve += "down"
            else:
                curve += "up"
        elif self.positions[idx+1][1] > self.positions[idx][1]:
            if self.positions[idx+1][1] - STEPSIZE == self.positions[idx][1]:
                curve += "down"
            else:
                curve += "up"
        # Horizontal
        if self.positions[idx-1][0] < self.positions[idx][0]:
            if self.positions[idx-1][0] + STEPSIZE == self.positions[idx][0]:
                curve += "left"
            else:
                curve += "right"
        elif self.positions[idx+1][0] < self.positions[idx][0]:
            if self.positions[idx+1][0] + STEPSIZE == self.positions[idx][0]:
                curve += "left"
            else:
                curve += "right"
        elif self.positions[idx-1][0] > self.positions[idx][0]:
            if self.positions[idx-1][0] - STEPSIZE == self.positions[idx][0]:
                curve += "right"
            else:
                curve += "left"
        elif self.positions[idx+1][0] > self.positions[idx][0]:
            if self.positions[idx+1][0] - STEPSIZE == self.positions[idx][0]:
                curve += "right"
            else:
                curve += "left"
        return self.curves[curve]  


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
        max_i = int(HEIGHT / STEPSIZE)
        max_j = int(WIDTH / STEPSIZE)
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
                pos = (pos[0] + STEPSIZE, pos[1])
            self.grid.append(row)
            pos = (0, pos[1] + STEPSIZE)

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
            i = random.randint(1, HEIGHT / STEPSIZE -1)
            j = random.randint(1, WIDTH / STEPSIZE -1)
            if self.grid[i][j] == "" and (i, j) not in illegal_positions:
                self.grid[i][j] = "f"
                self.spawn_food = False
            if loop_counter > 5:
                break
            loop_counter += 1
        loop_counter = 0
        while spawn_big_food:
            self.big_food_spawned = True
            self.big_food_timer = BIG_FOOD_TIME
            i = random.randint(1, HEIGHT / STEPSIZE -2)
            j = random.randint(1, WIDTH / STEPSIZE -2)
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

def main():
    pygame.init()

    # TODO: Logo
    logo = pygame.image.load("img/snake_logo.png")
    pygame.display.set_icon(logo)
    
    pygame.display.set_caption("Snake")

    screen = pygame.display.set_mode((WIDTH, HEIGHT + 40))

    background_tex = pygame.image.load("img/background.png")
   
    snakebits = [
        pygame.image.load("img/snakebits/snakebit_hor.png"),
        pygame.image.load("img/snakebits/snakebit_ver.png"),
        pygame.image.load("img/snakebits/snakebit_curve_upleft.png"),
        pygame.image.load("img/snakebits/snakebit_curve_upright.png"),
        pygame.image.load("img/snakebits/snakebit_curve_downright.png"),
        pygame.image.load("img/snakebits/snakebit_curve_downleft.png"),
        pygame.image.load("img/snakebits/snakebit_head_up.png"),
        pygame.image.load("img/snakebits/snakebit_head_down.png"),
        pygame.image.load("img/snakebits/snakebit_head_left.png"),
        pygame.image.load("img/snakebits/snakebit_head_right.png"),
        pygame.image.load("img/snakebits/snakebit_tail_up.png"),
        pygame.image.load("img/snakebits/snakebit_tail_down.png"),
        pygame.image.load("img/snakebits/snakebit_tail_left.png"),
        pygame.image.load("img/snakebits/snakebit_tail_right.png"),
    ]
  
    food_tex     = pygame.image.load("img/food.png")
    big_food_tex = pygame.image.load("img/big_food.png")
    wall_tex     = pygame.image.load("img/wall.png")

    ui_font = pygame.font.SysFont("monospace", 25, True)
    big_food_font = pygame.font.SysFont("monospace", 50, True)

    highscore = get_highscore()
    maptype = MAP_TYPE

    gamemap = GameMap(wall_tex, food_tex, big_food_tex, maptype)
    snake   = Snake((WIDTH / 2+25, HEIGHT / 2), snakebits)

    # Export map
    gamemap.export_map("saved/map_%d_export.txt" % maptype)

    try:
        gamemap.import_map("saved/map_%d_custom.txt" % maptype)
    except:
        pass

    running = True
    while running:
        exit_code = play_game(screen, gamemap, snake, highscore, background_tex, ui_font, big_food_font)
        if exit_code == 1:
            gamemap = GameMap(wall_tex, food_tex, big_food_tex, maptype)
            snake   = Snake((WIDTH / 2+25, HEIGHT / 2), snakebits) 
        elif exit_code == 0:
            running = False

def play_game(screen, gamemap, snake, highscore, background_tex, ui_font, big_food_font):
    beat_highscore = False
  
    last_update = pygame.time.get_ticks() - UPDATE_FREQ
    last_big_food = pygame.time.get_ticks() - BIG_FOOD_FREQ / 2
    
    direction_input = (-1, -1)

    running = True
    paused  = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_a] \
                and snake.direction[0] != 1:
                    direction_input = (-1, 0)
                elif event.key in [pygame.K_RIGHT, pygame.K_d] \
                and snake.direction[0] != -1:
                    direction_input = (1, 0)
                elif event.key in [pygame.K_UP, pygame.K_w] \
                and snake.direction[1] != 1:
                    direction_input = (0, -1)
                elif event.key in [pygame.K_DOWN, pygame.K_s] \
                and snake.direction[1] != -1:
                    direction_input = (0, 1)
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                
                    
        if not snake.alive and not paused:
            return 1

        now = pygame.time.get_ticks()
        if now - last_update >= UPDATE_FREQ + snake.dead_next_move * UPDATE_FREQ * LIFESAVER_TIME_FACTOR and not paused:
            # Update logic
            spawn_big_food = now - last_big_food >= BIG_FOOD_FREQ
            if spawn_big_food:
                last_big_food = now
            gamemap.update(snake, spawn_big_food)
            snake.update(gamemap, direction_input)
            direction_input = (-1, -1)
            last_update = now


            score = snake.size - START_SIZE
            if score > highscore:
                highscore = score
                beat_highscore = True
                
            gamemap.big_food_timer -= UPDATE_FREQ

            if gamemap.big_food_timer <= 0 and gamemap.big_food_spawned:
                gamemap.big_food_eaten(-1, -1)


            if not snake.alive:
                paused = True
                replay_label = ui_font.render("Press space to restart.", 1, (210, 232, 218))
                screen.blit(replay_label, ((WIDTH/3) + 50, (HEIGHT/2)))
                if beat_highscore:
                    save_highscore(highscore)
                    new_highscore_label = ui_font.render("Congratulations - New Highscore!", 1, (210, 232, 218))
                    screen.blit(new_highscore_label, ((WIDTH/3)-20, HEIGHT/2 - 50))
            else:
                # clear screen
                screen.blit(background_tex, (0,0))
                # Draw map
                gamemap.draw(screen)
                # Draw snake
                snake.draw(screen)
                # Draw score label
                score_label = ui_font.render("Score: %d" % score, 1, (210, 232, 218))
                screen.blit(score_label, (WIDTH * 0.15, HEIGHT + 5))
                # Draw highscore label
                highscore_label = ui_font.render("Highscore: %d" % highscore, 1, (210, 232, 218))
                screen.blit(highscore_label, (WIDTH * 0.7, HEIGHT + 5))
                # Draw big food timer
                if gamemap.big_food_spawned:
                    big_food_label = big_food_font.render("%d" % (gamemap.big_food_timer / UPDATE_FREQ), 1, (210, 232, 218))
                    screen.blit(big_food_label, (WIDTH*0.45, HEIGHT*0.1))

            # Update screen
            pygame.display.flip()
        

    return 0

def get_highscore():
    try:
        with open("saved/highscore.txt", "r") as f:
            highscore = int(f.readline())
        return highscore
    except:
        return 0

def save_highscore(score):
    with open("saved/highscore.txt", "w") as f:
        f.write(str(score))

if __name__ == "__main__":
    main()