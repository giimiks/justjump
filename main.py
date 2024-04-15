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
      virusImage = pygame.image.load('assets/virus.png')
      skyImage = pygame.image.load('assets/sky.png')
      cubeImage = pygame.image.load('assets/cube.png')
      shieldImage = pygame.image.load('assets/shield.png')
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
            lastShieldTime = 0
            #hlavní smyčka hry
            while running:
                  score+=1
                  currentTime = time.time()
                  dt = currentTime - lastSpawnTime
                  if lastShieldTime + 0.75 < currentTime:
                        shielded = False
                  spawnRate = max(1,2-score/500)

                  if dt > spawnRate:
                        lastSpawnTime = currentTime
                        spawnObstacle(obstacles)
                  
                  updateObstacles(obstacles)

                 

                  #hra projde každý event při jedné herní smyčce
                  for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                              running = False
                        #kontrola stisknutí a držení levého tlačítka na myši
                        if event.type == pygame.MOUSEBUTTONDOWN and not shieldBtnRect.collidepoint(pygame.mouse.get_pos()):
                                          held = True
                        elif event.type == pygame.MOUSEBUTTONUP:
                                    if shieldBtnRect.collidepoint(pygame.mouse.get_pos()):
                                          
                                          print(currentTime - lastShieldTime)
                                          if not shielded:
                                                lastShieldTime = currentTime
                                                shielded = True
                                    held = False
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
                  
                  shieldX, shieldY = cubeX-16, cubeY-16
                  #zobrazení všech elementů na obrazovku
                  sky = disp.blit(skyImage, (0,0)) #pozadí
                  pygame.draw.rect(disp, GND_COLOR, groundRect) #hlína
                  pygame.draw.rect(disp, OVERLAY_GND_COLOR, groundOverlay) #tráva

                  cube = disp.blit(cubeImage, (cubeX,cubeY)) #hráčova postava
                  if shielded: 
                        shieldBlit = disp.blit(pygame.transform.scale(shieldImage, (96,96)), (shieldX,shieldY))
                  else:
                        pygame.draw.rect(disp, (240,0,0), shieldBtnRect)
                        shieldBlit = disp.blit(pygame.transform.scale(shieldImage, (96,96)), (-10000,-10000))
                  for obstacle in obstacles:
                        disp.blit(pygame.transform.scale(virusImage, (64,64)), obstacle['rect'])
                        print(obstacle['type'])
                  checkShield(shieldBlit, obstacles)
                  checkCollision(cube, obstacles, score)
                  pygame.display.update()
                  gameClock.tick(FRAMERATE)
            pygame.quit()
      def mainMenu(score=0, death=False):
            menu = pygame_menu.Menu('Just Jump', DISP_SIZE[0], DISP_SIZE[1], theme=pygame_menu.themes.THEME_BLUE)
            if death:
                  menu.add.label(f'You died!')
            menu.add.label(f'Score: {score}')
            menu.add.button('Play', game)
            menu.add.button('Quit', pygame_menu.events.EXIT)
            menu.mainloop(disp)

      def spawnObstacle(obstacles: list):
            spawnPos = randint(0,2) #0 nahoře, 1, vlevo, 2 vpravo
            if spawnPos == 0:
                  obstRect = pygame.Rect(720//3, -50, 50, 50)
                  obstacles.append({'rect': obstRect, 'speed': 10, 'type': 'top'})
            elif spawnPos == 1:
                  obstRect = pygame.Rect(-50, 340, 50, 50)
                  obstacles.append({'rect': obstRect, 'speed': 10, 'type': 'right'})
            elif spawnPos == 2:
                  obstRect = pygame.Rect(720, 340, 50, 50)
                  obstacles.append({'rect': obstRect, 'speed': -10, 'type': 'left'})
      
      def updateObstacles(obstacles):
            for obstacle in obstacles:
                  print("After update: rect.left:", obstacle['rect'].left, "speed:", obstacle['speed'])
                  if obstacle['type'] == 'left' or obstacle['type'] == 'right':
                        obstacle['rect'].move_ip(obstacle['speed'], 0)
                  elif obstacle['type'] == 'top':
                        obstacle['rect'].move_ip(0, obstacle['speed'])
                  if obstacle['rect'].right < 0 or obstacle['rect'].left > DISP_SIZE[0] or obstacle['rect'].top > 540:
                        obstacles.remove(obstacle)

      def checkCollision(player, obstacles, score):
            for obstacle in obstacles:
                  if player.colliderect(obstacle['rect']):
                        mainMenu(score, death=True)

      def checkShield(shield, obstacles):
            for obstacle in obstacles:
                  if obstacle['type'] == 'top' and shield.colliderect(obstacle['rect']):
                        obstacles.remove(obstacle)

      mainMenu()




if __name__ == '__main__':
      main()