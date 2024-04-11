#Maturitní zkouška z předmětu 'Aplikovaná informatika'
#Téma: Postřehová hra pro dotykové tabule
#Gymnázium Sokolov a KVC
#Lukáš Rada 8.A 2023/2024
#Vytvořeno v pythonu s knihovnou pygame

import time

import pygame

#konstanty
DISP_SIZE = (720,540) #velikost obrazovky
BG_COLOR = (75,75,75) #barva pozadí
GND_COLOR = (56, 25, 2) #barva hlíny
OVERLAY_GND_COLOR = (22, 145, 0) #barva trávy nad hlínou
FRAMERATE = 60 #snímková frekvence (FPS)
GROUND_Y = DISP_SIZE[1]-200 #podlaha, na které bude postava stát a skákat
JUMP_HEIGHT = 100  # výška skoku
GRAVITY = 1.75  # gravitace

#funkce main; pokud bych jinde importoval main.py, nespustí se mi hra znovu
def main():
      #základní setup hry
      pygame.init()
      pygame.font.init()
      inMenu = True
      disp = pygame.display.set_mode(DISP_SIZE)
      gameClock = pygame.time.Clock()

      font = pygame.font.SysFont('Comic Sans MS', 40)
      virusImage = pygame.image.load('assets/virus.png')
      skyImage = pygame.image.load('assets/sky.png')
      cubeImage = pygame.image.load('assets/cube.png')
      groundRect = pygame.Rect(0,DISP_SIZE[1]-160,DISP_SIZE[0],160)
      groundOverlay = pygame.Rect(0,DISP_SIZE[1]-160,DISP_SIZE[0],60)
      resButton = pygame.Rect(100,270,150,100)
      
      cubeX = DISP_SIZE[0]//3
      cubeY = GROUND_Y/1.5
      cubeVelocity = 0
      jumping = True
      obstX = DISP_SIZE[0]
      running = True
      held = False
      dead = False
      inMenu = False 

      #hlavní smyčka hry
      while running:
            
            #hra projde každý event při jedné herní smyčce
            for event in pygame.event.get():
                  if event.type == pygame.QUIT:
                        running = False
                  #kontrola stisknutí a držení levého tlačítka na myši
                  if not inMenu:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                              held = True
                        elif event.type == pygame.MOUSEBUTTONUP:
                              held = False
                  else:

                        pos = pygame.mouse.get_pos()
                        if event.type == pygame.MOUSEBUTTONUP and resButton.collidepoint(pos):
                              obstX = DISP_SIZE[0] 
                              time.sleep(0.5)
                              dead = False
                              inMenu = False
                              
                              
            #pokud hráč není ve vzduchu a levé tlačítko je stisknuto/podrženo, postava vyskočí a sníží svou vertikální rychlost
            if not jumping and cubeY == GROUND_Y:
                  if held:
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
            if obstX < 0:
                  obstX = DISP_SIZE[0]
            
            
            #zobrazení všech elementů na obrazovku
            if not dead:
                  resButton = pygame.Rect(0,0,0,0)
                  obstX -= 10
                  sky = disp.blit(skyImage, (0,0)) #pozadí
                  
                  pygame.draw.rect(disp, GND_COLOR, groundRect) #hlína
                  pygame.draw.rect(disp, OVERLAY_GND_COLOR, groundOverlay) #tráva
                  virus = disp.blit(pygame.transform.scale(virusImage, (64,64)), (obstX, GROUND_Y))
                  cube = disp.blit(cubeImage, (cubeX,cubeY)) #hráčova postava

            if cube.colliderect(virus):
                  resButton = pygame.Rect(100,270,150,100)  
                  disp.fill(BG_COLOR)
                  text = font.render('Game over', True, (255,0,0))
                  reset = pygame.draw.rect(disp, (0,255,255), resButton)
                  disp.blit(text, (DISP_SIZE[0]//2, DISP_SIZE[1]//2))
                  dead = True
                  inMenu = True

            pygame.display.update()
            gameClock.tick(FRAMERATE)

      pygame.quit()



if __name__ == '__main__':
      main()