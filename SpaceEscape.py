#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pygame
import random
import os


# In[2]:


#initialize
FPS = 60
WIDTH = 500
HEIGHT = 600

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255, 255,0)

#build game and windows
pygame.init()
pygame.mixer.init() #base for sound
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Space Escape")
clock = pygame.time.Clock()

#add image
background_img = pygame.image.load(os.path.join("img","background.png")).convert()
player_img = pygame.image.load(os.path.join("img","player.png")).convert()
player_img_mini = pygame.transform.scale(player_img, (25,20))
player_img_mini.set_colorkey(BLACK)
pygame.display.set_icon(player_img_mini)
bullet_img = pygame.image.load(os.path.join("img","bullet.png")).convert()
# rock_img = pygame.image.load(os.path.join("img","rock.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img",f"rock{i}.png")).convert())
explode_animation = {}
explode_animation['large'] = []
explode_animation['small'] = []
explode_animation['player'] = []
for i in range(9):
    expl_img = pygame.image.load(os.path.join("img",f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    explode_animation['large'].append(pygame.transform.scale(expl_img, (75,75)))
    explode_animation['small'].append(pygame.transform.scale(expl_img, (30,30)))
    
    player_expl_img = pygame.image.load(os.path.join("img",f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    explode_animation['player'].append(player_expl_img)
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("img","shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("img","gun.png")).convert()

#font
font_name = pygame.font.match_font('arial')
    
#music / sound effect
shoot_sound = pygame.mixer.Sound(os.path.join("sound","shoot.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound","pow0.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound","pow1.wav"))
player_die = pygame.mixer.Sound(os.path.join("sound","rumble.ogg"))
explode_sounds = [
    pygame.mixer.Sound(os.path.join("sound","expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound","expl1.wav"))
]
pygame.mixer.music.load(os.path.join("sound","background.ogg"))
pygame.mixer.music.set_volume(0.4)


# In[3]:


#player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img,(50,38)) #image transformation
        self.image.set_colorkey(BLACK) #transparent background of spaceship
        self.rect = self.image.get_rect() #get position of image
        self.radius = 20
#         pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT-10
        self.speedx = 8
        self.health = 100
        self.chances = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0
        
    def update(self):
        now = pygame.time.get_ticks()
        
        #upgrade gun for 3 second
        if self.gun >1 and now - self.gun_time > 3000:
            self.gun -=1
            self.gun_time = now
        
        #hide 1 sec if die
        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT-10
            
#         #auto move right and loop (testing)
#         self.rect.x +=2
#         if self.rect.left > WIDTH:
#             self.rect.right = 0
        key_pressed = pygame.key.get_pressed() #get keyboard key
        if key_pressed[pygame.K_d]: #right
            self.rect.x += self.speedx
        if key_pressed[pygame.K_a]: #left
            self.rect.x -= self.speedx
        
        #prevent going out of screen
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
            
    def shoot(self):
        if not(self.hidden): #if not yet die
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx,self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play() #play sound effect
            elif self.gun >=2:
                bullet1 = Bullet(self.rect.left,self.rect.centery)
                bullet2 = Bullet(self.rect.right,self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play() #play sound effect
            
    #hide player before another chance
    def hide_player(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+500)
        
    def gunup(self):
        self.gun +=1
        self.gun_time = pygame.time.get_ticks()


# In[4]:


#rock class
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs) #to solve rotation problem
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy() #image
        self.rect = self.image.get_rect() #get position of image
        self.radius = int(self.rect.width * 0.85 / 2)
#         pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180,-100)
        self.speedy = random.randrange(2,10)
        self.speedx = random.randrange(-3,3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-5,5)
        
    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center #to get the center of every rotation
        self.rect = self.image.get_rect()
        self.rect.center = center
    
    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        #if rock out of screen, then drop another one, to continue
        if (self.rect.top > HEIGHT) or (self.rect.left > WIDTH) or (self.rect.right < 0):
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100,-40)
            self.speedy = random.randrange(2,10)
            self.speedx = random.randrange(-3,3)


# In[5]:


#bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img #image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect() #get position of image
        self.rect.centerx = x #x,y is x,y of the spaceship
        self.rect.bottom = y
        self.speedy = -10 #bullet move upward
        
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0: #if bullet go out of screen, delete it
            self.kill()


# In[6]:


#explosion class
class Explode(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explode_animation[self.size][0] #image
        self.rect = self.image.get_rect() #get position of image
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explode_animation[self.size]):
                self.kill()
            else:
                self.image = explode_animation[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center


# In[7]:


#power class
class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield','gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect() #get position of image
        self.rect.center = center
        self.speedy = 3
        
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT: #if power go out of screen, delete it
            self.kill()


# In[8]:


# create new rock 
def create_new_rock():
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)
    
#display text
def display_text(surface, text, size, x, y):
    font = pygame.font.Font(font_name,size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surface.blit(text_surface, text_rect)
    
#visualise health
def display_hp(surface, hp, x,y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x,y, BAR_LENGTH,BAR_HEIGHT)
    fill_rect = pygame.Rect(x,y, fill,BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)
    
#visualise chances left
def display_chances(surface, chances, img, x,y):
    for i in range (chances):
        img_rect = img.get_rect()
        img_rect.x = x + i*30
        img_rect.y = y
        surface.blit(img, img_rect)
        
#main menu
def display_main_menu():
    screen.blit(background_img,(0,0))
    display_text(screen, "SPACE ESCAPE", 64, WIDTH/2, HEIGHT/4)
    display_text(screen, r"'Press A' and 'D' to move left and right, 'SPACE' key to shoot", 22, WIDTH/2, HEIGHT/2)
    display_text(screen, "Press any key to start the game!!", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    wait = True
    while wait:
        clock.tick(FPS)
        #get input from user
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #if user want to quit
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP: #wait until u release the key
                wait = False
                return False


# In[10]:


#play background music
pygame.mixer.music.play(-1)


# In[11]:


#main loop
main_menu = True
running = True
while running:
    if main_menu:
        terminate = display_main_menu()
        if terminate:
            break
        main_menu = False
        # combine all sprite
        all_sprites = pygame.sprite.Group()
        #rocks and bullets group is to check whether they hit each other
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()

        #player
        player = Player()
        all_sprites.add(player)

        #rock
        for i in range(8):
            create_new_rock()

        #score
        score = 0
    
    #frame per second
    clock.tick(FPS) #run how many times in 1 sec (to standardize every computer)
    #get input from user
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #if user want to quit
            running = False
        elif event.type == pygame.KEYDOWN: #if user want to shoot
            if event.key == pygame.K_SPACE:
                player.shoot()
    
    #update game
    all_sprites.update()
    
    #CASE1: bullet hit rock
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True) #if collide, delete both
    for hit in hits: #if deleted rocks, nid to ganti back
        random.choice(explode_sounds).play()
        score += hit.radius
        explode = Explode(hit.rect.center, 'large')
        all_sprites.add(explode)
        if random.random() > 0.92:
            power = Power(hit.rect.center)
            all_sprites.add(power)
            powers.add(power)
        create_new_rock()
    
    #CASE2: rock hit spaceship
    #use circle as collision determination
    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
    for hit in hits:
        create_new_rock()
        player.health -= hit.radius
        explode = Explode(hit.rect.center, 'small')
        all_sprites.add(explode)
        if player.health <= 0:
            die = Explode(player.rect.center, 'player')
            all_sprites.add(die)
            player_die.play()
            player.chances -= 1 
            player.health = 100
            player.hide_player()
            
    #CASE3: spaceship powerup
    hits = pygame.sprite.spritecollide(player, powers, True, pygame.sprite.collide_circle)
    for hit in hits:
        if hit.type == 'shield':
            shield_sound.play()
            player.health +=8
            if player.health > 100:
                player.health = 100
        elif hit.type == 'gun':
            gun_sound.play()
            player.gunup()

    #ENDGAME
    if player.chances == 0 and not(die.alive()):
#         running = False
        main_menu = True #move user to main menu instead of straight end game
    
    #display
    screen.fill(BLACK)
    screen.blit(background_img,(0,0))
    all_sprites.draw(screen)
    display_text(screen, str(score), 18, WIDTH/2, 10)
    display_hp(screen, player.health,5,15)
    display_chances(screen, player.chances, player_img_mini, WIDTH-100, 15)
    pygame.display.update()
    
pygame.quit()


# In[ ]:




