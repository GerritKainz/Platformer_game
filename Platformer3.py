import json, copy, keyboard, pygame, sys
from pickle import FRAME
from PIL import Image
from time import sleep, time
from pygame.locals import *
from collision_colors import *
pygame.init()
pygame.mixer.init()

#open game_data.json file
with open('game_data.json', 'r') as f:
    data = json.load(f)

#clock DONE
clock = pygame.time.Clock()

#fps DONE
FRAMERATE = data["data"]["framerate"]
show_fps  = data["data"]["showfps"]
dt = 0 #delta time between frames
fps = 0

#sounds DONE
death_sound = pygame.mixer.Sound('sounds/smashsound.mp3')
error_sound = pygame.mixer.Sound('sounds/error.mp3')
kaching_sound = pygame.mixer.Sound('sounds/ka-ching.mp3')
background_music_start = pygame.mixer.Sound('sounds/Music2.mp3')
background_music_level = pygame.mixer.Sound('sounds/Music1.mp3')
level_complete_sound = pygame.mixer.Sound('sounds/level_complete_sound.mp3')
volume_effects = data["data"]["volume_effects"]
volume_music = data["data"]["volume_music"]
death_sound.set_volume(volume_effects)
error_sound.set_volume(volume_effects)
kaching_sound.set_volume(volume_effects)
level_complete_sound.set_volume(volume_effects)
background_music_start.set_volume(volume_music)
background_music_level.set_volume(volume_music)

#start background music DONE
background_music_start.play(-1)

#screen
if data["automatic_resolution"] == "True": size = width, height = pygame.display.get_desktop_sizes()[0] 
else: size = width, height = data["screen_resolution"]
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Platformer')
pygame.display.set_icon(pygame.image.load('pictures/players/0/jump.png'))
current_screen = "start" #what screen is displayed, can be "start", "level", "settings", "pause", "dead", "finish"

#fonts DONE
font_gameover = pygame.font.SysFont(None, int(90 * width / 1536))
font_menu     = pygame.font.SysFont(None, int(70 * width / 1536))
font_value    = pygame.font.SysFont(None, int(50 * width / 1536))
font_small    = pygame.font.SysFont(None, int(40 * width / 1536))

#keys DONE
key_moveleft = data["data"]["left_key"]
key_moveright = data["data"]["right_key"]
key_jump = data["data"]["jump_key"]
key_duck = data["data"]["duck_key"]

#levels DONE
levels = [] #pictures of the levels
levels_small = [] #pictures of the small levels
levels_size = [] #sizes of the scaled levels
true_levels_size = [] #list of the real size of the levels
level_positions = [] #rects of the small rects

for i in range(8): #max of 4 levels
    try:
        image = pygame.image.load(f'pictures/levels/{i}.png').convert_alpha()
        true_levels_size.append([image.get_width(), image.get_height()]) #add size of level to list
        #image = pygame.transform.scale(image, (int(width / 1536 * true_levels_size[i][0]), int(height / 864 * true_levels_size[i][1])))
        image = pygame.transform.rotozoom(image, 0, width / 1536) #scales the level according to the resolution
        levels.append(image) #add level picture to list
        levels_small.append(pygame.transform.scale(levels[i], (width / 5, width / 10))) #make small level and add it to list
        levels_size.append([levels[i].get_width(), levels[i].get_height()]) #add size of level to list
        if i < 4: level_positions.append(levels_small[i].get_rect(topleft = (width / 20 + i * width / 4.5, height / 4)))
        else: level_positions.append(levels_small[i].get_rect(topleft = (width / 20 + (i-4) * width / 4.5, height / 2)))
    except: break #if file not found stop looking

level_pics = [] #all the level pictures for searching for coins
for i in range(len(levels)):
    pic = Image.open(f'pictures/levels/{i}.png')
    pic = pic.load()
    level_pics.append(pic)

#players DONE
players_jump_l      = []
players_dead_l      = []
players_running_1   = []
players_running_2   = []
players_jump        = []
players_dead        = []
players_running_1_l = []
players_running_2_l = []
players_big         = [] #big players images
players_positions   = [] #big players rects

for i in range(9): #max 9 players
    try:
        img = pygame.image.load(f'pictures/players/{i}/jump.png').convert_alpha() #load jump player picture in currently checked player
        img = pygame.transform.rotozoom(img, 0, width / 1536)
        img.set_colorkey((255, 255, 255)) #make picture transparent
        players_jump.append(img) #add picture to list
        img = pygame.transform.flip(img, True, False) #make flipped picture
        img.set_colorkey((255, 255, 255)) #make picture transparent
        players_jump_l.append(img) #add picture to list

        img = pygame.image.load(f'pictures/players/{i}/dead.png').convert_alpha() #load dead player picture in currently checked player
        img = pygame.transform.rotozoom(img, 0, width / 1536)
        img.set_colorkey((255, 255, 255)) #make picture transparent
        players_dead.append(img) #add picture to list
        img = pygame.transform.flip(img, True, False) #make flipped picture
        img.set_colorkey((255, 255, 255)) #make picture transparent
        players_dead_l.append(img) #add picture to list

        img = pygame.image.load(f'pictures/players/{i}/running1.png').convert_alpha() 
        img = pygame.transform.rotozoom(img, 0, width / 1536)
        img.set_colorkey((255, 255, 255)) #make picture transparent
        players_running_1.append(img) #add picture to list
        img = pygame.transform.flip(img, True, False) #make flipped picture
        img.set_colorkey((255, 255, 255)) #make picture transparent
        players_running_1_l.append(img) #add picture to list

        img = pygame.image.load(f'pictures/players/{i}/running2.png').convert_alpha() 
        img = pygame.transform.rotozoom(img, 0, width / 1536)
        img.set_colorkey((255, 255, 255)) #make picture transparent
        players_running_2.append(img) #add picture to list
        img = pygame.transform.flip(img, True, False) #make flipped picture
        img.set_colorkey((255, 255, 255)) #make picture transparent
        players_running_2_l.append(img) #add picture to list

        img = pygame.image.load(f'pictures/players/{i}/big.png').convert_alpha()
        img = pygame.transform.scale(img, (width / 12, width / 12))
        players_big.append(img) #add picture to list

        players_positions.append(img.get_rect(topleft = (width / 20 + i * width / 10, height * 0.7)))

    except: break #if file not found stop looking

#menu assets DONE
coin_big   = pygame.image.load('pictures/menu/coin.png').convert_alpha() #60x60 px
coin_small = pygame.transform.rotozoom(coin_big, 0, 0.5 * width / 1536)
coin_big   = pygame.transform.rotozoom(coin_big, 0, width / 1536)
lock       = pygame.image.load('pictures/menu/lock.png').convert_alpha() 
lock       = pygame.transform.scale(lock, (players_big[0].get_width() * 0.5, players_big[0].get_height() * 0.7))
coin_big.set_colorkey((255, 255, 255))
coin_small.set_colorkey((255, 255, 255))
lock.set_colorkey((255, 255, 255))

#buttons DONE
pause_button            = pygame.image.load('pictures/menu/pause_button.png').convert_alpha() #50x49 px
pause_button            = pygame.transform.rotozoom(pause_button, 0, width / 1536)
pause_button_rect       = pause_button.get_rect(topleft = (width * 0.95, height * 0.01))
exit_button             = pygame.image.load('pictures/menu/exit_button.png').convert_alpha() #50x49 px
exit_button             = pygame.transform.rotozoom(exit_button, 0, width / 1536)
exit_button_rect        = exit_button.get_rect(topleft = (width * 0.95, height * 0.01))
start_arrow             = pygame.image.load('pictures/menu/play_level.png').convert_alpha() #75x62 px
start_arrow             = pygame.transform.rotozoom(start_arrow, 0, width / 1536)
start_arrow_rect        = start_arrow.get_rect(bottomright = (width  * 0.95, height * 0.95))
back_arrow              = pygame.transform.flip(start_arrow, True, False) #75x62 px
back_arrow              = pygame.transform.rotozoom(back_arrow, 0, width / 1536)
back_arrow_rect         = back_arrow.get_rect(topleft = (20, 20))
start_arrow.set_colorkey((255, 255, 255))
exit_button.set_colorkey((255, 255, 255))
pause_button.set_colorkey((255, 255, 255))
back_arrow.set_colorkey((255, 255, 255))

#texts and text rectangles DONE
play_text               = font_gameover.render('PLAY',            True, (0, 0, 0))
settings_text           = font_gameover.render('SETTINGS',        True, (0, 0, 0))
resume_text             = font_menu.render('RESUME',              True, (0, 0, 0))
restart_text            = font_menu.render('RESTART',             True, (0, 0, 0))
backtomenu_text         = font_menu.render('MENU',                True, (0, 0, 0))
quit_text               = font_menu.render('QUIT',                True, (0, 0, 0))
finished_text           = font_gameover.render('LEVEL COMPLETE!', True, (0, 0, 0))
loading_text            = font_gameover.render('Loading...',      True, (255, 255, 255))
teleport_text           = font_menu.render('NEXT LEVEL',          True, (0, 0, 0))
resume_text_rect        = resume_text.get_rect(    midtop = (width / 2, height * 0.3))
restart_text_rect       = restart_text.get_rect(   midtop = (width / 2, height * 0.4))
settings_text_rect      = settings_text.get_rect(  midtop = (width/2,   20))
backtomenu_text_rect    = backtomenu_text.get_rect(midtop = (width / 2, height * 0.5))
quit_text_rect          = quit_text.get_rect(      midtop = (width / 2, height * 0.6))
finished_text_rect      = finished_text.get_rect(  midtop = (width / 2, height * 0.05))
loading_text_rect       = loading_text.get_rect(   center = (width/2,   height/2))
teleport_text_rect      = teleport_text.get_rect(  midtop = (width / 2, height* 0.3))
play_text_rect          = play_text.get_rect(    topright = start_arrow_rect.topleft)
play_rect               = pygame.Rect.union(play_text_rect, start_arrow_rect)

#settings texts and rectangles DONE
jump_key_text           = font_menu.render(str('Jump Key: ' + str(key_jump)),      True, (0, 0, 0))
left_key_text           = font_menu.render(str('Left Key: ' + str(key_moveleft)),  True, (0, 0, 0))
right_key_text          = font_menu.render(str('Right Key: '+ str(key_moveright)), True, (0, 0, 0))
duck_key_text           = font_menu.render(str('Duck Key: ' + str(key_duck)),      True, (0, 0, 0))
jump_key_text_rect      = jump_key_text.get_rect(topleft = (width / 15, 0.6 * height / 5))
left_key_text_rect      = left_key_text.get_rect(topleft = (width / 15, 1.2 * height / 5))
right_key_text_rect     = right_key_text.get_rect(topleft= (width / 15, 1.8 * height / 5))
duck_key_text_rect      = duck_key_text.get_rect(topleft = (width / 15, 2.4 * height / 5))

volume_effects_base     = pygame.rect.Rect((width / 15, 3.6 * height / 5), (width / 8, height / 80))
volume_music_base       = pygame.rect.Rect((width / 15, 4.2 * height / 5), (width / 8, height / 80))
volume_effects_button   = pygame.rect.Rect((width / 15 + volume_effects * width / 8, 3.6 * height / 5 - height / 40 + height / 160), (height / 20, height / 20))
volume_music_button     = pygame.rect.Rect((width / 15 + volume_music *   width / 8, 4.2 * height / 5 - height / 40 + height / 160), (height / 20, height / 20))
volume_effects_text     = font_menu.render(str('Volume Effects: '+ str(volume_effects)), True, (0, 0, 0))
volume_music_text       = font_menu.render(str('Volume Music: '  + str(volume_music)),   True, (0, 0, 0))
volume_effects_text_rect= volume_effects_text.get_rect(midleft = (volume_effects_base.right + width / 20, volume_effects_base.top))
volume_music_text_rect  = volume_music_text.get_rect(   midleft = (volume_music_base.right  + width / 20,   volume_music_base.top))

cancel_text             = font_menu.render('CANCEL', True, (0, 0, 0))
ok_text                 = font_menu.render('OK', True, (0, 0, 0))
buy_text                = font_menu.render('BUY', True, (0, 0, 0))
reset_data_text         = font_menu.render('RESET DATA', True, (0, 0, 0))
cancel_text_rect        = cancel_text.get_rect(    bottomleft  = (width/2 - width / 8, height/2 + width / 15))
ok_text_rect            = ok_text.get_rect(        bottomright = (width/2 + width / 8,       height/2 + width / 15))
buy_text_rect           = buy_text.get_rect(       bottomright = (width/2 + width / 8, height/2 + width / 15))
reset_data_rect         = reset_data_text.get_rect(bottomleft  = (width / 15,          height * 0.95))
if show_fps == "True":    show_fps_text = font_menu.render(f'Show PFS: ON', True, (0, 0, 0))
else: show_fps_text     = font_menu.render(f'Show PFS: OFF', True, (0, 0, 0))
show_fps_text_rect      = show_fps_text.get_rect(topleft = (width / 15, 3.0 * height / 5))

#variables DONE
current_level = data["data"]["current_level"] #index of the level currently played
level_played = None #name of the level currently played
xplayer = 200 * width / 1536 #start x position of the player
yplayer = height - (170 * height / 864) # ... y position ...
xspeed = 0 #start x speed of the player
last_xspeed = 0 #saves the last movement direction (used for displaying the correct orientation of the player when standing)
yspeed = 0 # ... y speed ...  
gravity = 0.22 * width / 1536 #acceleration in y direction 
dead = False
jump = True
collision_ground = False
collision_right = False
collision_left = False
collision_top = False
mouse_pos = (0, 0)
level_clicked  = 0 #which one of the levels is highlighted, first one by default
player_clicked = data["data"]["current_player"] #which one of the players is highlighted, first one by default
current_player = 0

#lists DONE
player_size    = [players_jump[0].get_width(), players_jump[0].get_height()] #size of the player picture (x, y)
xlevel         = 0 #how far left / right the level is displayed (for scrolling the level in x direction)
ylevel         = height - levels_size[current_level][1] #how far up / down the level is displayed (for scrolling in y direction)
last_level_pos = [xlevel, ylevel]
level_values   = data["level_values"] #how many coins each level costs (level 0 is already unlocked, so 0 coins)
player_values  = data["player_values"] #how many coins each player costs (player 0 is already unlocked, so 0 coins)

#collision DONE
player_rect = players_jump[current_player].get_rect(topleft = (xplayer, yplayer))

#coins DONE
coins = data["data"]["coins"] #number of coins you have

levels_coins_rects = []
levels_coins_rects_copy = []
for i in range(len(levels)):
    levels_coins_rects.append([]) #rectangles of the coins in the levels
    levels_coins_rects_copy.append([]) #backup list for resetting

#write 'loading' on the screen DONE
loading_bar_rect = pygame.Rect(0, 0, 200, 20)
loading_bar_rect.center = (width/2, height* 3 / 4)
screen.blit(loading_text, loading_text_rect)
pygame.draw.rect(screen, (255, 255, 255), loading_bar_rect, 1)
pygame.display.update()


#functions ---------------------------------------------------------------------------------------------------------------------------

def search_coins():
    i = 0
    frame = 0
    total_frames = 0
    for i in range(len(level_pics)):
        total_frames += true_levels_size[i][0] * true_levels_size[i][1] #calculates how many total pixels have to be checked for coins
    #print( '\n' + str(total_frames) + ' Pixels have to be ckecked')
    for level in range(len(level_pics)):
        for x in range(true_levels_size[level][0]):
            for y in range(true_levels_size[level][1]):
                if level_pics[level][x, y][:3] == coin_color:
                    var_name = str("coin_rect_" + str(i))
                    i += 1
                    my_vars = vars()
                    my_vars[var_name] = coin_small.get_rect(center = (x * width / 1536, y *width / 1536))
                    levels_coins_rects[level].append(my_vars[var_name])
                    levels_coins_rects_copy[level].append(my_vars[var_name])

                if frame % 10000 == 0: #only every so many frames for better performance
                    pygame.draw.rect(screen, (255, 255, 255), (loading_bar_rect.left, loading_bar_rect.top, 200 * frame / total_frames, 20))
                    pygame.display.update(loading_bar_rect)

                frame += 1
                y += 1
            x += 1

            if keyboard.is_pressed('esc'):
                sys.exit()
        level += 1

def move_player(): 
    global xspeed, last_xspeed, yspeed, jump, xplayer, yplayer, collision_ground, collision_left, collision_right, collision_top

    if not jump:
        gravity = 0
        yspeed = 0
    else: gravity = 0.22 * width / 1536
    
    if keyboard.is_pressed(key_moveleft):
        if xplayer > 7 and collision_left == False:
            xspeed = -3 * width / 1536
    elif keyboard.is_pressed(key_moveright):
        if xplayer < width - player_size[0] - 7 and collision_right == False:
            xspeed = 3 * width / 1536
    else: xspeed = 0
    if keyboard.is_pressed(key_jump):
        if not jump: #you can only jump when on the ground
            jump = True
            yspeed = -9.9 * width / 1536
    if not jump and not collision_ground: #to fall down when running off an object
        jump = True
    if keyboard.is_pressed(key_duck):
        if jump:
            yspeed = 6 * width / 1536

    yspeed += gravity
    if yspeed > 12 * width / 1536: #limit yspeed
        yspeed = 12 * width / 1536
    # if yplayer < 5:
    #     yspeed = 0
    #     yplayer = 5
    yplayer += yspeed
    if xplayer < 5:
        xplayer = 5
        xspeed = 0
    elif xplayer > width - player_size[0] - 5:
        xplayer = width - player_size[0] - 5
        xspeed = 0
    else:
        xplayer += xspeed
    if xspeed != 0:
        last_xspeed = xspeed #saves the current movement direction (used for the correct player picture when not moving left / right)

def player_collision(): 
    global xspeed, yspeed, gravity, jump, collision_ground, collision_left, collision_right, collision_top, dead, current_screen, yplayer
    player_size[0] = player_rect.right - player_rect.left
    player_size[1] = player_rect.bottom - player_rect.top
    #top of player further away that limits yspeed 
    coll = False #makes the collision False when it's not colliding anymore
    posx = xplayer + 2
    posy = yplayer - 13
    while posx < xplayer + player_size[0] - 1: #for all the pixels 1 pixel below the player
        for i in range(len(collision_colors_ground)):
            try:
                if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_ground[i] and yspeed < - 3:
                    #will collide with the ceiling soon
                    yspeed = -5 #limits the vertical speed just before hitting the ceiling to make collision better
            except: pass
        posx += 1
    if coll != True:
        collision_top = False

    #top of player
    coll = False
    posx = xplayer + 2
    posy = yplayer - 1
    while posx < xplayer + player_size[0] - 2: #for all the pixels 1 pixel below the player
        for i in range(len(collision_colors_ground)): 
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_ground[i]:
                #collides with the top
                collision_top = True
                coll = True
                yspeed = 0
                yplayer += 0.1
        for i in range(len(collision_colors_death)): 
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_death[i]:
                dead = True
                death_sound.play()
        for i in range(len(collision_colors_finish)):
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_finish[i]:
                #hits the flag
                level_complete_sound.play()
                current_screen = "finish"
                return current_screen
        posx += 1
    if coll != True:
        collision_top = False

    #bottom of player further away that limits yspeed 
    coll = False #makes the collision False when it's not colliding anymore
    posx = xplayer + 2 
    posy = yplayer + player_size[1] + 7
    while posx < xplayer + player_size[0] - 2: #for all the pixels 1 pixel below the player
        for i in range(len(collision_colors_ground)):
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_ground[i] and yspeed > 3:
                #will collide with the ground soon
                yspeed = 3 #limits the vertical speed just befor hitting the ground to make collision better
        posx += 1
    if coll != True:
        collision_ground = False

    #bottom of player 
    coll = False #makes the collision False when it's not colliding anymore
    posx = xplayer + 2
    posy = yplayer + player_size[1] + 1
    while posx < xplayer + player_size[0] - 2: #for all the pixels 1 pixel below the player
        for i in range(len(collision_colors_ground)):
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_ground[i]:
                #collides with the ground
                collision_ground = True
                coll = True
                jump = False
        for i in range(len(collision_colors_death)):
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_death[i]:
                dead = True
                death_sound.play()
        for i in range(len(collision_colors_finish)):
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_finish[i]:
                #hits the flag
                level_complete_sound.play()
                current_screen = "finish"
                return current_screen
        posx += 1
    for i in range(len(collision_colors_ground)):
        if screen.get_at((int(posx), int(posy-1)))[:3] == collision_colors_ground[i]:
                yplayer -= 1 #experimental!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                jump = False
    if coll != True:
        collision_ground = False
    
    #right side of player 
    coll = False
    posx = xplayer + player_size[0] + 1
    posy = yplayer + 2
    while posy < yplayer + player_size[1] - 2: 
        for i in range(len(collision_colors_ground)): 
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_ground[i]:
                #collides with the right side of the player
                collision_right = True
                coll = True
                xspeed = 0
                return xspeed
        for i in range(len(collision_colors_death)): 
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_death[i]:
                dead = True
                death_sound.play()
        for i in range(len(collision_colors_finish)):
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_finish[i]:
                #hits the flag
                level_complete_sound.play()
                current_screen = "finish"
                return current_screen
        posy += 1
    if coll != True:
        collision_right = False
        
    #left side of player
    coll = False
    posx = xplayer - 1
    posy = yplayer + 2
    while posy < yplayer + player_size[1] - 2:
        for i in range(len(collision_colors_ground)): 
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_ground[i]:
                #collides with the left side of the player
                collision_left = True
                coll = True
                xspeed = 0
                return xspeed
        for i in range(len(collision_colors_death)): 
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_death[i]:
                dead = True
                death_sound.play()
        for i in range(len(collision_colors_finish)):
            if screen.get_at((int(posx), int(posy)))[:3] == collision_colors_finish[i]:
                #hits the flag
                level_complete_sound.play()
                current_screen = "finish"
                return current_screen
        posy += 1
    if coll != True:
        collision_left = False

def scroll(): 
    global xplayer, yplayer, xlevel, ylevel
    #scroll level left / right
    if xplayer > width * 0.4 and abs(xlevel) < levels_size[current_level][0] - width:  #to the right
        xlevel -= 3 * width / 1536
        xplayer -= 3 * width / 1536
    if xplayer < width * 0.6 and abs(xlevel) > 0: #to the left
        xlevel += 3 * width / 1536
        xplayer += 3 * width / 1536
        
    #scroll level up / down
    if yplayer < height * 0.4:# and ylevel < -5:
        ylevel += 5 * width / 1536
        yplayer += 5 * width / 1536
    if yplayer > height * 0.6 and ylevel > height - levels_size[current_level][1]: #3500 = width of background picture
        ylevel -= yspeed
        yplayer -= yspeed

def blit_player(): 
    global last_xspeed, xspeed, xplayer, yplayer, frame, jump, player_rect
    if last_xspeed >= 0: #when moving to right or not moving
        if jump or xspeed == 0:
            screen.blit(players_jump[current_player], (round(xplayer), round(yplayer)))
            player_rect = players_jump[current_player].get_rect(bottomleft = (xplayer, yplayer + player_size[1]))
        elif not dead and xspeed > 0 and frame % 16 < 8: #changes between the two walking pictures every so many frames
            screen.blit(players_running_2[current_player], (round(xplayer), round(yplayer)))
            player_rect = players_running_2[current_player].get_rect(bottomleft = (xplayer, yplayer + player_size[1]))
        else: 
            screen.blit(players_running_1[current_player], (round(xplayer), round(yplayer)))
            player_rect = players_running_1[current_player].get_rect(bottomleft = (xplayer, yplayer + player_size[1]))

    else: #when moving to the left
        if jump or xspeed == 0:
            screen.blit(players_jump_l[current_player], (round(xplayer), round(yplayer)))
            player_rect = players_jump_l[current_player].get_rect(bottomleft = (xplayer, yplayer + player_size[1]))

        elif not dead and xspeed < 0 and frame % 16 < 8:
            screen.blit(players_running_2_l[current_player], (round(xplayer), round(yplayer)))
            player_rect = players_running_2_l[current_player].get_rect(bottomleft = (xplayer, yplayer + player_size[1]))
        else: 
            screen.blit(players_running_1_l[current_player], (round(xplayer), round(yplayer)))
            player_rect = players_running_1_l[current_player].get_rect(bottomleft = (xplayer, yplayer + player_size[1]))

def blit_player_dead(): 
    global last_xspeed, xplayer, yplayer, current_screen
    if last_xspeed < 0:
        screen.blit(players_dead_l[current_player], (round(xplayer), round(yplayer)))
    else: 
        screen.blit(players_dead[current_player], (round(xplayer), round(yplayer)))
    gameover_text = font_gameover.render(str('GAME OVER!'), True, (0, 0, 0))
    gameover_text_rect = gameover_text.get_rect(midtop = (width/2, 50))
    screen.blit(gameover_text, gameover_text_rect)
    blit_coins_count()
    pygame.display.update()
    sleep(1)
    pygame.image.save(screen, "pictures/screenshot.png")
    current_screen = "dead"

def blit_dead_menu(): 
    global width, height
    screenshot = pygame.image.load('pictures/screenshot.png')
    screen.blit(screenshot, (0, 0))
    big_rect = restart_text_rect.unionall([backtomenu_text_rect, quit_text_rect])
    big_rect1 = big_rect.inflate(width / 20, width / 20)
    pygame.draw.rect(screen, (200, 200, 200), big_rect1)
    screen.blit(quit_text, quit_text_rect)
    screen.blit(backtomenu_text, backtomenu_text_rect)
    screen.blit(restart_text, (restart_text_rect))

def blit_finished_menu():
    global width, height

    screenshot = pygame.image.load('pictures/screenshot.png')
    screen.blit(screenshot, (0, 0))
    big_rect = teleport_text_rect.unionall([restart_text_rect, backtomenu_text_rect, quit_text_rect])
    big_rect1 = big_rect.inflate(width / 20, width / 20)
    pygame.draw.rect(screen, (200, 200, 200), big_rect1)
    screen.blit(teleport_text, teleport_text_rect)
    screen.blit(restart_text, restart_text_rect) 
    screen.blit(backtomenu_text, backtomenu_text_rect)
    screen.blit(quit_text, quit_text_rect)
    pygame.display.update()

def reset_level(): 
    global xplayer, yplayer, xspeed, last_xspeed, yspeed, gravity, dead, jump, xlevel, ylevel, levels_coins_rects

    xplayer = 200 * width / 1536 #start x position of the player
    yplayer = height - (170 * height / 864) 
    xspeed = 0
    last_xspeed = 0 
    yspeed = 0
    gravity = 0.4
    dead = False
    jump = True
    xlevel = 0 
    ylevel = height - levels_size[current_level][1]
    #reset coins
    levels_coins_rects = copy.deepcopy(levels_coins_rects_copy)

def dead_menu_click(): 
    global width, height, current_screen, running

    pygame.event.get()
    if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
        mouse_pos = pygame.mouse.get_pos()
    
        if restart_text_rect.collidepoint(mouse_pos):
            #clicks restart
            pygame.draw.rect(screen, (0, 255, 0), restart_text_rect, 5) #marks the selected rectangle green
            pygame.display.update()
            sleep(0.1)

            reset_level() 
            current_screen = "level"
            
        if backtomenu_text_rect.collidepoint(mouse_pos):
            #clicks menu
            pygame.draw.rect(screen, (0, 255, 0), backtomenu_text_rect, 3) #marks the selected rectangle green
            pygame.display.update()
            sleep(0.1)

            reset_level()
            current_screen = "start"
            pygame.mixer.stop()
            background_music_start.play(-1)

        if quit_text_rect.collidepoint(mouse_pos):
            #clicks quit
            pygame.draw.rect(screen, (0, 255, 0), quit_text_rect, 3) #marks the selected rectangle green
            pygame.display.update()
            sleep(0.1)
            save_data()
            running = False

def start_screen_blit(): 

    screen.fill((255, 255, 255))
    screen.blit(play_text, play_text_rect)
    screen.blit(start_arrow, start_arrow_rect)
    screen.blit(settings_text, settings_text_rect)
    screen.blit(exit_button, exit_button_rect)

def unlock_level():
    global coins, level_clicked, current_level

    #draw white rectangle in middle of the screen with text: Buy this level for + level value + coins?
    screen.blit(cancel_text, cancel_text_rect)
    screen.blit(buy_text, buy_text_rect)
    buy_level_text1 = font_small.render('Do you want to buy', True, (0, 0, 0))
    buy_level_text2 = font_small.render(str('this level for ') + str(level_values[level_clicked]) + (' coins?'), True, (0, 0, 0))
    buy_level_text_rect1 = buy_level_text1.get_rect(midtop = (width/2, height/2 - 100))
    buy_level_text_rect2 = buy_level_text2.get_rect(midtop = (width/2, height/2 - 50))
    screen.blit(buy_level_text1, buy_level_text_rect1)
    screen.blit(buy_level_text2, buy_level_text_rect2)
    all_rect = ok_text_rect.unionall([buy_level_text_rect1, buy_level_text_rect2, cancel_text_rect])
    pygame.draw.rect(screen, (0, 0, 0), all_rect, 5)
    pygame.display.update()

    while True:
        pygame.event.get()
        if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
            mouse_pos = pygame.mouse.get_pos()
            if cancel_text_rect.collidepoint(mouse_pos):
                #draw rect around cancel text to show it has been clicked
                pygame.draw.rect(screen, (0, 255, 0), cancel_text_rect, 3)
                pygame.display.update()
                sleep(0.1)
                break
            if buy_text_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (0, 255, 0), buy_text_rect, 3)
                pygame.display.update()
                sleep(0.1)
                if coins >= level_values[level_clicked]: #if you have enough money
                    coins -= level_values[level_clicked]
                    kaching_sound.play()
                    #unlock level
                    with open('game_data.json', 'w') as f:
                        data["levels_unlocked"][level_clicked] = "True"
                        json.dump(data, f, indent=1)
                    # mark bought level as currently selected level
                    current_level = level_clicked
                    break

                else: #you don't have enough coins
                    error_sound.play()
                    not_enough_coins_text1 = font_small.render(str("You don't have enough coins"), True, (0, 0, 0))
                    not_enough_coins_text2 = font_small.render(str("You need " + str(level_values[level_clicked] - coins) + (' more coins')), True, (0, 0, 0))
                    ok_text               = font_menu.render('OK', True, (0, 0, 0))
                    not_enough_coins_rect1 = not_enough_coins_text1.get_rect(midtop = (width/2, height/2 - 100))
                    not_enough_coins_rect2 = not_enough_coins_text2.get_rect(midtop = (width/2, height/2 - 50))
                    all_rect = ok_text_rect.unionall([not_enough_coins_rect1, not_enough_coins_rect2, cancel_text_rect])
                    pygame.draw.rect(screen, (255, 255, 255), all_rect)
                    pygame.draw.rect(screen, (0, 0, 0), all_rect, 5)
                    screen.blit(not_enough_coins_text1, not_enough_coins_rect1)
                    screen.blit(not_enough_coins_text2, not_enough_coins_rect2)
                    screen.blit(ok_text, ok_text_rect)
                    pygame.display.update()

                    while True:
                        pygame.event.get()
                        if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
                            mouse_pos = pygame.mouse.get_pos()
                            if ok_text_rect.collidepoint(mouse_pos): #clicks ok
                                #draw rect around cancel text to show it has been clicked
                                pygame.draw.rect(screen, (0, 255, 0), ok_text_rect, 3)
                                pygame.display.update()
                                sleep(0.1)
                                break
                break

def unlock_player():
    global coins, player_clicked, current_player

    #draw white rectangle in middle of the screen with text: Buy this level for + level value + coins?
    screen.blit(cancel_text, cancel_text_rect)
    screen.blit(buy_text, buy_text_rect)
    buy_player_text1 = font_small.render('Do you want to buy', True, (0, 0, 0))
    buy_player_text2 = font_small.render(str('this player for ') + str(player_values[player_clicked]) + (' coins?'), True, (0, 0, 0))
    buy_player_text_rect1 = buy_player_text1.get_rect(midtop = (width/2, height/2 - 100))
    buy_player_text_rect2 = buy_player_text2.get_rect(midtop = (width/2, height/2 - 50))
    screen.blit(buy_player_text1, buy_player_text_rect1)
    screen.blit(buy_player_text2, buy_player_text_rect2)
    all_rect = ok_text_rect.unionall([buy_player_text_rect1, buy_player_text_rect1, cancel_text_rect])
    pygame.draw.rect(screen, (0, 0, 0), all_rect, 5)
    pygame.display.update()

    while True:
        pygame.event.get()
        if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
            mouse_pos = pygame.mouse.get_pos()
            if cancel_text_rect.collidepoint(mouse_pos):
                #draw rect around cancel text to show it has been clicked
                pygame.draw.rect(screen, (0, 255, 0), cancel_text_rect, 3)
                pygame.display.update()
                sleep(0.1)
                break
            if buy_text_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (0, 255, 0), buy_text_rect, 3)
                pygame.display.update()
                sleep(0.1)
                if coins >= player_values[player_clicked]: #if you have enough money
                    coins -= player_values[player_clicked]
                    kaching_sound.play()
                    #unlock level
                    with open('game_data.json', 'w') as f:
                        data["players_unlocked"][player_clicked] = "True"
                        json.dump(data, f, indent=1)
                    # mark bought level as currently selected level
                    current_player = player_clicked
                    break

                else: #you don't have enough coins
                    error_sound.play()
                    not_enough_coins_text1 = font_small.render(str("You don't have enough coins"), True, (0, 0, 0))
                    not_enough_coins_text2 = font_small.render(str("You need " + str(player_values[player_clicked] - coins) + (' more coins')), True, (0, 0, 0))
                    ok_text               = font_menu.render('OK', True, (0, 0, 0))
                    not_enough_coins_rect1 = not_enough_coins_text1.get_rect(midtop = (width/2, height/2 - 100))
                    not_enough_coins_rect2 = not_enough_coins_text2.get_rect(midtop = (width/2, height/2 - 50))
                    all_rect = ok_text_rect.unionall([not_enough_coins_rect1, not_enough_coins_rect2, cancel_text_rect])
                    pygame.draw.rect(screen, (255, 255, 255), all_rect)
                    pygame.draw.rect(screen, (0, 0, 0),       all_rect, 3)
                    screen.blit(not_enough_coins_text1, not_enough_coins_rect1)
                    screen.blit(not_enough_coins_text2, not_enough_coins_rect2)
                    screen.blit(ok_text, ok_text_rect)
                    pygame.display.update()

                    while True:
                        pygame.event.get()
                        if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
                            mouse_pos = pygame.mouse.get_pos()
                            if ok_text_rect.collidepoint(mouse_pos): #clicks ok
                                #draw rect around cancel text to show it has been clicked
                                pygame.draw.rect(screen, (0, 255, 0), ok_text_rect, 3)
                                pygame.display.update()
                                sleep(0.1)
                                break
                break

def start_screen_click(): 
    global current_screen, current_level, level_played, current_player, mouse_pos, level_clicked, player_clicked
    
    pygame.event.get()
    if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
        mouse_pos = pygame.mouse.get_pos()

        #select level
        for i in range(len(level_positions)): #for all levels
            if level_positions[i].collidepoint(mouse_pos):
                #clicks the small image of the currently checked level  
                level_clicked = i
                if data["levels_unlocked"][i] == "False": #if level is locked
                    unlock_level()
                else: current_level = i #if level is unlocked, level is selected
            i += 1

        #select player
        for i in range(len(players_positions)): #for all players
            if players_positions[i].collidepoint(mouse_pos):
                #clicks the small image of the currently checked player
                player_clicked = i
                if data["players_unlocked"][i] == "False": #if player is locked
                    unlock_player()
                else: current_player = i #if player is unlocked, player is selected
            i += 1

        #click play
        if play_rect.collidepoint(mouse_pos):
            #"play" is clicked
            pygame.draw.rect(screen, (0, 255, 0), play_rect, 3) #mark 'play' rectangle
            level_played = levels[level_clicked]
            pygame.display.update()
            sleep(0.1)
            current_screen = "level"
            pygame.mixer.stop()
            background_music_level.play(-1)

         #click settings
        if settings_text_rect.collidepoint(mouse_pos):
            #"settings" is clicked
            pygame.draw.rect(screen, (0, 255, 0), settings_text_rect, 3) #mark 'settings' rectangle
            pygame.display.update()
            sleep(0.1)
            current_screen = "settings"    


    #draw level and rectangle around selected level
    for i in range(len(level_positions)):
        screen.blit(levels_small[i], level_positions[i]) #draws the small pictures of the levels on the start screen

        if data["levels_unlocked"][i] == "False":
            #blit lock
            lock_rect = lock.get_rect(center = level_positions[i].center) #locked_text.get_rect(center = level_positions[i])
            screen.blit(lock, lock_rect)

        if current_level == i: #draws a rectangle around the selected level
            pygame.draw.rect(screen, (0, 200, 10), level_positions[i], 3)
        else: 
            pygame.draw.rect(screen, (0, 0, 0), level_positions[i], 3)

        #draw text with the value of the level if it isn't unlocked
        if data["levels_unlocked"][i] == "False": 
            value_text = font_value.render(str(level_values[i]), True, (0, 0, 0))
            value_text_rect = value_text.get_rect(topleft = level_positions[i].bottomleft)
            coin_rect = coin_small.get_rect(midleft = value_text_rect.midright)
            screen.blit(value_text, value_text_rect)
            screen.blit(coin_small, coin_rect)

    #draw player and rectangle around selected player
    for i in range(len(players_positions)):
        screen.blit(players_big[i], players_positions[i]) #draws the small pictures of the levels on the start screen

        if data["players_unlocked"][i] == "False":
            #blit lock
            lock_rect = lock.get_rect(center = players_positions[i].center) #locked_text.get_rect(center = level_positions[i])
            screen.blit(lock, lock_rect)

        if current_player == i: #draws a rectangle around the selected level
            pygame.draw.rect(screen, (0, 200, 10), players_positions[i], 3)
        else: 
            pygame.draw.rect(screen, (0, 0, 0), players_positions[i], 3)

        #draw text with the value of the player if it isn't unlocked
        if data["players_unlocked"][i] == "False": 
            value_text = font_value.render(str(player_values[i]), True, (0, 0, 0))
            value_text_rect = value_text.get_rect(topleft = players_positions[i].bottomleft)
            coin_rect = coin_small.get_rect(midleft = value_text_rect.midright)
            screen.blit(value_text, value_text_rect)
            screen.blit(coin_small, coin_rect)

def pause_button_click(): 
    global current_screen

    pygame.event.get()
    if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
        mouse_pos = pygame.mouse.get_pos()
        if pause_button_rect.collidepoint(mouse_pos):
            #pause button is pressed
            pygame.image.save(screen, "pictures/screenshot.png")
            current_screen = "pause"

def blit_pause_menu(): 
    global width, height

    screenshot = pygame.image.load('pictures/screenshot.png')
    screen.blit(screenshot, (0, 0))
    big_rect = resume_text_rect.unionall([restart_text_rect, backtomenu_text_rect, quit_text_rect])
    pygame.draw.rect(screen, (200, 200, 200), big_rect)
    screen.blit(resume_text, resume_text_rect)
    screen.blit(restart_text, restart_text_rect) 
    screen.blit(backtomenu_text, backtomenu_text_rect)
    screen.blit(quit_text, quit_text_rect)
    blit_coins_count()

def pause_menu_click(): 
    global width, height, current_screen, running
    pygame.event.get()
    if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
        mouse_pos = pygame.mouse.get_pos()

        if resume_text_rect.collidepoint(mouse_pos): 
            #clicks resume
            pygame.draw.rect(screen, (0, 255, 0), resume_text_rect, 3) #marks the selected rectangle green
            pygame.display.update()
            sleep(0.1)
            current_screen = "level"

        if restart_text_rect.collidepoint(mouse_pos): 
            #clicks restart
            pygame.draw.rect(screen, (0, 255, 0), restart_text_rect, 3) #marks the selected rectangle green
            pygame.display.update()
            sleep(0.1)
            reset_level()
            current_screen = "level"

        if backtomenu_text_rect.collidepoint(mouse_pos):
            #clicks menu
            pygame.draw.rect(screen, (0, 255, 0), backtomenu_text_rect, 3) #marks the selected rectangle green
            pygame.display.update()
            sleep(0.1) 
            reset_level()
            current_screen = "start"
            pygame.mixer.stop()
            background_music_start.play(-1)

        if quit_text_rect.collidepoint(mouse_pos):
           #clicks quit
           pygame.draw.rect(screen, (0, 255, 0), quit_text_rect, 3) #marks the selected rectangle green
           pygame.display.update()
           sleep(0.1)  
           save_data()
           running = False

def exit_button_click(): 
    global current_screen, running

    pygame.event.get()
    if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
        mouse_pos = pygame.mouse.get_pos()
        if exit_button_rect.collidepoint(mouse_pos):
            #exit button is pressed
            pygame.draw.circle(screen, (255, 0, 0), exit_button_rect.center, exit_button_rect.width / 2, 4)
            pygame.display.update()
            sleep(0.1)
            save_data()
            running = False

def blit_player_finished(): 
    global current_screen

    screen.blit(finished_text, finished_text_rect)
    pygame.display.update()
    pygame.image.save(screen, "pictures/screenshot.png")

def click_finished_menu(): 
    global width, height, current_screen, running, jump, current_level

    pygame.event.get()
    if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
        mouse_pos = pygame.mouse.get_pos()

        if teleport_text_rect.collidepoint(mouse_pos):
            #clicks teleport
            pygame.draw.rect(screen, (0, 255, 0), teleport_text_rect, 3) #marks the selected rectangle green
            pygame.display.update()
            sleep(0.1)

            teleport()
            reset_level()
            jump = False
            current_screen = "level"
    
        if restart_text_rect.collidepoint(mouse_pos):
            #clicks restart
            pygame.draw.rect(screen, (0, 255, 0), restart_text_rect, 3) #marks the selected rectangle green
            pygame.display.update()
            sleep(0.1)

            reset_level() 
            current_screen = "level"
            
        if backtomenu_text_rect.collidepoint(mouse_pos):
            #clicks menu
            pygame.draw.rect(screen, (0, 255, 0), backtomenu_text_rect, 3) #marks the selected rectangle green
            pygame.display.update()
            sleep(0.1)

            reset_level()
            current_screen = "start"
            pygame.mixer.stop()
            background_music_start.play(-1)

        if quit_text_rect.collidepoint(mouse_pos):
            #clicks quit
            pygame.draw.rect(screen, (0, 255, 0), quit_text_rect, 3) #marks the selected rectangle green
            pygame.display.update()
            sleep(0.1)
            save_data()
            running = False

def blit_settings():
    global volume_music, volume_effects

    screen.fill((255, 255, 255))
    screen.blit(back_arrow, back_arrow_rect)
    screen.blit(jump_key_text, jump_key_text_rect)
    screen.blit(left_key_text, left_key_text_rect)
    screen.blit(right_key_text, right_key_text_rect)
    screen.blit(duck_key_text, duck_key_text_rect)
    pygame.draw.rect(screen, (0, 0, 0), volume_effects_base)   
    pygame.draw.rect(screen, (255, 0, 0), volume_effects_button)
    volume_effects_text = font_menu.render(str('Volume Effects: '+ str(round(volume_effects, 2))), True, (0, 0, 0))
    volume_effects_text_rect = volume_effects_text.get_rect(midleft = (volume_effects_base.right + width / 20, volume_effects_base.top))
    screen.blit(volume_effects_text, volume_effects_text_rect)
    pygame.draw.rect(screen, (0, 0, 0), volume_music_base)   
    pygame.draw.rect(screen, (255, 0, 0), volume_music_button)
    volume_music_text = font_menu.render(str('Volume Music: '+ str(round(volume_music, 2))), True, (0, 0, 0))
    volume_music_text_rect = volume_music_text.get_rect(midleft = (volume_music_base.right + width / 20, volume_music_base.top))
    screen.blit(volume_music_text, volume_music_text_rect)
    screen.blit(reset_data_text, reset_data_rect)
    screen.blit(exit_button, exit_button_rect)

    if show_fps == "True":    
        show_fps_text = font_menu.render(f'Show FPS: ON', True, (0, 0, 0))
    else: 
        show_fps_text = font_menu.render(f'Show PFS: OFF', True, (0, 0, 0))
    screen.blit(show_fps_text, show_fps_text_rect)

def change_key():
    global key_jump, key_moveleft, key_moveright, key_duck
    global jump_key_text, left_key_text, right_key_text, duck_key_text
    global jump_key_text_rect, left_key_text_rect, right_key_text_rect, duck_key_text_rect

    pygame.event.get()
    if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
        mouse_pos = pygame.mouse.get_pos()
        if jump_key_text_rect.collidepoint(mouse_pos):
            #jump key text is pressed
            pygame.draw.rect(screen, (0, 255, 0), jump_key_text_rect, 3)
            pygame.display.update()
            sleep(0.1)
            #wait for keyboard input and set jump key to the pressed key
            key_jump = str(keyboard.read_key())
        if left_key_text_rect.collidepoint(mouse_pos):
            #jump key text is pressed
            pygame.draw.rect(screen, (0, 255, 0), left_key_text_rect, 3)
            pygame.display.update()
            sleep(0.1)
            #wait for keyboard input and set jump key to the pressed key
            key_moveleft = str(keyboard.read_key())
        if right_key_text_rect.collidepoint(mouse_pos):
            #jump key text is pressed
            pygame.draw.rect(screen, (0, 255, 0), right_key_text_rect, 3)
            pygame.display.update()
            sleep(0.1)
            #wait for keyboard input and set jump key to the pressed key
            key_moveright = str(keyboard.read_key())
        if duck_key_text_rect.collidepoint(mouse_pos):
            #jump key text is pressed
            pygame.draw.rect(screen, (0, 255, 0), duck_key_text_rect, 3)
            pygame.display.update()
            sleep(0.1)
            #wait for keyboard input and set jump key to the pressed key
            key_duck = str(keyboard.read_key())

    jump_key_text           = font_menu.render(str('Jump Key: ' + str(key_jump)),      True, (0, 0, 0))
    left_key_text           = font_menu.render(str('Left Key: ' + str(key_moveleft)),  True, (0, 0, 0))
    right_key_text          = font_menu.render(str('Right Key: '+ str(key_moveright)), True, (0, 0, 0))
    duck_key_text           = font_menu.render(str('Duck Key: ' + str(key_duck)),      True, (0, 0, 0))
    jump_key_text_rect      = jump_key_text.get_rect(topleft = (width / 15, 0.6 * height / 5))
    left_key_text_rect      = left_key_text.get_rect(topleft = (width / 15, 1.2 * height / 5))
    right_key_text_rect     = right_key_text.get_rect(topleft= (width / 15, 1.8 * height / 5))
    duck_key_text_rect      = duck_key_text.get_rect(topleft = (width / 15, 2.4 * height / 5))

def click_reset_data():
    global reset_data_rect

    pygame.event.get()
    if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
        mouse_pos = pygame.mouse.get_pos()
        if reset_data_rect.collidepoint(mouse_pos):
            #reset data is pressed
            pygame.draw.rect(screen, (0, 255, 0), reset_data_rect, 3)
            pygame.display.update()
            sleep(0.1)

            screen.blit(cancel_text, cancel_text_rect)
            screen.blit(ok_text, ok_text_rect)
            reset_data_text1 = font_value.render('Do you want to', True, (255, 0, 0))
            reset_data_text2 = font_value.render(str('reset all game data? '), True, (255, 0, 0))
            reset_data_rect1 = reset_data_text1.get_rect(midtop = (width/2, height/2 - 100))
            reset_data_rect2 = reset_data_text2.get_rect(midtop = (width/2, height/2 - 50))
            screen.blit(reset_data_text1, reset_data_rect1)
            screen.blit(reset_data_text2, reset_data_rect2)
            all_rect = reset_data_rect1.unionall([reset_data_rect2, cancel_text_rect, ok_text_rect])
            pygame.draw.rect(screen, (0, 0, 0), all_rect, 3)
            pygame.display.update()

            while True:
                pygame.event.get()
                if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
                    mouse_pos = pygame.mouse.get_pos()
                    if cancel_text_rect.collidepoint(mouse_pos):
                        #draw rect around cancel text to show it has been clicked
                        pygame.draw.rect(screen, (0, 255, 0), cancel_text_rect, 3)
                        pygame.display.update()
                        sleep(0.1)
                        break
                    if ok_text_rect.collidepoint(mouse_pos):
                        pygame.draw.rect(screen, (0, 255, 0), ok_text_rect, 3)
                        pygame.display.update()
                        sleep(0.1)
                        reset_data()
                        break

def change_volume():
    global volume_effects, volume_music, volume_effects_button, volume_music_button

    pygame.event.get()
    if pygame.mouse.get_pressed()[0]:#if left mouse button is pressed
        mouse_pos = pygame.mouse.get_pos()
        if volume_effects_button.collidepoint(mouse_pos): #clicks the red button 
            while True:
                pygame.event.get()
                if pygame.mouse.get_pressed()[0]:#if left mouse button is still pressed
                    mouse_pos = pygame.mouse.get_pos()
                    volume_effects = (mouse_pos[0] - width / 15 - volume_effects_button.width / 2) / (width / 8)
                    if volume_effects > 1: volume_effects = 1
                    if volume_effects < 0: volume_effects = 0
                    volume_effects_button = pygame.rect.Rect((width / 15 + volume_effects * width / 8 - volume_effects_button.width / 2, 3.6 * height / 5 - height / 40 + height / 160), (height / 20, height / 20))
                    volume_effects_text = font_menu.render(str('Volume Effects: '+ str(round(volume_effects, 2))), True, (0, 0, 0))
                    volume_effects_text_rect = volume_effects_text.get_rect(midleft = (volume_effects_base.right + width / 20, 3.6 * height / 5))
                    blit_settings()
                    pygame.draw.rect(screen, (0, 0, 0), volume_effects_base) 
                    pygame.draw.rect(screen, (255, 0, 0), volume_effects_button)
                    screen.blit(volume_effects_text, volume_effects_text_rect)
                    pygame.display.update()
                    death_sound.set_volume(volume_effects)
                    error_sound.set_volume(volume_effects)
                    kaching_sound.set_volume(volume_effects)
                    level_complete_sound.set_volume(volume_effects)
                else: break #stop loop

        if volume_music_button.collidepoint(mouse_pos): #clicks the red button 
            while True:
                pygame.event.get()
                if pygame.mouse.get_pressed()[0]:#if left mouse button is still pressed
                    mouse_pos = pygame.mouse.get_pos()
                    volume_music = (mouse_pos[0] - width / 15 - volume_music_button.width / 2) / (width / 8)
                    if volume_music > 1: volume_music = 1
                    if volume_music < 0: volume_music = 0
                    volume_music_button = pygame.rect.Rect((width / 15 + volume_music * width / 8 - volume_music_button.width / 2, 4.2 * height / 5 - height / 40 + height / 160), (height / 20, height / 20))
                    volume_music_text = font_menu.render(str('Volume Music: '+ str(round(volume_music, 2))), True, (0, 0, 0))
                    volume_music_text_rect = volume_music_text.get_rect(midleft = (volume_music_base.right + width / 20, 4.2 * height / 5))
                    blit_settings()
                    pygame.draw.rect(screen, (0, 0, 0), volume_music_base) 
                    pygame.draw.rect(screen, (255, 0, 0), volume_music_button)
                    screen.blit(volume_music_text, volume_music_text_rect)
                    pygame.display.update()
                    background_music_start.set_volume(volume_music)
                    background_music_level.set_volume(volume_music)
                else: break #stop loop

def click_fps():
    global show_fps

    pygame.event.get()
    if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
        mouse_pos = pygame.mouse.get_pos()
        if show_fps_text_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (0, 255, 0), show_fps_text_rect, 3)
            pygame.display.update()
            sleep(0.1)
            if show_fps == "True":
                show_fps = "False"
                with open('game_data.json', 'w') as f:
                    data["data"]["showfps"] == "False"
                    json.dump(data, f)
            else:
                show_fps = "True"
                with open('game_data.json', 'w') as f:
                    data["data"]["showfps"] == "True"
                    json.dump(data, f)

def back_button_click():
    global current_screen

    pygame.event.get()
    if pygame.mouse.get_pressed()[0]: #if left mouse button is pressed
        mouse_pos = pygame.mouse.get_pos()
        if back_arrow_rect.collidepoint(mouse_pos):
            #back arrow is pressed
            pygame.draw.rect(screen, (0, 255, 0), back_arrow_rect, 3)
            pygame.display.update()
            sleep(0.1)
            current_screen = "start"

def save_data():
    global key_jump, key_moveleft, key_moveright, key_duck, volume_effects, volume_music, current_level, current_player

    with open('game_data.json', 'w') as f:
        data["data"]["showfps"] = show_fps
        data["data"]["jump_key"] = key_jump
        data["data"]["left_key"] = key_moveleft
        data["data"]["right_key"] = key_moveright
        data["data"]["duck_key"] = key_duck
        data["data"]["volume_effects"] = round(volume_effects, 2)
        data["data"]["volume_music"] = round(volume_music, 2)
        data["data"]["current_level"] = 0
        data["data"]["current_player"] = 0
        data["data"]["coins"] = coins
        json.dump(data, f, indent=1)

def reset_data():
    global coins, current_level, current_player

    with open('game_data.json', 'w') as f:
        data["data"]["jump_key"] = "w"
        data["data"]["left_key"] = "a"
        data["data"]["right_key"] = "d"
        data["data"]["duck_key"] = "s"
        data["data"]["volume_effects"] = 0.1
        data["data"]["volume_music"] = 0.2
        data["data"]["current_level"] = 0
        data["data"]["current_player"] = 0
        data["data"]["coins"] = 0
        i = 1
        while i < len(data["levels_unlocked"]):
            data["levels_unlocked"][i] = "False"
            i += 1
        i = 1
        while i < len(data["players_unlocked"]):
            data["players_unlocked"][i] = "False"
            i += 1
        json.dump(data, f)
        coins = 0
        current_level = 0
        current_player = 0

def blit_and_collide_coins():
    global current_level, levels_coins_rects, xlevel, ylevel, last_level_pos, coins

    #get new coin rect based on level position
    level_move = [0, 0]
    level_move[0] = (last_level_pos[0] + xlevel) * 0.5 #how much the level moved in x direction compared to the previus frame 
    level_move[1] = (last_level_pos[1] + ylevel) * 0.5 #same for y direction
    i = 0
    while i < (len(levels_coins_rects[current_level])): #for all coin rects
        new_coin_rect = levels_coins_rects[current_level][i].move(level_move[0], level_move[1]) #move the coin by the amount the level background moved
        screen.blit(coin_small, new_coin_rect)
        if player_rect.colliderect(new_coin_rect): #if player collides with currently checked coin
            #collects a coin
            coins += 1 #you have one more coin
            del levels_coins_rects[current_level][i] #removes the coin from the list of coins
            i -= 1 #fixes the coin disappearing for one frame bug
        i += 1

    last_level_pos = (xlevel, ylevel) #sets the old pos to the current pos
  
def blit_coins_count():
    global coins

    coin_rect = coin_big.get_rect(topleft = (width * 0.01, 0.01))
    coin_count_text = font_menu.render(f'{coins}', True, (0, 0, 0))
    screen.blit(coin_big, coin_rect)
    screen.blit(coin_count_text, (width * 0.06, height * 0.01))

def blit_fps():
    global show_fps, fps

    if show_fps == "True":
        fps_text = font_small.render(f'FPS: {fps}', True, (0, 0, 0))
        fps_text_rect = fps_text.get_rect(bottomleft = (width * 0.01, height * 0.99))
        screen.blit(fps_text, fps_text_rect)

def teleport():
    global xlevel, ylevel, levels_size, size, current_level

    angle = 0
    scale = 1
    i = 0
    while i < 100:
        screen.fill((0, 0, 0))
        new_background = pygame.transform.rotozoom(levels[current_level], angle, scale)
        new_background_rect = new_background.get_rect(center = (xlevel + levels_size[current_level][0]/2 + -5 * i, ylevel + levels_size[current_level][1]/2))
        screen.blit(new_background, new_background_rect)
        pygame.display.update()
        scale /= 1.04
        i += 1
        clock.tick(FRAMERATE)

    newlevel = False
    j = current_level
    while j < len(levels):
        try:
            if data["levels_unlocked"][j + 1] == "True": #if next level is unlocked
                current_level = j + 1
                newlevel = True
                break
        except: 
            current_level = 0
            break
        j += 1
    if newlevel == False: current_level = 0
        
    #angle = 0
    xlevel = 0 
    ylevel = height - levels_size[current_level][1]
    i = 0
    while i < 100:
        screen.fill((0, 0, 0))
        new_background = pygame.transform.rotozoom(levels[current_level], angle, scale)
        new_background_rect = new_background.get_rect(center = (xlevel + levels_size[current_level][0]/2 - 2 * i + 2 * 150, ylevel + levels_size[current_level][1]/2))
        screen.blit(new_background, new_background_rect)
        pygame.display.update()
        scale *= 1.04
        i += 1
        clock.tick(FRAMERATE)

#main loop ------------------------------------------------------------------------------------------------------------------------

search_coins()

running = True 
frame = 0 #counts the frames, used for displaying the correct player picture when running
last_time = time()
while running: #loop for the entire game, when running is False, program ends

    dt = time() - last_time
    last_time = time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if current_screen == "start": #all the stuff for the start screen 
        start_screen_blit()
        blit_coins_count()
        start_screen_click()
        exit_button_click()

    if current_screen == "level": #all the stuff for playing the level 
        screen.fill(background_colors[current_level])
        scroll()
        screen.blit(levels[current_level], (xlevel, ylevel)) #displays the level on the screen
        
        if not dead: #when player is alive
            blit_player()
            player_collision()
            move_player()
            blit_and_collide_coins()
            pause_button_click()
            blit_coins_count()

        else: #when player died
            blit_and_collide_coins()
            blit_player_dead()
            blit_coins_count()

        screen.blit(pause_button, pause_button_rect) #displays the pause button
            
    if current_screen == "settings": #all the stuff for the settings 
        blit_settings()
        back_button_click()
        change_key()
        change_volume()
        click_reset_data()
        click_fps()
        exit_button_click()

    if current_screen == "dead": #all the stuff for the dead screen 
        blit_dead_menu()
        dead_menu_click()

    if current_screen == "finish": #finished level
        blit_player_finished()
        blit_finished_menu()
        click_finished_menu()

    if current_screen == "pause": #all the stuff for the pause screen 
        blit_pause_menu()
        pause_menu_click()

    if keyboard.is_pressed('esc'):
        save_data()
        running = False #ends the program

    blit_fps()

    pygame.display.update() #updates the screen
    frame += 1 #keeps track fo the frame number, used for the "walking" with different pictures of the player
    clock.tick(FRAMERATE) #makes sure the game runs at no more than 60 fps
    try: 
        fps = round(1 / dt)
    except: pass
