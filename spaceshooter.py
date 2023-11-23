import pygame
import os
import random
import threading
pygame.font.init()
pygame.mixer.init()
pygame.joystick.init()
pygame.display.init()
CONTROLLERS = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
CONTROLLER_1 = None
CONTROLLER_2 = None
if len(CONTROLLERS):
    CONTROLLER_1 = CONTROLLERS[0]
if len(CONTROLLERS) > 1:
    CONTROLLER_2 = CONTROLLERS[1]

MONITOR_HEIGHT = pygame.display.Info().current_h
WIDTH, HEIGHT = 1400, min(1200, MONITOR_HEIGHT-100)

if CONTROLLER_2:
    WIDTH = 1600

WINDOW = pygame.display.set_mode((WIDTH + 250, HEIGHT))
pygame.display.set_caption('Space Shooter')

# load images
RED_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_red_small.png'))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_green_small.png'))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_blue_small.png'))
ORANGE_ENEMY_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_orange_medium.png'))


# Player shipS
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_yellow.png'))
YELLOW_SPACE_SHIP_BURNER = pygame.image.load(os.path.join('assets', 'pixel_ship_yellow_burner.png'))
ORANGE_SPACE_SHIP = pygame.image.load(os.path.join('assets', 'pixel_ship_orange.png'))
ORANGE_SPACE_SHIP_BURNER = pygame.image.load(os.path.join('assets', 'pixel_ship_orange_burner.png'))
ORANGE_SPACE_SHIP_SHIELD = pygame.image.load(os.path.join('assets', 'pixel_ship_orange_shield.png'))
YELLOW_SPACE_SHIP_SHIELD = pygame.image.load(os.path.join('assets', 'pixel_ship_yellow_shield.png'))

# Player Font Colors
WHITE_FONT = (255, 255, 255)
YELLOW_FONT = (225,188,41)
ORANGE_FONT = (255, 119, 43)
GREEN_FONT = (50,255,50)
RED_FONT = (255,50,50)

# Power Ups
SHIELD_GENERATOR = pygame.image.load(os.path.join('assets', 'pixel_shield.png'))
FAST_LASER = pygame.image.load(os.path.join('assets', 'laser-power-up.png'))
SPEED_BOOST = pygame.image.load(os.path.join('assets', 'energy.png'))
HEALTH_PACK = pygame.image.load(os.path.join('assets', 'health.png'))

# Explosion
EXPLOSION = pygame.image.load(os.path.join('assets', 'explosion-small.png'))

# lasers
RED_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_red.png'))
GREEN_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_green.png'))
BLUE_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_blue.png'))
YELLOW_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_yellow.png'))
ORANGE_LASER = pygame.image.load(os.path.join('assets', 'pixel_laser_orange.png'))

# sounds
PLAYER_LASER = pygame.mixer.Sound('assets/laser1.wav')
PLAYER_LASER.set_volume(.7)
ENEMY_LASER = pygame.mixer.Sound('assets/laser1.wav')
ENEMY_LASER.set_volume(0.2)
EXPLOSION_SOUND = pygame.mixer.Sound('assets/explosion.wav')
EXPLOSION_SOUND.set_volume(0.4)
THUD_SOUND = pygame.mixer.Sound('assets/thud.wav')
THUD_SOUND.set_volume(0.4)

SHIELD_RECHARGE = pygame.mixer.Sound('assets/shield-charge.wav')
SHIELD_RECHARGE.set_volume(0.4)
CHANNEL_2 = pygame.mixer.Channel(2)
NEXT_LEVEL = pygame.mixer.Sound('assets/next-level.wav')
NEXT_LEVEL.set_volume(0.4)
CHANNEL_2.play(NEXT_LEVEL)


# background
BG = pygame.transform.scale(pygame.image.load(os.path.join('assets', 'background-black-wide.png')),(WIDTH,HEIGHT))
INFO_RECT = pygame.Rect(WIDTH, 0, 250, HEIGHT)




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
        self.starting_y = y
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
                if not obj.shield_on:
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
                'blue': BLUE_LASER,
                'orange': ORANGE_LASER
                }
    
    def __init__(self, x, y, laser_color = "yellow", health = 100, player = 1):
        self.kills = 0
        self.total_shots = 0
        self.speed = 15
        self.shield_on = False
        super().__init__(x, y, health)
        if player == 1:
            self.ship_img = YELLOW_SPACE_SHIP
        else: 
            self.ship_img = ORANGE_SPACE_SHIP
        self.laser_color = laser_color
        # self.ship_img = None
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

    def turn_on_shield(self):
        self.shield_on = True
        
    def turn_off_shield(self):
        self.shield_on = False

    def decrease_cooldown(self):
        if self.COOLDOWN > 4:
            self.COOLDOWN  -= 2
        else:
            self.COOLDOWN = 4
        if self.COOLDOWN > 4 and self.COOLDOWN < 9:
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
                'blue': (BLUE_SPACE_SHIP, BLUE_LASER),
                'orange': (ORANGE_ENEMY_SPACE_SHIP, ORANGE_LASER)
                }
    def __init__(self, x, y, color, health = 100):
        super().__init__(x,y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.color = color
        self.exploded = False
        self.ZIG_ZAG_TIMER = random.randint(0,199)

    def move(self, vel):
        self.y += vel
        if self.color == 'blue':
            self.y += .2
        if self.color == 'red':
            self.y -= .2
        if self.color == "orange":
            self.y -= 1
            if self.x < WIDTH - self.get_width() and self.x > 0:
                
                if self.ZIG_ZAG_TIMER < 100:
                    self.x += random.randint(2,5)
                    self.ZIG_ZAG_TIMER += 1
                elif self.ZIG_ZAG_TIMER < 200:
                    self.x -= random.randint(2,5)
                    self.ZIG_ZAG_TIMER += 1
                else:
                    self.ZIG_ZAG_TIMER = 0
            elif self.x >= WIDTH - self.get_width():
                self.x -= 5
                self.ZIG_ZAG_TIMER = 100
            elif self.x < 0:
                self.x += 5
                self.ZIG_ZAG_TIMER = 0
            
    
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y, self.laser_img)
            ENEMY_LASER.play()
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
    def explode(self):
        EXPLOSION_SOUND.play()
        self.ship_img = EXPLOSION
        self.exploded = True

class Power_up(Ship):
    TYPE_MAP = {
                'shield': (SHIELD_GENERATOR, BLUE_LASER),
                'laser': (FAST_LASER, RED_LASER),
                'speed': (SPEED_BOOST, RED_LASER),
                'health': (HEALTH_PACK, RED_LASER)
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
    # Get the height of the background image
    BG_HEIGHT = BG.get_height()

# Initialize the y-coordinates for the two background images
    BG_Y1 = 0
    BG_Y2 = -BG_HEIGHT  # Initially off the screen
    run = True
    FPS = 60
    clock = pygame.time.Clock()
    lost = False
    lost_count = 0
    level = 0
    level_indicator = level -1
    lives = 10
    main_font = pygame.font.SysFont('comicsans', 30)
    message_font = pygame.font.SysFont('comicsans', 60)
    warning_messages = []
    warning_messages_current = None
    message_timer = 150
    line_height = 50
    enemies = []
    enemy_vel = 1
    power_ups = []
    power_up_vel = 2
    wave_length = 11
    laser_vel = 20
    scroll_speed = 1
    player_1 = Player(WIDTH/2, 650)
    p1_laser_timer = 0
    p1_laser_on = False
    p1_speed_timer = 0
    p1_speed_on = False
    p1_shield_timer = 0
    p1_player_vel = 13
    p1_kills = 0
    p1_accuracy = 0
    p1_shoot_slow = 0
    
    player_2 = None

    if CONTROLLER_2:
        player_2 = Player(WIDTH/2, 650, "orange", 100, 2)
        p2_laser_timer = 0
        p2_laser_on = False
        p2_speed_timer = 0
        p2_speed_on = False
     
        p2_shield_timer = 0
        p2_player_vel = 13
        p2_kills = 0
        p2_accuracy = 0
        p2_shoot_slow = 0
    
    def redraw_backround():
        WINDOW.blit(BG, (0,BG_Y1))
        WINDOW.blit(BG, (0,BG_Y2))

    def redraw_window():
        nonlocal run
        nonlocal p1_kills
        nonlocal p1_accuracy
        nonlocal p2_kills
        nonlocal p2_accuracy
        nonlocal warning_messages_current
        nonlocal warning_messages_current
        nonlocal message_timer
        

        for enemy in enemies:
            enemy.draw(WINDOW)
            if enemy.exploded:
                enemy.EXPLODE_TIMER -= 1
            if enemy.EXPLODE_TIMER == 0:
                enemies.remove(enemy)
        for power_up in power_ups:
            power_up.draw(WINDOW)
        

        player_1.draw(WINDOW)

        if player_2:
            player_2.draw(WINDOW)


        if lost:
            lost_label = message_font.render("You Lost!!", 1, (255,255,255))
            WINDOW.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 300))
            if lost_count > FPS * 30:
                run = False

        pygame.draw.rect(WINDOW, (10,10,10), INFO_RECT)
        
        # draw text
        p1_kills = player_1.getKills()
        p1_accuracy = player_1.getAccuracy()
        if player_2:
            p2_kills = player_2.getKills()
            p2_accuracy = player_2.getAccuracy()

        # on screen text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        player_1_label = main_font.render(f"PLAYER 1", 1, YELLOW_FONT)
        p1_kills_label = main_font.render(f"kills: {p1_kills}", 1, (255,255,255))
        p1_accuracy_label = main_font.render(f"accuracy: {p1_accuracy}%", 1, (255,255,255))
        if player_2:
            player_2_label = main_font.render(f"PLAYER 2", 1, ORANGE_FONT)
            p2_kills_label = main_font.render(f"kills: {p2_kills}", 1, (255,255,255))
            p2_accuracy_label = main_font.render(f"accuracy: {p2_accuracy}%", 1, (255,255,255))

        if len(warning_messages):
            warning_messages_current = warning_messages.pop(0)
        
        if warning_messages_current:
            warning_label = message_font.render(warning_messages_current["message"], 1, warning_messages_current["color"])
            WINDOW.blit(warning_label, (WIDTH/2 - warning_label.get_width()/2, 200))
            if message_timer > 0:
                message_timer -= 1
            else:
                warning_messages_current = None
                message_timer = 100

        
        WINDOW.blit(level_label, (WIDTH + 10, 5))
        WINDOW.blit(lives_label, (WIDTH + 10, line_height * 1.5))
        WINDOW.blit(player_1_label, (WIDTH + 10, line_height * 4))
        WINDOW.blit(p1_accuracy_label, (WIDTH + 10, line_height * 5))
        WINDOW.blit(p1_kills_label, (WIDTH + 10, line_height * 6))
        if player_2:
            WINDOW.blit(player_2_label, (WIDTH + 10, line_height * 8))
            WINDOW.blit(p2_accuracy_label, (WIDTH + 10, line_height * 9))
            WINDOW.blit(p2_kills_label, (WIDTH + 10, line_height * 10))


        pygame.display.update()
    


    while run:
        clock.tick(FPS)
        # Move the background images
        BG_Y1 += scroll_speed
        BG_Y2 += scroll_speed

        # If the first BG image goes off the screen, reset its position
        if BG_Y1 >= HEIGHT:
            BG_Y1 = -BG_HEIGHT

        # If the second BG image goes off the screen, reset its position
        if BG_Y2 >= HEIGHT:
            BG_Y2 = -BG_HEIGHT

        if p1_laser_on and p1_laser_timer > 0:
            p1_laser_timer -= 1
        if p1_laser_on and p1_laser_timer < 1:
            player_1.reset_cooldown()
            p1_laser_on = False

        if player_2:
            if p2_laser_on and p2_laser_timer > 0:
                p2_laser_timer -= 1
            if p2_laser_on and p2_laser_timer < 1:
                player_2.reset_cooldown()
                p2_laser_on = False
        
        if p1_speed_on and p1_speed_timer > 0:
            p1_speed_timer -= 1
            player_1.ship_img = YELLOW_SPACE_SHIP_BURNER
        if p1_speed_on and p1_speed_timer < 1:
            player_1.ship_img = YELLOW_SPACE_SHIP
            p1_player_vel = 13
            p1_speed_on = False

        if player_2:
            if p2_speed_on and p2_speed_timer > 0:
                p2_speed_timer -= 1
                player_2.ship_img = ORANGE_SPACE_SHIP_BURNER
            if p2_speed_on and p2_speed_timer < 1:
                player_2.ship_img = ORANGE_SPACE_SHIP
                p2_player_vel = 13
                p2_speed_on = False

        if player_1.shield_on and p1_shield_timer > 0:
            p1_shield_timer -= 1
            player_1.ship_img = YELLOW_SPACE_SHIP_SHIELD
        if player_1.shield_on and p1_shield_timer < 1:
            player_1.ship_img = YELLOW_SPACE_SHIP
            player_1.turn_off_shield()

        if player_2:
            if player_2.shield_on and p2_shield_timer > 0:
                p2_shield_timer -= 1
                player_2.ship_img = ORANGE_SPACE_SHIP_SHIELD
            if player_2.shield_on and p2_shield_timer < 1:
                player_2.ship_img = ORANGE_SPACE_SHIP
                player_2.turn_off_shield()
        
        seperate_thread = threading.Thread(target=redraw_window)
        seperate_thread.start()
        seperate_thread.join()
        
        background_thread = threading.Thread(target=redraw_backround)
        background_thread.start()
        # Every five levels
        if level > 2 and level_indicator % 3 == 0:
            CHANNEL_2.play(NEXT_LEVEL)  

        if lost == True:
            enemies = []
            if lost_count > FPS * 20:
                run = False
            elif lost_count == 2:
                CHANNEL_2.play(NEXT_LEVEL) 
        if lives <= 0 or player_1.health  <= 0 or player_2 and player_2.health <=0:
            lost = True
            lost_count += 1

        if len(enemies) == 0 and not lost:
            level += 1
            warning_messages.append({"message": f"level: {level}", "color": GREEN_FONT})
            level_indicator +=1
            wave_length += 1
            enemy_vel += .2
            
            # generates random enemy ships
            for i in range(wave_length):
                if level > 6:
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(['red','blue', 'green', 'orange']))
                else:
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(['red','blue', 'green']))

                enemies.append(enemy)
            # generates random power-ups. 20% accuracy allows a max of 5, 24 = max of 6...
            combined_accuracy = p1_accuracy
            if player_2:
                combined_accuracy = (p1_accuracy + p2_accuracy / 1.5)
            for i in range(random.randrange(0, min(wave_length // 2, max(4, combined_accuracy // 4)))):
                power_up = Power_up(random.choice([random.randrange(-1500, -100),random.randrange(WIDTH + 100, WIDTH + 1500)]), random.randrange(30, 700), random.choice(['shield','laser', 'speed', 'health']))
                power_ups.append(power_up)

        if lives == 1 or player_1.health == 10 or p1_player_vel - level < 10:
            if p1_player_vel < 19:
                p1_player_vel += 2

        if player_2 and lives == 1 or player_2 and player_2.health == 10 or player_2 and p2_player_vel - level < 10:
            if p1_player_vel < 19:
                p2_player_vel += 2

        if level % 4 == 0:
            if Ship.COOLDOWN > 8:
                Ship.COOLDOWN -= 1
            if p1_player_vel < 18:
                p1_player_vel += 1
            if player_2 and p2_player_vel < 18:
                p2_player_vel += 1
            level_indicator = 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        # Only used for controller
        if CONTROLLER_1:
            # get x axis of first analog stick
            if abs(CONTROLLER_1.get_axis(0)) > .2: 
                
                x_vel = CONTROLLER_1.get_axis(0) * p1_player_vel
                if  player_1.x - p1_player_vel > 0 and x_vel < 0:
                    player_1.x += x_vel
                if player_1.x + player_1.get_width() + p1_player_vel < WIDTH and x_vel > 0:
                    player_1.x += x_vel
            # get y axis of first analog stick        
            if abs(CONTROLLER_1.get_axis(1)) > .2:
                y_vel = CONTROLLER_1.get_axis(1) * p1_player_vel 
                if  player_1.y - p1_player_vel > 0 and y_vel < 0:
                    player_1.y += y_vel
                if player_1.y + player_1.get_height() + p1_player_vel + 12 < HEIGHT and y_vel > 0:
                    player_1.y += y_vel
                
            
            if CONTROLLER_1.get_axis(5) >= .2 and CONTROLLER_1.get_axis(5) < .7:
                if p1_shoot_slow:
                    p1_shoot_slow -= 1
                else:
                    player_1.shoot()
                    p1_shoot_slow = 10
            if CONTROLLER_1.get_axis(5) >= .8:
                player_1.shoot()


        if player_2:
            # get x axis of first analog stick
            if abs(CONTROLLER_2.get_axis(0)) > .2: 
                
                x_vel = CONTROLLER_2.get_axis(0) * p2_player_vel
                if  player_2.x - p2_player_vel > 0 and x_vel < 0:
                    player_2.x += x_vel
                if player_2.x + player_2.get_width() + p2_player_vel < WIDTH and x_vel > 0:
                    player_2.x += x_vel
            # get y axis of first analog stick        
            if abs(CONTROLLER_2.get_axis(1)) > .2:
                y_vel = CONTROLLER_2.get_axis(1) * p2_player_vel 
                if  player_2.y - p2_player_vel > 0 and y_vel < 0:
                    player_2.y += y_vel
                if player_2.y + player_2.get_height() + p2_player_vel + 12 < HEIGHT and y_vel > 0:
                    player_2.y += y_vel
                
            
            if CONTROLLER_2.get_axis(5) >= .2 and CONTROLLER_2.get_axis(5) < .7:
                if p2_shoot_slow:
                    p2_shoot_slow -= 1
                else:
                    player_2.shoot()
                    p2_shoot_slow = 10
            if CONTROLLER_2.get_axis(5) >= .8:
                player_2.shoot()

        if not player_2:
            # says what happens when specific keys are pressed. One player only
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                run = False
            if keys[pygame.K_LEFT] and player_1.x - p1_player_vel > 0: #left
                player_1.x -= p1_player_vel
            if keys[pygame.K_RIGHT] and player_1.x + player_1.get_width() + p1_player_vel < WIDTH: #right
                player_1.x += p1_player_vel
            if keys[pygame.K_UP] and player_1.y - 50 - p1_player_vel > 0: #up
                player_1.y -= p1_player_vel
            if keys[pygame.K_DOWN] and player_1.y + player_1.get_height() + p1_player_vel + 12 < HEIGHT: #down
                player_1.y += p1_player_vel
            if keys[pygame.K_SPACE]:
                player_1.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player_1)
            p1_collision_check = Collision(enemy, player_1)
            if p1_collision_check.collide():
                if not enemy.exploded:
                    if not player_1.shield_on:
                      player_1.health -= 15
                    enemy.explode()
            if player_2:
                enemy.move_lasers(laser_vel, player_2)
                p2_collision_check = Collision(enemy, player_2)
                if p2_collision_check.collide():
                    if not enemy.exploded:
                        if not player_2.shield_on:
                          player_2.health -= 15
                        enemy.explode()
            if enemy.color == 'orange' and random.randrange(0, 50) == 1:
                enemy.shoot()
            if enemy.color == 'red' and random.randrange(0, 200) == 1:
                enemy.shoot()
            if enemy.color == 'green' and random.randrange(0, 400) == 1:
                enemy.shoot()
            if enemy.color == 'blue' and random.randrange(0, 500) == 1:
                enemy.shoot()
            
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                THUD_SOUND.play()
                warning_messages.append({"message": f"{lives} lives left", "color": RED_FONT})
                enemies.remove(enemy)

        # power-up logic
        for power_up in power_ups[:]:
          power_up.move(power_up_vel)
          
          if player_2:
            p2_collision_check = Collision(power_up, player_2)
            if p2_collision_check.collide():
              SHIELD_RECHARGE.play()
              if power_up.type == 'health':
                  player_2.health = 100
                  lives += 1
                  power_ups.remove(power_up)
              if power_up.type == 'laser':
                  p2_laser_on = True
                  p2_laser_timer = 500
                  player_2.decrease_cooldown()
                  player_2.decrease_cooldown()
                  power_ups.remove(power_up)
              if power_up.type == 'speed':
                  p2_speed_on = True
                  p2_speed_timer = 300
                  p2_player_vel = 20
                  power_ups.remove(power_up)
              if power_up.type == 'shield':
                  player_2.turn_on_shield()
                  p2_shield_timer = 300
                  power_ups.remove(power_up)
          p1_collision_check = Collision(power_up, player_1)
          if p1_collision_check.collide():
              SHIELD_RECHARGE.play()
              if power_up.type == 'health':
                  player_1.health = 100
                  lives += 1
                  power_ups.remove(power_up)
              if power_up.type == 'laser':
                  p1_laser_on = True
                  p1_laser_timer = 500
            
                  player_1.decrease_cooldown()
                  player_1.decrease_cooldown()
                  power_ups.remove(power_up)
              if power_up.type == 'speed':
                  p1_speed_on = True
                  p1_speed_timer = 300
                  p1_player_vel = 20
                  power_ups.remove(power_up)
              if power_up.type == 'shield':
                  player_1.turn_on_shield()
                  p1_shield_timer = 300
                  power_ups.remove(power_up)
              
          elif power_up.y + power_up.get_height() > HEIGHT or power_up.x > WIDTH + 1500 or power_up.x < -1500:              
              power_ups.remove(power_up)
            
        player_1.move_lasers(- laser_vel, enemies)
        if player_2:
            player_2.move_lasers(- laser_vel, enemies)




def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    directions_font = pygame.font.SysFont("comicsans", 50)
    # one_player = pygame.Rect(300,200,200,100)
    # two_player = pygame.Rect(WIDTH - 500,200,200,100)
    run = True
    while run:
        WINDOW.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        directions = directions_font.render("Higher accuracy + levels = More upgrades!", 1, (250,250,250))
        WINDOW.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        WINDOW.blit(directions, (WIDTH/2 - directions.get_width()/2, 450))
        # ONE_PLAYER = pygame.draw.rect(WINDOW, (90,255,90), (one_player), border_radius=10)
        # TWO_PLAYER = None
        # if CONTROLLER_2:
        #     TWO_PLAYER = pygame.draw.rect(WINDOW, (90,255,90), (two_player), border_radius=10)
            
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN  or event.type == pygame.KEYDOWN or CONTROLLER_1 and CONTROLLER_1.get_axis(5) > .5:
                main()
                # if event.button == 1:
                #     if ONE_PLAYER.collidepoint(event.pos):
                #         main()
                #     if TWO_PLAYER and TWO_PLAYER.collidepoint(event.pos):
                #         pass
                
    pygame.quit()            


main_menu()
