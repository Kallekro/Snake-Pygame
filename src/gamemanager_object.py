import pygame

import constants as const
import snake_object as snek
import gamemap_object as gmap

class GameManager(object):
    def __init__(self):
        pygame.init()

        # TODO: Logo
        logo = pygame.image.load("img/snake_logo.png")
        pygame.display.set_icon(logo)
        
        pygame.display.set_caption("Snake")

        self.screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT + 40))

        self.background_tex = pygame.image.load("img/background.png")
        self.food_tex     = pygame.image.load("img/food.png")
        self.big_food_tex = pygame.image.load("img/big_food.png")
        self.wall_tex     = pygame.image.load("img/wall.png")
    
        self.snakebits = [
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
    

        self.ui_font = pygame.font.SysFont("monospace", 25, True)
        self.big_food_font = pygame.font.SysFont("monospace", 50, True)

        self.get_highscore()
        self.maptype = const.MAP_TYPE

        self.gamemap = gmap.GameMap(self.wall_tex, self.food_tex, self.big_food_tex, self.maptype)
        self.snake   = snek.Snake((const.WIDTH / 2+25, const.HEIGHT / 2), self.snakebits)

        # Export map
        self.gamemap.export_map("saved/map_%d_export.txt" % self.maptype)

        try:
            self.gamemap.import_map("saved/map_%d_custom.txt" % self.maptype)
        except:
            pass

    def start(self):
        running = True
        while running:
            exit_code = self.play_game()
            if exit_code == 1:
                self.gamemap = gmap.GameMap(self.wall_tex, self.food_tex, self.big_food_tex, self.maptype)
                self.snake   = snek.Snake((const.WIDTH / 2+25, const.HEIGHT / 2), self.snakebits) 
            elif exit_code == 0:
                running = False


    def play_game(self):
        beat_highscore = False
    
        last_update = pygame.time.get_ticks() - const.UPDATE_FREQ
        last_big_food = pygame.time.get_ticks() - const.BIG_FOOD_FREQ / 2
        
        direction_input = (-1, -1)

        running = True
        paused  = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LEFT, pygame.K_a] \
                    and self.snake.direction[0] != 1:
                        direction_input = (-1, 0)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d] \
                    and self.snake.direction[0] != -1:
                        direction_input = (1, 0)
                    elif event.key in [pygame.K_UP, pygame.K_w] \
                    and self.snake.direction[1] != 1:
                        direction_input = (0, -1)
                    elif event.key in [pygame.K_DOWN, pygame.K_s] \
                    and self.snake.direction[1] != -1:
                        direction_input = (0, 1)
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    
                        
            if not self.snake.alive and not paused:
                return 1

            now = pygame.time.get_ticks()
            if now - last_update >= const.UPDATE_FREQ + self.snake.dead_next_move * const.UPDATE_FREQ * const.LIFESAVER_TIME_FACTOR and not paused:
                # Update logic
                spawn_big_food = now - last_big_food >= const.BIG_FOOD_FREQ
                if spawn_big_food:
                    last_big_food = now
                self.gamemap.update(self.snake, spawn_big_food)
                self.snake.update(self.gamemap, direction_input)
                direction_input = (-1, -1)
                last_update = now


                score = self.snake.size - const.START_SIZE
                if score > self.highscore:
                    self.highscore = score
                    beat_highscore = True
                    
                self.gamemap.big_food_timer -= const.UPDATE_FREQ

                if self.gamemap.big_food_timer <= 0 and self.gamemap.big_food_spawned:
                    self.gamemap.big_food_eaten(-1, -1)


                if not self.snake.alive:
                    paused = True
                    replay_label = self.ui_font.render("Press space to restart.", 1, (210, 232, 218))
                    self.screen.blit(replay_label, ((const.WIDTH/3) + 50, (const.HEIGHT/2)))
                    if beat_highscore:
                        self.save_highscore()
                        new_highscore_label = self.ui_font.render("Congratulations - New Highscore!", 1, (210, 232, 218))
                        self.screen.blit(new_highscore_label, ((const.WIDTH/3)-20, const.HEIGHT/2 - 50))
                else:
                    # clear screen
                    self.screen.blit(self.background_tex, (0,0))
                    # Draw map
                    self.gamemap.draw(self.screen)
                    # Draw snake
                    self.snake.draw(self.screen)
                    # Draw score label
                    score_label = self.ui_font.render("Score: %d" % score, 1, (210, 232, 218))
                    self.screen.blit(score_label, (const.WIDTH * 0.15, const.HEIGHT + 5))
                    # Draw highscore label
                    highscore_label = self.ui_font.render("Highscore: %d" % self.highscore, 1, (210, 232, 218))
                    self.screen.blit(highscore_label, (const.WIDTH * 0.7, const.HEIGHT + 5))
                    # Draw big food timer
                    if self.gamemap.big_food_spawned:
                        big_food_label = self.big_food_font.render("%d" % (self.gamemap.big_food_timer / const.UPDATE_FREQ), 1, (210, 232, 218))
                        self.screen.blit(big_food_label, (const.WIDTH*0.45, const.HEIGHT*0.1))

                # Update screen
                pygame.display.flip()
            

        return 0

    def get_highscore(self):
        try:
            with open("saved/highscore.txt", "r") as f:
                self.highscore = int(f.readline())
        except:
            self.highscore = 0

    def save_highscore(self):
        with open("saved/highscore.txt", "w") as f:
            f.write(str(self.highscore))