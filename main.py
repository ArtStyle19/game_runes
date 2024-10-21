import pygame as pg
import os
import sys
from button import Button
pg.init() 

BG = pg.image.load("../assets/Background.png")

PLAY_BUTTON = Button(image=pg.image.load("../assets/Play Rect.png"), pos=(640, 250), 
                    text_input="PLAY", font=pg.font.Font("../assets/font.ttf", 75), base_color="#d7fcd4", hovering_color="White")
OPTIONS_BUTTON = Button(image=pg.image.load("../assets/Options Rect.png"), pos=(640, 400), 
                    text_input="OPTIONS", font=pg.font.Font("../assets/font.ttf", 75), base_color="#d7fcd4", hovering_color="White")
QUIT_BUTTON = Button(image=pg.image.load("../assets/Quit Rect.png"), pos=(640, 550), 
                    text_input="QUIT", font=pg.font.Font("../assets/font.ttf", 75), base_color="#d7fcd4", hovering_color="White")


class Player():
    def __init__(self, game):
        self.game = game
        self.position_x, self.position_y = 100, 100
        self.width, self.height = 30, 30
        self.speed = 100  
        self.health = 1000  
        self.max_health = 1000 
        self.current_frame = 0
        self.last_frame_update = 0
        self.animation_cooldown = 150
        self.load_sprites()
        self.direction = "down"  

    def update(self, delta_time, actions):
        direction_x = actions["right"] - actions["left"]
        direction_y = actions["down"] - actions["up"]
        self.position_x += self.speed * delta_time * direction_x
        self.position_y += self.speed * delta_time * direction_y
        self.animate(delta_time, direction_x, direction_y)

        for enemy in self.game.enemies:
            if self.is_colliding_with_enemy(enemy):
                self.take_damage(10)  

        if self.health <= 0:
            self.game.next = 'menu'  
            self.game.done = True  

    def animate(self, delta_time, direction_x, direction_y):
        if direction_x != 0 or direction_y != 0:  
            self.last_frame_update += delta_time * 1000  
            if self.last_frame_update >= self.animation_cooldown:
                self.last_frame_update = 0  # Reset frame update time
                self.current_frame = (self.current_frame + 1) % len(self.front_sprites)

            if direction_x < 0:
                self.direction = "left"
            elif direction_x > 0:
                self.direction = "right"
            elif direction_y < 0:
                self.direction = "up"
            elif direction_y > 0:
                self.direction = "down"

            self.curr_image = self.front_sprites[self.current_frame]

    def is_colliding_with_enemy(self, enemy):
        player_rect = pg.Rect(self.position_x, self.position_y, self.width, self.height)
        enemy_rect = pg.Rect(enemy.position_x, enemy.position_y, enemy.enemy_width, enemy.enemy_height)
        return player_rect.colliderect(enemy_rect)

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def render(self, display):
        scaled_image = pg.transform.scale(self.curr_image, (self.width, self.height))
        display.blit(scaled_image, (self.position_x, self.position_y))
        self.draw_health_bar(display)

    def draw_health_bar(self, display):
        health_bar_length = 200  
        health_bar_height = 20   
        health_ratio = self.health / self.max_health  
        health_bar_width = health_bar_length * health_ratio
        health_bar_x = 20
        health_bar_y = 20
        pg.draw.rect(display, (0, 0, 0), (health_bar_x, health_bar_y, health_bar_length, health_bar_height))
        color = (255 * (1 - health_ratio), 255 * health_ratio, 0)
        pg.draw.rect(display, color, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))

    def game_over(self):
        self.game.next = 'menu'  
        self.game.done = True  

    def load_sprites(self):
        self.sprite_dir = os.path.join(self.game.sprite_dir, "player")
        self.front_sprites = [pg.image.load(os.path.join(self.sprite_dir, "player_front" + str(i) + ".png")) for i in range(1, 5)]
        self.curr_image = self.front_sprites[0]

class Enemy():
    def __init__(self, game, x, y):
        self.game = game
        self.position_x, self.position_y = x, y
        self.enemy_width, self.enemy_height = 30, 30  
        self.health = 100  
        self.max_health = 100  
        self.speed = 1.5  
        self.chase_range = 200  
        self.current_frame, self.last_frame_update = 0, 0
        self.load_sprites()

    def update(self, delta_time):
        player_x, player_y = self.game.player.position_x, self.game.player.position_y
        distance_x = player_x - self.position_x
        distance_y = player_y - self.position_y
        distance_to_player = (distance_x ** 2 + distance_y ** 2) ** 0.5  # Euclidean distance

        if distance_to_player < self.chase_range:
            self.move_towards_player(player_x, player_y)

    def move_towards_player(self, player_x, player_y):
        direction_x = player_x - self.position_x
        direction_y = player_y - self.position_y

        distance = (direction_x ** 2 + direction_y ** 2) ** 0.5  

        if distance != 0:
            direction_x /= distance
            direction_y /= distance

        self.position_x += direction_x * self.speed
        self.position_y += direction_y * self.speed

    def render(self, display):
        scaled_image = pg.transform.scale(self.curr_image, (self.enemy_width, self.enemy_height))  # Set enemy size
        display.blit(scaled_image, (self.position_x, self.position_y))
        self.draw_health_bar(display)

    def draw_health_bar(self, display):
        health_bar_length = 50  
        health_bar_height = 5  
        health_ratio = self.health / self.max_health  
        health_bar_width = health_bar_length * health_ratio
        health_bar_x = self.position_x + (self.enemy_width // 2) - (health_bar_length // 2)
        health_bar_y = self.position_y - 10  

        pg.draw.rect(display, (0, 0, 0), (health_bar_x, health_bar_y, health_bar_length, health_bar_height))
        pg.draw.rect(display, (0, 255, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))

    def load_sprites(self):
        self.sprite_dir = os.path.join(self.game.sprite_dir, "player")
        self.front_sprites = [pg.image.load(os.path.join(self.sprite_dir, "player_front" + str(i) + ".png")) for i in range(1, 5)]
        self.curr_image = self.front_sprites[0]

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.game.enemies.remove(self)
            if len(self.game.enemies) == 0:  
                self.game.next = 'menu'  
                self.game.done = True  



def get_font(size): 
    return pg.font.Font("../assets/font.ttf", size)
  
class States(object):
    def __init__(self):
        self.mousePos = pg.mouse.get_pos()
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None

  
class Menu(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'game'
        self.buttons = [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]
    def cleanup(self):
        print('cleaning up Menu state stuff')
    def startup(self):
        print('starting Menu state stuff')
    def get_event(self, event):
        self.mousePos = pg.mouse.get_pos()  

        if event.type == pg.KEYDOWN:
            print('Menu State keydown')

        if event.type == pg.MOUSEBUTTONDOWN:
            if PLAY_BUTTON.checkForInput(self.mousePos):
                self.done = True
            if OPTIONS_BUTTON.checkForInput(self.mousePos):
                options()
            if QUIT_BUTTON.checkForInput(self.mousePos):
                pg.quit()
                sys.exit()

    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        screen.blit(BG, (0, 0))

        print(self.mousePos)
        MENU_TEXT = pg.font.Font("../assets/font.ttf", 100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))
        screen.blit(MENU_TEXT, MENU_RECT)
        for button in self.buttons:
            button.changeColor(self.mousePos)
            button.update(screen)
  
class Game(States):
    def __init__(self):
        States.__init__(self)
        self.next = 'menu'
        self.assets_dir = os.path.join("../assets")
        self.grass_img = pg.image.load(os.path.join(self.assets_dir, "map", "grass.png"))
        self.sprite_dir = os.path.join(self.assets_dir, "sprites")
        self.font_dir = os.path.join(self.assets_dir, "font")
        self.font=pg.font.Font(os.path.join(self.font_dir, "PressStart2P-vaV7.ttf"), 20)
        self.player = Player(self)
        self.actions = {"left": False, "right": False, "up" : False, "down" : False, "action1" : False, "action2" : False, "start" : False}
        self.screen_width, self.screen_height = 1280, 720  # Set screen dimensions here
        self.enemies = []  
        self.spawn_enemies()
        self.load_audio()  


    def load_audio(self):
        pg.mixer.init()  
        pg.mixer.music.load(os.path.join("../assets", "background_music.mp3")) 
        pg.mixer.music.set_volume(0.5)  
        pg.mixer.music.play(-1)  



    def spawn_enemies(self):
        self.enemies.append(Enemy(self, 210, 210))
        self.enemies.append(Enemy(self, 230, 230))
        self.enemies.append(Enemy(self, 700, 400))

    def update(self, screen, dt):
        screen.fill("../#ffffff")
        self.player.update(0.03, self.actions)

        for enemy in self.enemies:
            enemy.update(dt)
            enemy.render(screen)

        if self.actions['action1']:
            self.handle_attacks()

        self.draw(screen)

    def handle_attacks(self):
        attack_range = 50  
        for enemy in self.enemies:
            distance_x = abs(self.player.position_x - enemy.position_x)
            distance_y = abs(self.player.position_y - enemy.position_y)
            if distance_x < attack_range and distance_y < attack_range:
                enemy.take_damage(1)  

    def draw(self, screen):
        background_image = pg.transform.scale(self.grass_img, (self.screen_width, self.screen_height))
        screen.blit(background_image, (0, 0))

        for enemy in self.enemies:
            enemy.render(screen)

        self.player.render(screen)


    def cleanup(self):
        print('cleaning up Game state stuff')

    def startup(self):
        print('starting Game state stuff')

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True
            if event.key == pg.K_a:
                self.actions['left'] = True
            if event.key == pg.K_d:
                self.actions['right'] = True
            if event.key == pg.K_w:
                self.actions['up'] = True
            if event.key == pg.K_s:
                self.actions['down'] = True
            if event.key == pg.K_p:
                self.actions['action1'] = True

        if event.type == pg.KEYUP:
            if event.key == pg.K_a:
                self.actions['left'] = False
            if event.key == pg.K_d:
                self.actions['right'] = False
            if event.key == pg.K_w:
                self.actions['up'] = False
            if event.key == pg.K_s:
                self.actions['down'] = False
            if event.key == pg.K_p:
                self.actions['action1'] = False
  
class Control:
    def __init__(self, **settings):
        self.__dict__.update(settings)
        self.done = False
        self.screen = pg.display.set_mode(self.size)
        self.clock = pg.time.Clock()
        self.load_assets()

    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def flip_state(self):
        self.state.done = False
        previous,self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup()
        self.state.previous = previous

    def update(self, dt):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.screen, dt)

    def load_assets(self):
        self.assets_dir = os.path.join("../assets")
        self.sprite_dir = os.path.join(self.assets_dir, "sprites")
        self.font_dir = os.path.join(self.assets_dir, "font")
        self.font=pg.font.Font(os.path.join(self.font_dir, "PressStart2P-vaV7.ttf"), 20)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            self.state.get_event(event)

            
    def main_game_loop(self):
        while not self.done:
            delta_time = self.clock.tick(self.fps)/1000.0
            self.event_loop()
            self.update(delta_time)
            pg.display.update()

# def resource_path(relative_path):
#     """ Get the absolute path to the resource, works for development and PyInstaller """
#     try:
#         # PyInstaller creates a temp folder and stores path in _MEIPASS
#         base_path = sys._MEIPASS
#     except AttributeError:
#         base_path = os.path.abspath("../.")

#     return os.path.join(base_path, relative_path)

  
settings = {
    'size':(1280, 720),
    'fps' :60
}
  
app = Control(**settings)
state_dict = {
    'menu': Menu(),
    'game': Game()
}
app.setup_states(state_dict, 'menu')
app.main_game_loop()
pg.quit()
sys.exit()



