#Maturitní zkouška z předmětu 'Aplikovaná informatika'
#Téma: Postřehová hra pro dotykové tabule
#Gymnázium Sokolov a KVC
#Lukáš Rada 8.A 2023/2024
#Vytvořeno v pythonu s knihovnou pygame

import random
import time
from random import randint

import pygame
import pygame_menu

#konstanty
DISP_SIZE = (1280,720) #velikost obrazovky
BG_COLOR = (75,75,75) #barva pozadí
GND_COLOR = (56, 25, 2) #barva hlíny
OVERLAY_GND_COLOR = (22, 145, 0) #barva trávy nad hlínou
FRAMERATE = 60 #snímková frekvence (FPS)
GROUND_Y = DISP_SIZE[1]-200 #podlaha, na které bude postava stát a skákat
JUMP_HEIGHT = 180  # výška skoku
GRAVITY = 1.6  # gravitace

score = 0

#funkce main; pokud bych jinde importoval main.py, 
#nespustí se mi hra znovu
def main():
      
      #základní setup hry
      pygame.init()
      pygame.font.init()
      disp = pygame.display.set_mode(DISP_SIZE)

      #načtení textur, příprava fontů
      virusImages = [pygame.image.load('assets/virus.png'),pygame.image.load('assets/virus2.png'),pygame.image.load('assets/virus3.png'),pygame.image.load('assets/virus4.png')]
      shieldLeftImage = pygame.image.load('assets/shieldleft.png')
      fakeVerticalImage =  pygame.image.load('assets/fakevertical.png')
      verticalSpikeImage =  pygame.image.load('assets/verticalspike.png')
      cubeImage = pygame.image.load('assets/cube.png')
      superchargedImage = pygame.image.load('assets/supercharged.png')
      shieldImage = pygame.image.load('assets/shield.png')
      chargeBtnImage = pygame.image.load('assets/chargebtn.png')
      shieldBtnImage = pygame.image.load('assets/shieldbtn.png')
      scoreFont = pygame.font.SysFont('Arial', 30)
      clouds = [pygame.image.load('assets/cloud1.png'),
                pygame.image.load('assets/cloud2.png'),
                pygame.image.load('assets/cloud3.png'),
                pygame.image.load('assets/cloud4.png')]

      theme = pygame_menu.Theme(background_color=(0,170,210,255),
            title_background_color=(0,0,0,0),
            title_font=pygame.font.Font('./assets/BaksoSapi.otf', 100),
            title_font_shadow=True,
            title_offset=(90,0),
            widget_alignment=pygame_menu.locals.ALIGN_CENTER,
            widget_font=pygame.font.SysFont('Comic Sans MS', 40)
            )

      

      def game():
            global score
            score = 0
            
            gameClock = pygame.time.Clock()

            #proměnné pro překážky
            obstacles = [] #seznam překážek
            clouds = []
            lastSpawnTime = time.time()
            spawnRate = 5
            for _ in range(4):
                  clouds.append(spawnCloud())
            #podlaha
            groundRect = pygame.Rect(0,DISP_SIZE[1]-160,DISP_SIZE[0],160)
            groundOverlay = pygame.Rect(0,DISP_SIZE[1]-160,DISP_SIZE[0],60)
            shieldBtnRect = pygame.Rect(DISP_SIZE[0]//2-160,DISP_SIZE[1]-140, 100,80)
            superChargeBtnRect = pygame.Rect(DISP_SIZE[0]//2+60,DISP_SIZE[1]-140, 100,80)

            shieldX, shieldY = -1000,-1000
            cubeX = DISP_SIZE[0]//2-32
            cubeY = GROUND_Y/1.5
            cubeHeight = 64

            cubeVelocity = 0
            jumping = True
            running = True
            held = False

            shielded = False
            shieldAble = True
            lastShieldTime = 0

            superCharge = 0
            charged = False
            lastChargedTime = 0
            chargesNeeded = 4

            #hlavní smyčka hry
            while running:
                  #skóre je jeden snímek hry
                  score+=1
                  currentTime = time.time()
                  dt = currentTime - lastSpawnTime #lastSpawnTime využívám pro spawnování obstacles
                  shieldX, shieldY = cubeX-16, cubeY-16 #štít má větší texturu než hráč, je potřeba jej odsadit o 16px neboť je o 32px větší
                  if lastShieldTime + 0.75 < currentTime: #štít trvá pouze 750ms, poté zmizí
                        shielded = False
                        shieldX, shieldY = -1000,-1000 #hitbox štítu přesunu mimo obrazovku, aby nefungoval, i když není viditelný
                  if lastChargedTime + 0.75 < currentTime:
                        charged = False
                  spawnRate = max(0.75,1.75-(score/1.5)) #výpočet lineárně zvyšujícího se spawnratu pro spawnování obstacles, aby hra byla progresivně těžší

                  if dt > spawnRate: #po uplynutí spawnrate času se spawne obstacle
                        lastSpawnTime = currentTime
                        spawnObstacle(obstacles, score)
                  
                  #pohyb překážek
                  updateObstacles(obstacles, score, cubeX, cubeY)

                  if len(clouds) < 20 and random.random() < 0.5:
                        clouds.append(spawnCloud())

                  #hra projde každý event při jedné herní smyčce
                  for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                              running = False
                        #kontrola stisknutí a držení levého tlačítka na myši
                        if event.type == pygame.MOUSEBUTTONDOWN and not shieldBtnRect.collidepoint(pygame.mouse.get_pos()):
                                          held = True
                        elif event.type == pygame.MOUSEBUTTONUP:
                                    #funkcionalita šítu
                                    if shieldBtnRect.collidepoint(pygame.mouse.get_pos()):
                                          if not shielded and shieldAble: #shielded kontroluje, zdali mám aktivní štít, shieldAble, zdali mám nabitý štít z kolize s padající překážkou
                                                lastShieldTime = currentTime
                                                shielded = True
                                                shieldAble = False
                                    elif superChargeBtnRect.collidepoint(pygame.mouse.get_pos()):
                                          if superCharge >= chargesNeeded:
                                                lastChargedTime = currentTime
                                                charged = True
                                                superCharge = 0
                                    held = False
                        #stisk shield tlačítka na klávesnici pro debug
                        elif pygame.key.get_pressed()[pygame.K_e]:
                              if not shielded and shieldAble:
                                                lastShieldTime = currentTime
                                                shielded = True
                                                shieldAble = False
                        elif pygame.key.get_pressed()[pygame.K_w]:
                              if superCharge >= chargesNeeded:
                                                lastChargedTime = currentTime
                                                charged = True
                                                superCharge = 0
                        elif pygame.key.get_pressed()[pygame.K_ESCAPE]:
                              mainMenu()
                  #pokud hráč není ve vzduchu a levé tlačítko je stisknuto/podrženo, postava vyskočí a sníží svou vertikální rychlost
                  if not jumping and cubeY == GROUND_Y and held:
                        jumping = True
                        cubeVelocity = -20
                  if jumping:
                        cubeHeight = int(64*0.8)
                        cubeY += cubeVelocity
                        cubeVelocity += GRAVITY
                        #pokud se postava dotýká země, postava se nenachází ve vzduchu a vertikální rychlost je vynulována
                        if cubeY >= GROUND_Y:
                              cubeY = GROUND_Y
                              jumping = False
                              cubeVelocity = 0
                  else:
                        cubeHeight = 64    
                  
                  
                  #zobrazení všech elementů na obrazovku
                  disp.fill('#00ccff') #pozadí
                  drawClouds(disp, clouds)
                  pygame.draw.rect(disp, GND_COLOR, groundRect) #hlína
                  pygame.draw.rect(disp, OVERLAY_GND_COLOR, groundOverlay) #tráva
                  
                  if not charged:
                        cube = disp.blit(pygame.transform.scale(cubeImage, (64, cubeHeight)), (cubeX,cubeY))
                         #hráčova postava
                  else: 
                        cube = disp.blit(pygame.transform.scale(superchargedImage, (64, cubeHeight)), (cubeX,cubeY))
                  if superCharge >= chargesNeeded:
                        disp.blit(chargeBtnImage, superChargeBtnRect)
                  if shielded: 
                        shieldBlit = disp.blit(pygame.transform.scale(shieldImage, (96,96)), (shieldX,shieldY)) #štít
                  else:
                        if shieldAble and not charged: #pokud je postava zaštítitelná, štít se přesune mimo obrazovku a tlačítko pro použití štítu se vyrenderuje
                              shieldBtn = disp.blit(shieldBtnImage, shieldBtnRect)
                              shieldBlit = disp.blit(pygame.transform.scale(shieldImage, (96,96)), (-10000,-10000))
                  #renderování překážek
                  for obstacle in obstacles:
                        #překážky se spawnují jedna za druhou, jsou ale dvojité překážky
                              for ob in obstacle:
                                    if ob['type'] == 'faketop':
                                          disp.blit(pygame.transform.scale(fakeVerticalImage, (64,64)), ob['rect'])
                                    elif ob['type'] == 'top':
                                          disp.blit(pygame.transform.scale(verticalSpikeImage, (64,64)), ob['rect'])
                                    elif ob['type'] == 'shieldleft':
                                          disp.blit(pygame.transform.scale(shieldLeftImage, (64,64)), ob['rect'])
                                    else: disp.blit(pygame.transform.scale(ob['img'], (64,64)), ob['rect'])

                  #render skóre
                  showsScore = scoreFont.render("Score: " + str(score), True, (255, 255, 255))
                  disp.blit(showsScore, (DISP_SIZE[0]/2, 50))
                  #kontrola kolize s překážkou a zaštítovatelnosti
                  shieldCheck = checkShield(shieldBlit, obstacles, shieldAble, shielded)
                  shielded = shieldCheck[2]
                  shieldAble = shieldCheck[0]
                  superCharge+=shieldCheck[1]
                  moveClouds(clouds)
                  drawClouds(disp, clouds)    
                  checkCollision(cube, obstacles, charged)
                  pygame.display.update()
                  gameClock.tick(FRAMERATE)
            pygame.quit()

      def saveScore():
            f = open('./assets/.sa', 'r')
            savedScore = f.read()
            if int(savedScore) < score:
                  f.close()
                  f = open('./assets/.sa', 'w')
                  f.seek(0)
                  f.write(str(score))
                  f.truncate()
            f.close()
            mainMenu()

      def resetScore():
            f = open('./assets/.sa', 'w')
            f.seek(0)
            f.write('0')
            f.truncate()
      #hlavní menu vytvořené pomocí knihovny pygame_menu
      def mainMenu():
            f = open('./assets/.sa', 'r')
            highScore = f.read()
            f.close()
            menu = pygame_menu.Menu('Just Jump', DISP_SIZE[0], DISP_SIZE[1], theme=theme)
            menu.add.label('High Score')
            menu.add.label(highScore)
            menu.add.button('Play', game)
            menu.add.button('Reset Score', resetScore)
            menu.add.button('Quit', pygame_menu.events.EXIT)
            menu.mainloop(disp)
      
      def deathMenu():
            menu = pygame_menu.Menu('Just Jump', DISP_SIZE[0], DISP_SIZE[1], theme=theme)
            menu.add.label(f'You died!')
            menu.add.label(f'Score: {score}')
            menu.add.button(f'Main Menu', saveScore)
            menu.mainloop(disp)

            


      #spawnování překážek
      def spawnObstacle(obstacles: list, score: int): #obstacles je dvoudimenzionální seznam objektů
            spawnPos = randint(0,4) #0 zeshora, 1, zleva, 2 zprava
            #počet překážek v z jedné strany
            spawnNum = 1
            virusSeed = randint(0,3)
            if score > 3000:
                  spawnNum = 2
            if spawnPos == 0:
                  obstRect = pygame.Rect(DISP_SIZE[0]//2-32, -50, 50, 50)
                  obstacles.append([{'rect': obstRect, 'speed': 10, 'type': 'top'}])
            elif spawnPos == 1:
                  
                  obstRect = pygame.Rect(-50, GROUND_Y, 50, 50)
                  obstacles.append([{'rect': obstRect, 'speed': 10, 'type': 'left', 'img': virusImages[virusSeed]}])
            elif spawnPos == 2:
                  if spawnNum != 2:
                        obstRect = pygame.Rect(DISP_SIZE[0]+50, GROUND_Y, 50, 50)

                        obstacles.append([{'rect': obstRect, 'speed': -10, 'type': 'right', 'img': virusImages[virusSeed]}])
                  else:
                        obstRect = pygame.Rect(DISP_SIZE[0]+50, GROUND_Y, 50, 50)
                        obstRect2 = pygame.Rect(DISP_SIZE[0]+100, GROUND_Y, 50, 50)
                        obstacles.append([{'rect': obstRect, 'speed': -10, 'type': 'right', 'img': virusImages[virusSeed]},{'rect': obstRect2, 'speed': -10, 'type': 'right', 'img': virusImages[virusSeed]}])
            elif spawnPos == 3:
                  obstRect = pygame.Rect(DISP_SIZE[0]//2-32, -50, 50, 50)
                  obstacles.append([{'rect': obstRect, 'speed': 15, 'type': 'faketop'}]) 
            elif spawnPos == 4:
                  obstRect = pygame.Rect(-50, GROUND_Y, 50, 50)
                  obstacles.append([{'rect': obstRect, 'speed': 15, 'type': 'shieldleft'}]) 

      #pohyb překážek
      def updateObstacles(obstacles, score, cubeX, cubeY):
            for obstacle in obstacles:
                  if obstacle[0]['type'] == 'left':
                        obstacle[0]['rect'].move_ip(obstacle[0]['speed']+score/750,0)
                  if obstacle[0]['type'] == 'shieldleft':
                        obstacle[0]['rect'].move_ip(obstacle[0]['speed']+score/750, 0)
                        obstacle[0]['rect'].top = cubeY
                  elif  obstacle[0]['type'] == 'right':
                        obstacle[0]['rect'].move_ip(obstacle[0]['speed']-score/750, 0)
                        if len(obstacle) == 2:
                              obstacle[1]['rect'].move_ip(obstacle[0]['speed']-score/750, 0)
                  elif obstacle[0]['type'] == 'top' or obstacle[0]['type'] == 'faketop':
                        obstacle[0]['rect'].move_ip(0, obstacle[0]['speed']+score/750)
                  if ((obstacle[0]['type'] == 'left' and  obstacle[0]['rect'].left > DISP_SIZE[0] )or (obstacle[0]['type'] == 'right' and obstacle[0]['rect'].left < 0) or (obstacle[0]['type']=='top' and obstacle[0]['rect'].top > DISP_SIZE[1])):
                        if len(obstacle) == 2:
                              if obstacle[1]['rect'].left < 0:
                                    obstacles.remove(obstacle)
                        else:
                                    obstacles.remove(obstacle)

      def checkCollision(player, obstacles, charged):
            for obstacle in obstacles:
                  if player.colliderect(obstacle[0]['rect']) and not charged and obstacle[0]['type'] != 'faketop':
                        deathMenu()
                  if len(obstacle) == 2:
                        if player.colliderect(obstacle[1]['rect']) and not charged:
                              deathMenu()

      def checkShield(shield, obstacles, shieldable, shielded):
            for obstacle in obstacles:
                  if (obstacle[0]['type'] == 'top' or obstacle[0]['type'] == 'shieldleft') and shield.colliderect(obstacle[0]['rect']) and shielded:
                        obstacles.remove(obstacle)
                        return (True,1, False)
                  elif obstacle[0]['type'] == 'faketop' and shield.colliderect(obstacle[0]['rect']) and shielded:
                        deathMenu()
            return (shieldable,0, shielded)
      
      def spawnCloud():
            cloud = random.choice(clouds)
            side = random.choice(['left', 'right'])
            if side == 'left':
                  cloudX = DISP_SIZE[0]+120
            else:
                  cloudX = -120

            cloudY = random.randint(50, DISP_SIZE[1] // 3) 

            cloudSpeed = random.randint(1, 3) * (-1 if side == 'left' else 1)

            return {'image': cloud, 'rect': cloud.get_rect(topleft=(cloudX, cloudY)), 'speed': cloudSpeed}
      
      def moveClouds(clouds):
            for cloud in clouds:
                  cloud['rect'].move_ip(cloud['speed'], 0)
                  if cloud['rect'].left < -120 and cloud['speed']<0:
                        clouds.remove(cloud)
                  elif cloud['rect'].left > DISP_SIZE[0]+120 and cloud['speed']>0:
                        clouds.remove(cloud)

      def drawClouds(surface, clouds):
            for cloud in clouds:
                  surface.blit(cloud['image'], cloud['rect'])

      mainMenu()

if __name__ == '__main__':
      main()