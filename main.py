#Maturitní zkouška z předmětu 'Aplikovaná informatika'
#Téma: Postřehová hra pro dotykové tabule
#Gymnázium Sokolov a KVC
#Lukáš Rada 8.A 2023/2024
#Vytvořeno v pythonu s knihovnou pygame

from random import randint
import time

import pygame
import pygame_menu

#konstanty
DISP_SIZE = (720,540) #velikost obrazovky
BG_COLOR = (75,75,75) #barva pozadí
GND_COLOR = (56, 25, 2) #barva hlíny
OVERLAY_GND_COLOR = (22, 145, 0) #barva trávy nad hlínou
FRAMERATE = 60 #snímková frekvence (FPS)
GROUND_Y = DISP_SIZE[1]-200 #podlaha, na které bude postava stát a skákat
JUMP_HEIGHT = 140  # výška skoku
GRAVITY = 1.75  # gravitace


#funkce main; pokud bych jinde importoval main.py, 
#nespustí se mi hra znovu
def main():
      #základní setup hry
      pygame.init()
      
      disp = pygame.display.set_mode(DISP_SIZE)

      #načtení textur, příprava fontů
      virusImage = pygame.image.load('assets/virus.png')
      skyImage = pygame.image.load('assets/sky.png')
      cubeImage = pygame.image.load('assets/cube.png')
      shieldImage = pygame.image.load('assets/shield.png')
      scoreFont = pygame.font.SysFont('Arial', 30)

      def game():
            
            pygame.font.init()
            gameClock = pygame.time.Clock()

            #proměnné pro překážky
            obstacles = [] #seznam překážek
            lastSpawnTime = time.time()
            spawnRate = 5
            score = 0
      

            
            groundRect = pygame.Rect(0,DISP_SIZE[1]-160,DISP_SIZE[0],160)
            groundOverlay = pygame.Rect(0,DISP_SIZE[1]-160,DISP_SIZE[0],60)
            shieldBtnRect = pygame.Rect(40,DISP_SIZE[1]-140, 100,80)
            shieldX, shieldY = -1000,-1000
            cubeX = DISP_SIZE[0]//3
            cubeY = GROUND_Y/1.5
            cubeVelocity = 0
            jumping = True
            running = True
            held = False
            shielded = False
            shieldAble = True
            lastShieldTime = 0
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
                  spawnRate = max(1,2-score/500) #výpočet lineárně zvyšujícího se spawnratu pro spawnování obstacles, aby hra byla progresivně těžší

                  if dt > spawnRate: #po uplynutí spawnrate času se spawne obstacle
                        lastSpawnTime = currentTime
                        spawnObstacle(obstacles, score)
                  
                  #pohyb překážek
                  updateObstacles(obstacles, score)

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
                                    held = False
                        #stisk shield tlačítka na klávesnici pro debug
                        elif pygame.key.get_pressed()[pygame.K_e]:
                              if not shielded and shieldAble:
                                                lastShieldTime = currentTime
                                                shielded = True
                                                shieldAble = False
                        elif pygame.key.get_pressed()[pygame.K_ESCAPE]:
                              mainMenu(score, death=False)
                  #pokud hráč není ve vzduchu a levé tlačítko je stisknuto/podrženo, postava vyskočí a sníží svou vertikální rychlost
                  if not jumping and cubeY == GROUND_Y and held:
                        jumping = True
                        cubeVelocity = -20
                  if jumping:
                        cubeY += cubeVelocity
                        cubeVelocity += GRAVITY
                        #pokud se postava dotýká země, postava se nenachází ve vzduchu a vertikální rychlost je vynulována
                        if cubeY >= GROUND_Y:
                              cubeY = GROUND_Y
                              jumping = False
                              cubeVelocity = 0    
                  
                  
                  #zobrazení všech elementů na obrazovku
                  sky = disp.blit(skyImage, (0,0)) #pozadí
                  pygame.draw.rect(disp, GND_COLOR, groundRect) #hlína
                  pygame.draw.rect(disp, OVERLAY_GND_COLOR, groundOverlay) #tráva

                  cube = disp.blit(cubeImage, (cubeX,cubeY)) #hráčova postava
                  if shielded: 
                        shieldBlit = disp.blit(pygame.transform.scale(shieldImage, (96,96)), (shieldX,shieldY)) #štít
                  else:
                        if shieldAble: #pokud je postava zaštítitelná, štít se přesune mimo obrazovku a tlačítko pro použití štítu se vyrenderuje
                              pygame.draw.rect(disp, (240,0,0), shieldBtnRect)
                              shieldBlit = disp.blit(pygame.transform.scale(shieldImage, (96,96)), (-10000,-10000))
                  #renderování překážek
                  for obstacle in obstacles:
                        #překážky se spawnují jedna za druhou, jsou ale dvojité překážky
                        if not (type(obstacle) is list):
                              disp.blit(pygame.transform.scale(virusImage, (64,64)), obstacle['rect'])
                        else:
                              for ob in obstacle:
                                    disp.blit(pygame.transform.scale(virusImage, (64,64)), ob['rect'])
                  #render skóre
                  showsScore = scoreFont.render("Score: " + str(score), True, (255, 255, 255))
                  disp.blit(showsScore, (DISP_SIZE[0]/2, 50))
                  #kontrola kolize s překážkou a zaštítovatelnosti
                  shieldAble = checkShield(shieldBlit, obstacles, shieldAble, shielded)
                  checkCollision(cube, obstacles, score)
                  pygame.display.update()
                  gameClock.tick(FRAMERATE)
            pygame.quit()
      #hlavní menu vytvořené pomocí knihovny pygame_menu
      def mainMenu(score=0, death=False):
            menu = pygame_menu.Menu('Just Jump', DISP_SIZE[0], DISP_SIZE[1], theme=pygame_menu.themes.THEME_BLUE)
            if death:
                  menu.add.label(f'You died!')
            menu.add.label(f'Score: {score}')
            menu.add.button('Play', game)
            menu.add.button('Quit', pygame_menu.events.EXIT)
            menu.mainloop(disp)

      #spawnování překážek
      def spawnObstacle(obstacles: list, score: int): #obstacles je dvoudimenzionální seznam objektů
            spawnPos = randint(0,2) #0 zeshora, 1, zleva, 2 zprava
            #počet překážek v z jedné strany
            spawnNum = 1
            if score > 3000:
                  spawnNum = 2
            if spawnPos == 0:
                  obstRect = pygame.Rect(720//3, -50, 50, 50)
                  obstacles.append([{'rect': obstRect, 'speed': 10, 'type': 'top'}])
            elif spawnPos == 1:
                  
                  obstRect = pygame.Rect(-100, 340, 50, 50)
                  obstacles.append([{'rect': obstRect, 'speed': 10, 'type': 'left'}])
            elif spawnPos == 2:
                  if spawnNum != 2:
                        obstRect = pygame.Rect(720, 340, 50, 50)

                        obstacles.append([{'rect': obstRect, 'speed': -10, 'type': 'right'}])
                  else:
                        obstRect = pygame.Rect(720, 340, 50, 50)
                        obstRect2 = pygame.Rect(770, 340, 50, 50)
                        obstacles.append([{'rect': obstRect, 'speed': -10, 'type': 'right'},{'rect': obstRect2, 'speed': -10, 'type': 'right'}])
      
      #pohyb překážek
      def updateObstacles(obstacles, score):
            for obstacle in obstacles:
                  if obstacle[0]['type'] == 'left':
                        obstacle[0]['rect'].move_ip(obstacle[0]['speed']+score/1000, 0)
                  elif  obstacle[0]['type'] == 'right':
                        obstacle[0]['rect'].move_ip(obstacle[0]['speed']-score/1000, 0)
                        if len(obstacle) == 2:
                              obstacle[1]['rect'].move_ip(obstacle[0]['speed']-score/1000, 0)
                        
                  elif obstacle[0]['type'] == 'top':
                        obstacle[0]['rect'].move_ip(0, obstacle[0]['speed']+score/1000)
                  if (obstacle[0]['type'] == 'left' and  obstacle[0]['rect'].left > DISP_SIZE[0] )or (obstacle[0]['type'] == 'right' and obstacle[0]['rect'].left < 0) or obstacle[0]['rect'].top > 540:
                        if len(obstacle) == 2:
                              if obstacle[1]['rect'].left < 0:
                                    obstacles.remove(obstacle)
                              else:
                                    obstacles.remove(obstacle)

      def checkCollision(player, obstacles, score):
            for obstacle in obstacles:
                  if player.colliderect(obstacle[0]['rect']):
                        mainMenu(score, death=True)
                  if len(obstacle) == 2:
                        if player.colliderect(obstacle[1]['rect']):
                              mainMenu(score, death=True)

      def checkShield(shield, obstacles, shieldable, shielded):
            for obstacle in obstacles:
                  if obstacle[0]['type'] == 'top' and shield.colliderect(obstacle[0]['rect']) and shielded:
                        obstacles.remove(obstacle)
                        
                        return True
            return shieldable

      mainMenu()




if __name__ == '__main__':
      main()