#Maturitní zkouška z předmětu 'Aplikovaná informatika'
#Téma: Postřehová hra pro dotykové tabule
#Gymnázium Sokolov a KVC
#Lukáš Rada 8.A 2023/2024

import pygame

#konstanty
DISP_SIZE = (720,540) #velikost obrazovky
BG_COLOR = (75,75,75) #barva pozadí
GND_COLOR = (56, 25, 2) #barva hlíny
OVERLAY_GND_COLOR = (22, 145, 0) #barva trávy nad hlínou
FRAMERATE = 60 #snímková frekvence (FPS)
GROUND_Y = DISP_SIZE[1]-200 #podlaha, na které bude postava stát a skákat
JUMP_HEIGHT = 100  # výška skoku
GRAVITY = 1.5  # gravitace

#funkce main; pokud bych jinde importoval main.py, nespustí se mi hra znovu
def main():
      #základní setup hry
      pygame.init()
      disp = pygame.display.set_mode(DISP_SIZE)
      gameClock = pygame.time.Clock()

      skyImage = pygame.image.load('assets/sky.png')
      cubeImage = pygame.image.load('assets/cube.png')
      groundRect = pygame.Rect(0,DISP_SIZE[1]-160,DISP_SIZE[0],160)
      groundOverlay = pygame.Rect(0,DISP_SIZE[1]-160,DISP_SIZE[0],60)

      cubeX = DISP_SIZE[0]//3
      cubeY = GROUND_Y
      cubeVelocity = 0
      jumping = False

      #hlavní smyčka hry
      running = True
      held = False
      while running:
            
            #hra projde každý event při jedné herní smyčce
            for event in pygame.event.get():
                  if event.type == pygame.QUIT:
                        running = False
                  elif event.type == pygame.MOUSEBUTTONDOWN:
                        held = True
                  elif event.type == pygame.MOUSEBUTTONUP:
                        held = False
            if not jumping:
                  if held:
                        jumping = True
                        cubeVelocity = -20
            if jumping:
                  cubeY += cubeVelocity
                  cubeVelocity += GRAVITY

                  if cubeY >= GROUND_Y:
                        cubeY = GROUND_Y
                        jumping = False
                        cubeVelocity = 0

      
            #zobrazení všech elementů na obrazovku
            sky = disp.blit(skyImage, (0,0)) #pozadí
            pygame.draw.rect(disp, GND_COLOR, groundRect) #hlína
            pygame.draw.rect(disp, OVERLAY_GND_COLOR, groundOverlay) #tráva
            cube = disp.blit(cubeImage, (cubeX,cubeY)) #hráčova postava
            
           
            pygame.display.update()
            gameClock.tick(FRAMERATE)

      pygame.quit()



if __name__ == '__main__':
      main()