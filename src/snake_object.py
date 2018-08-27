import constants as const

class Snake(object):
    def __init__(self, startpos, snakebits):
        self.positions = [startpos]
        self.size = const.START_SIZE
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
        new_head = (head[0] + self.direction[0] * const.STEPSIZE, head[1] + self.direction[1] * const.STEPSIZE)
        try:
            row, col = gamemap.position_to_idx_dict[new_head]
        except KeyError:
            if self.direction[0] == 1:
                new_head = (0, new_head[1])
            elif self.direction[0] == -1:
                new_head = (const.WIDTH - const.STEPSIZE, new_head[1])
            elif self.direction[1] == 1:
                new_head = (new_head[0], 0)
            elif self.direction[1] == -1:
                new_head = (new_head[0], const.HEIGHT - const.STEPSIZE)

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
            next_pos = (new_head[0] + self.direction[0] * const.STEPSIZE, new_head[1] + self.direction[1] * const.STEPSIZE)
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
                    if self.positions[i+1][0] - const.STEPSIZE > self.positions[i][0]:
                        tex = self.tail_left
                    else:
                        tex = self.tail_right
                elif self.positions[i+1][0] < self.positions[i][0]:
                    if self.positions[i+1][0] + const.STEPSIZE < self.positions[i][0]:
                        tex = self.tail_right
                    else:
                        tex = self.tail_left
                elif self.positions[i+1][1] > self.positions[i][1]:
                    if self.positions[i+1][1] - const.STEPSIZE > self.positions[i][1]:
                        tex = self.tail_up
                    else:
                        tex = self.tail_down
                else:
                    if self.positions[i+1][1] + const.STEPSIZE < self.positions[i][1]:
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
            if self.positions[idx-1][1] + const.STEPSIZE == self.positions[idx][1]:
                curve += "up"
            else:
                curve += "down"
        elif self.positions[idx+1][1] < self.positions[idx][1]:
            if self.positions[idx+1][1] + const.STEPSIZE == self.positions[idx][1]:
                curve += "up"
            else:
                curve += "down"
        elif self.positions[idx-1][1] > self.positions[idx][1]:
            if self.positions[idx-1][1] - const.STEPSIZE == self.positions[idx][1]:
                curve += "down"
            else:
                curve += "up"
        elif self.positions[idx+1][1] > self.positions[idx][1]:
            if self.positions[idx+1][1] - const.STEPSIZE == self.positions[idx][1]:
                curve += "down"
            else:
                curve += "up"
        # Horizontal
        if self.positions[idx-1][0] < self.positions[idx][0]:
            if self.positions[idx-1][0] + const.STEPSIZE == self.positions[idx][0]:
                curve += "left"
            else:
                curve += "right"
        elif self.positions[idx+1][0] < self.positions[idx][0]:
            if self.positions[idx+1][0] + const.STEPSIZE == self.positions[idx][0]:
                curve += "left"
            else:
                curve += "right"
        elif self.positions[idx-1][0] > self.positions[idx][0]:
            if self.positions[idx-1][0] - const.STEPSIZE == self.positions[idx][0]:
                curve += "right"
            else:
                curve += "left"
        elif self.positions[idx+1][0] > self.positions[idx][0]:
            if self.positions[idx+1][0] - const.STEPSIZE == self.positions[idx][0]:
                curve += "right"
            else:
                curve += "left"
        return self.curves[curve]  
