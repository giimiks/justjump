import pygame

#konstanty
DISP_SIZE = (720,560)
BG_COLOR = (50,50,50)

#funkce main; pokud bych jinde importoval main.py, nespustí se mi hra znovu
def main():
      #základní setup hry
      pygame.init()
      disp = pygame.display.set_mode(DISP_SIZE)
      
      pygame.image.load('assets/cube.png')
      cubeImage = pygame.transform.scale(pygame.image.load('assets/cube.png'), (56,56))
      #hlavní smyčka hry
      running = True
      while running:
            #hra projde každý event při jedné herní smyčce
            for event in pygame.event.get():
                  if event.type == pygame.QUIT:
                        running = False

            disp.fill(BG_COLOR)
            cube = disp.blit(cubeImage, (50,40))
            
            pygame.display.flip()

      pygame.quit()



if __name__ == '__main__':
      main()