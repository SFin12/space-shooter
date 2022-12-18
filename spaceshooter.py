import pygame
import os
import random
pygame.font.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1600, 1000
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Shooter')

# load images
RED_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_red_small.png'))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png'))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_blue_small.png'))

# Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_yellow.png'))

# Power Ups
SHIELD_GENERATOR = pygame.image.load(os.path.join('assets', 'pixel_shield.png'))
FAST_LASER = pygame.image.load(os.path.join('assets', 'laser-power-up.png'))

# Explosion
EXPLOSION = pygame.image.load(os.path.join('assets', 'explosion-small.png'))

# lasers
RED_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_red.png'))
GREEN_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_green.png'))
BLUE_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_blue.png'))
YELLOW_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_yellow.png'))

# sounds
PLAYER_LASER = pygame.mixer.Sound('assets/laser1.wav')
PLAYER_LASER.set_volume(.7)
ENEMY_LASER = pygame.mixer.Sound('assets/laser1.wav')
ENEMY_LASER.set_volume(0.2)
EXPLOSION_SOUND = pygame.mixer.Sound('assets/explosion.wav')
EXPLOSION_SOUND.set_volume(0.5)
SHIELD_RECHARGE = pygame.mixer.Sound('assets/shield-charge.wav')
SHIELD_RECHARGE.set_volume(0.5)
CHANNEL_2 = pygame.mixer.Channel(2)
NEXT_LEVEL = pygame.mixer.Sound('assets/next-level.wav')
NEXT_LEVEL.set_volume(0.4)
CHANNEL_2.play(NEXT_LEVEL)


# background
BG = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'background-black-wide.png')),(WIDTH,HEIGHT))

class Laser:
    
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel    

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return Collision(self, obj).collide()

class Ship:
    COOLDOWN  = 12
    def __init__(self, x, y, health = 100):
        self.starting_x = x
        self.stargin_y = y
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 5
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >=  self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
            
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            PLAYER_LASER.play()
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
    
    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    
    LASER_COLOR_MAP = {
                'yellow': YELLOW_LASER,
                'red': RED_LASER,
                'green': GREEN_LASER,
                'blue': BLUE_LASER
                }
    
    def __init__(self, x, y, laser_color = "yellow", health = 100):
        self.kills = 0
        self.total_shots = 0
        super().__init__(x, y, health)
        self.laser_color = laser_color
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = self.LASER_COLOR_MAP[self.laser_color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    
    def set_laser_color(self, color):
        self.laser_img = self.LASER_COLOR_MAP[color]

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
                self.total_shots += 1
            else: 
                for obj in objs:
                    if laser.collision(obj):
                        self.total_shots += 1
                        self.kills += 1
                        obj.explode()
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def decrease_cooldown(self):
        if self.COOLDOWN > 4:
            self.COOLDOWN  -= 2
        else:
            self.COOLDOWN = 4
        if self.COOLDOWN < 4 and self.COOLDOWN < 9:
            self.set_laser_color('blue')
        elif self.COOLDOWN == 4:
            self.set_laser_color('red')
        
    def reset_cooldown(self):
        self.COOLDOWN  = Ship.COOLDOWN
        self.set_laser_color('yellow')

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width()* (self.health/self.max_health), 10))
    
    def getKills(self):
        return self.kills

    def getAccuracy(self):
        if not self.kills or not self.total_shots:
            return 0
        return round((self.kills / self.total_shots) * 100)

class Enemy(Ship):
    EXPLODE_TIMER = 5
    COLOR_MAP = {
                'red': (RED_SPACE_SHIP, RED_LASER),
                'green': (GREEN_SPACE_SHIP, GREEN_LASER),
                'blue': (BLUE_SPACE_SHIP, BLUE_LASER)
                }
    def __init__(self, x, y, color, health = 100):
        super().__init__(x,y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.color = color
        self.exploded = False

    def move(self, vel):
        self.y += vel
        if self.color == 'blue':
            self.y += .2
        if self.color == 'red':
            self.y -= .2
    
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y, self.laser_img)
            ENEMY_LASER.play()
            self.lasers.append(laser)
            self.cool_down_counter -= .5
    
    def explode(self):
        EXPLOSION_SOUND.play()
        self.ship_img = EXPLOSION
        self.exploded = True

class Power_up(Ship):
    TYPE_MAP = {
                'shield': (SHIELD_GENERATOR, BLUE_LASER),
                'laser': (FAST_LASER, RED_LASER)
                }
    def __init__(self, x, y, type, health = 100):
        super().__init__(x,y, health)
        
        self.ship_img, self.laser_img = self.TYPE_MAP[type]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.type = type

    def move(self, vel):
      if self.starting_x < 0:
        self.x += vel
      if self.starting_x >= WIDTH:
        self.x -= vel
class Collision:
    EXPLOSION_TIME = 15

    def __init__(self, obj1, obj2, img = EXPLOSION):
        self.obj1 = obj1
        self.obj2 = obj2
        self.img = img
        self.explosion_counter = 0 
        self.mask = pygame.mask.from_surface(self.img)
        self.collision_que = []

    def collide(self):
        offset_x = self.obj2.x - self.obj1.x
        offset_y = self.obj2.y - self.obj1.y
        self.collision_que.append(self.obj1)
        return self.obj1.mask.overlap(self.obj2.mask, (offset_x, offset_y)) != None
    
    def explode(self, WINDOW):
        return WINDOW.blit(self.img, (self.obj1.x, self.obj1.y))
    
    def explosion_countdown(self):
        if self.explosion_counter >=  self.EXPLOSION_TIME:
            self.explosion_counter = 0
        elif self.explosion_counter < self.EXPLOSION_TIME:
            self.explosion_counter += 1

def main():
    run = True
    FPS = 60
    level = 0
    level_indicator = level -1
    lives = 10
    main_font = pygame.font.SysFont('comicsans', 40)
    lost_font = pygame.font.SysFont('comicsans', 60)
    enemies = []
    enemy_vel = 2
    power_ups = []
    power_up_vel = 2
    laser_timer = 0
    laser_on = False
    wave_length = 6
    player = Player(300, 550)
    player_vel = 15
    laser_vel = 20
    clock = pygame.time.Clock()
    lost = False
    lost_count = 0
    kills = 0
    accuracy = 0

    def redraw_window():
        nonlocal run
        WINDOW.blit(BG, (0,0))
        # draw text
        nonlocal kills
        nonlocal accuracy
        kills = player.getKills()
        accuracy = player.getAccuracy()
        lives_label = main_font.render(f"lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"level: {level}", 1, (255,255,255))
        kills_label = main_font.render(f"kills: {kills}", 1, (255,255,255))
        accuracy_label = main_font.render(f"accuracy: {accuracy}%", 1, (255,255,255))

        WINDOW.blit(lives_label, (10,10))
        WINDOW.blit(accuracy_label, (300,10))
        WINDOW.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WINDOW.blit(kills_label, (WIDTH - level_label.get_width() - 300, 10))
        
        for enemy in enemies:
            enemy.draw(WINDOW)
            if enemy.exploded:
                enemy.EXPLODE_TIMER -= 1
            if enemy.EXPLODE_TIMER == 0:
                enemies.remove(enemy)
        for power_up in power_ups:
            power_up.draw(WINDOW)
        

        player.draw(WINDOW)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WINDOW.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, HEIGHT/2))
            if lost_count > FPS * 5:
                run = False

        pygame.display.update()
        

    while run:
        clock.tick(FPS)
        if laser_on and laser_timer > 0:
            laser_timer -= 1
        if laser_on and laser_timer < 1:
            player.reset_cooldown()
            laser_on = False
            
        redraw_window()
        
        # Every five levels
        if level_indicator > 1 and level_indicator % 3 == 0:
            CHANNEL_2.play(NEXT_LEVEL)  

        if lost == True:
            
            if lost_count > 60:
                run = False
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if len(enemies) == 0:
            level += 1
            level_indicator +=1
            wave_length += 1
            enemy_vel += .2
            
            # generates random enemy ships
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(['red','blue', 'green']))
                enemies.append(enemy)
            # generates random power-ups. 20% accuracy allows a max of 5, 24 = max of 6...
            for i in range(random.randrange(0, min(wave_length // 2, max(4, accuracy // 4)))):
                # power_up = Power_up(random.randrange(50, WIDTH-100), random.randrange(-1600, -100), random.choice(['shield','laser']))
                power_up = Power_up(random.choice([random.randrange(-1500, -100),random.randrange(WIDTH + 100, WIDTH + 1500)]), random.randrange(30, 700), random.choice(['shield','laser']))
                power_ups.append(power_up)

        if lives == 1 or player.health == 10 or player_vel - level < 10:
            player_vel  = 18

        if level_indicator > 2:
            if level_indicator // 4 == 0 and Ship.COOLDOWN > 8:
              Ship.COOLDOWN -= 1
            if player_vel < 18:
                player_vel += 1
            level_indicator = 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # says what happens when specific keys are pressed.
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: #left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player.get_width() + player_vel < WIDTH: #right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - 50 - player_vel > 0: #up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player.get_height() + player_vel + 10 < HEIGHT: #down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            e_collision_check = Collision(enemy, player)
            if enemy.color == 'red' and random.randrange(0, 40) == 1:
                enemy.shoot()
            if enemy.color == 'green' and random.randrange(0, 80) == 1:
                enemy.shoot()
            if enemy.color == 'blue' and random.randrange(0, 120) == 1:
                enemy.shoot()
            if e_collision_check.collide():
                if not enemy.exploded:
                    player.health -= 10
                enemy.explode()
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        for power_up in power_ups[:]:
          power_up.move(power_up_vel)
          power_up.move_lasers(laser_vel, player)
          p_collision_check = Collision(power_up, player)
          
          if p_collision_check.collide():
              SHIELD_RECHARGE.play()
              if power_up.type == 'shield':
                  player.health = 100
                  lives += 1
                  power_ups.remove(power_up)
              if power_up.type == 'laser':
                  laser_on = True
                  laser_timer = 600
            
                  player.decrease_cooldown()
                  player.decrease_cooldown()
                  power_ups.remove(power_up)
          elif power_up.y + power_up.get_height() > HEIGHT or power_up.x > WIDTH + 1500 or power_up.x < -1500:              
              power_ups.remove(power_up)
            
        player.move_lasers(- laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WINDOW.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WINDOW.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                main()
    pygame.quit()            


main_menu()
