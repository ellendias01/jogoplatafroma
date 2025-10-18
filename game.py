import pgzrun
import random
from pygame import Rect, transform

WIDTH = 800
HEIGHT = 600
TITLE = "Hero Adventure Platformer"

game_state = "menu"  # menu, playing, finished
sound_on = True
camera_x = 0  # posição da câmera
score = 0     # contador de moedas

def load_scaled(name, size=(70, 70)):
    img = images.load(name)
    surf = transform.scale(img, size)
    return surf

hero_idle_surf = [load_scaled("hero_stand", (70, 70))]
hero_run_surf = [
    load_scaled("hero_run", (70, 70)),
    load_scaled("hero_run2", (70, 70))
]

enemy_surf = [load_scaled("enemy1", (60, 60))]
menu_bg_surf = transform.scale(images.menu_bg, (WIDTH, HEIGHT))
forest_bg_surf = transform.scale(images.forest_bg, (2000, HEIGHT))
coin_surf = transform.scale(images.coin, (30, 30))  

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width, self.height = 30, 30
        self.rect = Rect(self.x, self.y, self.width, self.height)

    def draw(self, offset_x):
        screen.surface.blit(coin_surf, (self.x - offset_x, self.y))

coins = [Coin(500, HEIGHT-100), Coin(900, HEIGHT-100), Coin(1500, HEIGHT-100)]

class Character:
    def __init__(self, x, y, idle_sprites, run_sprites):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width, self.height = idle_sprites[0].get_size()
        self.on_ground = False
        self.idle_sprites = idle_sprites
        self.run_sprites = run_sprites
        self.frame = 0
        self.rect = Rect(self.x, self.y, self.width, self.height)

    def move(self):
        self.vy += 0.5  
        self.y += self.vy
        self.x += self.vx

        if self.y + self.height >= HEIGHT - 40:  
            self.y = HEIGHT - 40 - self.height
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        self.rect.topleft = (self.x, self.y)

    def draw(self, offset_x=0):
        sprite_list = self.run_sprites if self.vx != 0 else self.idle_sprites
        self.frame += 0.15  
        if self.frame >= len(sprite_list):
            self.frame = 0
        sprite = sprite_list[int(self.frame)]
        screen.surface.blit(sprite, (self.x - offset_x, self.y))

class Hero(Character):
    def jump(self):
        if self.on_ground:
            self.vy = -12
            if sound_on:
                sounds.jump.play()

class Enemy(Character):
    def __init__(self, x, y, sprite_surf, territory):
        super().__init__(x, y, [sprite_surf], [sprite_surf])
        self.territory = territory
        self.vx = random.choice([-2, 2])

    def move(self):
        super().move()
        if self.x < self.territory[0]:
            self.vx = 2
        elif self.x + self.width > self.territory[1]:
            self.vx = -2

hero = Hero(100, HEIGHT - 150, hero_idle_surf, hero_run_surf)
enemies = [
    Enemy(400, HEIGHT - 150, enemy_surf[0], (350, 600)),
    Enemy(800, HEIGHT - 150, enemy_surf[0], (700, 1100)),
    Enemy(1300, HEIGHT - 150, enemy_surf[0], (1200, 1600))
]

from pygame import Rect as PyRect
btn_start = PyRect(WIDTH//2 - 100, 200, 200, 50)
btn_sound = PyRect(WIDTH//2 - 100, 300, 200, 50)
btn_exit = PyRect(WIDTH//2 - 100, 400, 200, 50)

def draw():
    screen.clear()
    global camera_x
    if game_state == "menu":
        screen.surface.blit(menu_bg_surf, (0, 0))
        screen.draw.filled_rect(btn_start, "green")
        screen.draw.text("START GAME", center=btn_start.center, color="white", fontsize=30)
        screen.draw.filled_rect(btn_sound, "orange")
        screen.draw.text(f"SOUND: {'ON' if sound_on else 'OFF'}", center=btn_sound.center, color="white", fontsize=30)
        screen.draw.filled_rect(btn_exit, "red")
        screen.draw.text("EXIT", center=btn_exit.center, color="white", fontsize=30)
    elif game_state in ["playing", "finished"]:
        camera_x = hero.x - WIDTH//2
        if camera_x < 0:
            camera_x = 0
        max_camera = forest_bg_surf.get_width() - WIDTH
        if camera_x > max_camera:
            camera_x = max_camera

        screen.surface.blit(forest_bg_surf, (-camera_x, 0))
        screen.draw.filled_rect(PyRect(0, HEIGHT-40, WIDTH, 40), "brown") 

        for coin in coins:
            coin.draw(camera_x)
        for enemy in enemies:
            enemy.draw(camera_x)
        hero.draw(camera_x)
        screen.draw.text(f"Coins: {score}", (10, 10), fontsize=30, color="yellow")

        if game_state == "finished":
            screen.draw.text("YOU WIN!", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="green")

def update():
    global game_state, score
    if game_state == "playing":
        hero.move()
        for enemy in enemies:
            enemy.move()
            if hero.rect.colliderect(enemy.rect):
                if sound_on:
                    sounds.hit.play()
                reset_level()
        for coin in coins[:]:
            if hero.rect.colliderect(coin.rect):
                coins.remove(coin)
                score += 1
                if sound_on:
                    sounds.coin.play()
        if hero.x > 1900:
            game_state = "finished"
            music.stop()

def on_key_down(key):
    if game_state == "playing":
        if key == keys.RIGHT:
            hero.vx = 6
        elif key == keys.LEFT:
            hero.vx = -6
        elif key == keys.SPACE:
            hero.jump()

def on_key_up(key):
    if key in (keys.RIGHT, keys.LEFT):
        hero.vx = 0

def on_mouse_down(pos):
    global game_state, sound_on, score, coins
    if game_state == "menu":
        if btn_start.collidepoint(pos):
            game_state = "playing"
            if sound_on:
                music.play("forest_theme")
            sounds.click.play()
            score = 0
            coins = [Coin(500, HEIGHT-100), Coin(900, HEIGHT-100), Coin(1500, HEIGHT-100)]
        elif btn_sound.collidepoint(pos):
            sound_on = not sound_on
            if sound_on:
                music.play("forest_theme")
            else:
                music.stop()
            sounds.click.play()
        elif btn_exit.collidepoint(pos):
            exit()

def reset_level():
    hero.x, hero.y = 100, HEIGHT - 150
    hero.vx, hero.vy = 0, 0
    for enemy in enemies:
        enemy.x = random.randint(enemy.territory[0], enemy.territory[1])
        enemy.vx = random.choice([-2, 2])
pgzrun.go()