import pygame
import os

import constants as const
import gamemap_object as gmap
import snake_object as snek


class GameManager(object):
    def __init__(self):
        pygame.init()

        self.my_path = "%s/.." % os.path.dirname(os.path.realpath(__file__))
        logo = pygame.image.load("%s/img/snake_logo.png" % self.my_path)
        pygame.display.set_icon(logo)

        pygame.display.set_caption("Snake")

        self.screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT + 40))

        self.background_tex = pygame.image.load("%s/img/background.png" % self.my_path)
        self.menu_tex       = pygame.image.load("%s/img/menu.png" % self.my_path)
        self.food_tex       = pygame.image.load("%s/img/food.png" % self.my_path)
        self.big_food_tex   = pygame.image.load("%s/img/big_food.png" % self.my_path)
        self.wall_tex       = pygame.image.load("%s/img/wall.png" % self.my_path)

        self.snakebits = [
            pygame.image.load("%s/img/snakebits/snakebit_hor.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_ver.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_curve_upleft.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_curve_upright.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_curve_downright.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_curve_downleft.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_head_up.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_head_down.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_head_left.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_head_right.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_tail_up.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_tail_down.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_tail_left.png" % self.my_path),
            pygame.image.load("%s/img/snakebits/snakebit_tail_right.png" % self.my_path),
        ]


        self.ui_font = pygame.font.SysFont("monospace", 25, True)
        self.big_food_font = pygame.font.SysFont("monospace", 50, True)

        self.get_highscore()
        self.maptype = const.MAP_TYPE

        self.gamemap = gmap.GameMap(self.wall_tex, self.food_tex, self.big_food_tex, self.maptype)
        self.snake   = snek.Snake((const.WIDTH / 2+25, const.HEIGHT / 2), self.snakebits)

        # Export map
        self.gamemap.export_map("%s/saved/map_%d_export.txt" % (self.my_path, self.maptype))

        self.lightblue_color = (210, 232, 218)
        self.pink_color      = (224,  79, 127)

        try:
            self.gamemap.import_map("%s/saved/map_%d_custom.txt" % (self.my_path, self.maptype))
        except:
            pass

    def start(self):
        running = True
        #menu_exit_code = self.game_menu()
        #if menu_exit_code == -1:
        #    return
        while running:
            exit_code = self.play_game()
            if exit_code == 1:
                self.gamemap = gmap.GameMap(self.wall_tex, self.food_tex, self.big_food_tex, self.maptype)
                self.snake   = snek.Snake((const.WIDTH / 2+25, const.HEIGHT / 2), self.snakebits)
            elif exit_code == 0:
                running = False

    def game_menu(self):
        running = True
        direction_input = (-1,-1)
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        direction_input = (-1, 0)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        direction_input = (1, 0)
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        direction_input = (0, -1)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        direction_input = (0, 1)

            # clear screen
            self.screen.blit(self.menu_tex, (0,0))

            # Title
            menu_title_label = self.big_food_font.render("Snake", 1, self.pink_color)
            self.screen.blit(menu_title_label, (const.WIDTH*0.45, 60))
            # Level menu
            level_select_label = self.ui_font.render("Select level", 1, self.pink_color)
            self.screen.blit(level_select_label, (const.WIDTH*0.44, 250))


            pygame.display.flip()


    def play_game(self):
        beat_highscore = False

        last_update = pygame.time.get_ticks() - const.UPDATE_FREQ
        last_big_food = pygame.time.get_ticks() - const.BIG_FOOD_FREQ / 2

        direction_input = (-1, -1)
        move_queue = []

        running = True
        paused  = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        direction_input = (-1, 0)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        direction_input = (1, 0)
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        direction_input = (0, -1)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        direction_input = (0, 1)
                    elif event.key == pygame.K_SPACE:
                        paused = not paused

            if not self.snake.alive and not paused:
                return 1
            if len(move_queue) < 3 and direction_input != (-1, -1):
                move_queue.append(direction_input)
            elif len(move_queue) == 0:
                move_queue.append(direction_input)
            direction_input = (-1, -1)

            now = pygame.time.get_ticks()
            if now - last_update >= const.UPDATE_FREQ + self.snake.dead_next_move * const.UPDATE_FREQ * const.LIFESAVER_TIME_FACTOR and not paused:
                # Update logic
                spawn_big_food = now - last_big_food >= const.BIG_FOOD_FREQ
                if spawn_big_food:
                    last_big_food = now
                self.gamemap.update(self.snake, spawn_big_food)

                next_move = move_queue[0]
                move_queue = move_queue[1:]

                self.snake.update(self.gamemap, next_move)
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
                    replay_label = self.ui_font.render("Press space to restart.", 1, self.lightblue_color)
                    self.screen.blit(replay_label, ((const.WIDTH/3) + 50, (const.HEIGHT/2)))
                    if beat_highscore:
                        self.save_highscore()
                        new_highscore_label = self.ui_font.render("Congratulations - New Highscore!", 1, self.lightblue_color)
                        self.screen.blit(new_highscore_label, ((const.WIDTH/3)-20, const.HEIGHT/2 - 50))
                else:
                    # clear screen
                    self.screen.blit(self.background_tex, (0,0))
                    # Draw map
                    self.gamemap.draw(self.screen)
                    # Draw snake
                    self.snake.draw(self.screen)
                    # Draw score label
                    score_label = self.ui_font.render("Score: %d" % score, 1, self.lightblue_color)
                    self.screen.blit(score_label, (const.WIDTH * 0.15, const.HEIGHT + 5))
                    # Draw highscore label
                    highscore_label = self.ui_font.render("Highscore: %d" % self.highscore, 1, self.lightblue_color)
                    self.screen.blit(highscore_label, (const.WIDTH * 0.7, const.HEIGHT + 5))
                    # Draw big food timer
                    if self.gamemap.big_food_spawned:
                        big_food_label = self.big_food_font.render("%d" % (self.gamemap.big_food_timer / const.UPDATE_FREQ), 1, self.lightblue_color)
                        self.screen.blit(big_food_label, (const.WIDTH*0.45, const.HEIGHT*0.1))

                # Update screen
                pygame.display.flip()


        return 0

    def get_highscore(self):
        try:
            with open("%s/saved/highscore.txt" % self.my_path, "r") as f:
                self.highscore = int(f.readline())
        except:
            self.highscore = 0

    def save_highscore(self):
        with open("%s/saved/highscore.txt" % self.my_path, "w") as f:
            f.write(str(self.highscore))
