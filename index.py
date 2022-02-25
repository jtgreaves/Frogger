import random, pygame, os

pygame.init()
monitorSize = [pygame.display.Info().current_w, pygame.display.Info().current_h]
screenSize = [500, 500]
screen = pygame.display.set_mode((screenSize[0], screenSize[1]), pygame.RESIZABLE)
pygame.display.set_caption("Frogger - Joshua Greaves")

clock = pygame.time.Clock()

current_path = os.path.dirname(__file__)
assets_path = os.path.join(current_path, 'assets')

class AbstractRegion:
	def updateRegion(self):
		pass 

	def drawRegion(self, pos): # Pos being row on screen
		pass

	def updateRegion(self, pos): # Pos being row on screen
		pass 

	def spawnRegion(mapWidth):
		pass

class SafeRegion(AbstractRegion):
	tileAssets = []

	def __init__(self, mapWidth):
		self.tiles = [] # Array of numbers (standing for type)
		self.regionWidth = mapWidth

		for tile in range(mapWidth):
			if random.randint(0, 4) == 0: type = random.randint(10, 60) // 10 # 1 in 4 chance of being a different tile to "default"
			else: type = 0

			self.tiles.append(type)

	def drawRegion(self, pos):
		tileNum = 0 
		while tileNum < len(self.tiles): 
			screen.blit(SafeRegion.tileAssets[self.tiles[tileNum]], (((screenSize[0] // self.regionWidth) * tileNum), screenSize[1] - (pos * (screenSize[1] // 10))))
			tileNum += 1
	
	def spawnRegion(mapWidth):
		return SafeRegion(mapWidth)

	
			
class RoadRegion(AbstractRegion):
	def __init__(self): 
		pass

class RailRegion(AbstractRegion): 
	def __init__(self): 
		pass 

class WaterRegion(AbstractRegion):
	def __innit__(self): 
		pass

class AbstractScreen:
	def updateScreen(self): 
		pass 

	def drawScreen(self, screen):
		pass
	
	def handleInput(self, e):
		pass

	def nextScreen(self):
		return self
		
class GameScreen(AbstractScreen):
	def __init__(self):
		self.map = []
		self.mapDimensions = [int(screenSize[0] // (screenSize[1]//10)), 10]

		self.playerState = "forwards"
		self.playerPosition = [(screenSize[0] // 10) * 5, screenSize[1] - (screenSize[1] // 10)]

		SafeRegion.tileAssets = [pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '0.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '1.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '2.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '3.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '4.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '5.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '6.png')), (screenSize[1]//10, screenSize[1]//10))] # Loads here, once the scale for the window has been locked
		
		self.playerAssets = {
		"forwards": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', 'forwards.png')), (screenSize[1]//10, screenSize[1]//10)),
		"forwards_tongue": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', 'forwards_tongue.png')), (screenSize[1]//10, screenSize[1]//10)),
		"dead": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', 'dead.png')), (screenSize[1]//10, screenSize[1]//10)),
		"right": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', 'right.png')), (screenSize[1]//10, screenSize[1]//10)),
		"right_jump1": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', 'right_jump1.png')), (screenSize[1]//10, screenSize[1]//10)),
		"right_jump2": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', 'right_jump2.png')), (screenSize[1]//10, screenSize[1]//10))
		}

	def handleInput(self, e):
		if e.type == pygame.KEYDOWN: 
			if e.key == pygame.K_w: 
				newValue = self.playerPosition[1] - (screenSize[1]//10)
				if newValue < (screenSize[1]//10)*7: self.map.pop(0)
				else: self.playerPosition[1] -= (screenSize[1]//10)
			elif e.key == pygame.K_a: 
				self.playerPosition[0] -= (screenSize[1]//10)
			elif e.key == pygame.K_s: 
				self.playerPosition[1] += (screenSize[1]//10)
			elif e.key == pygame.K_d:
				self.playerPosition[0] += (screenSize[1]//10)

	def updateScreen(self):
		if len(self.map) < 12: self.generateRegions(self.map)
		
		for regionNum in range(len(self.map)): self.map[regionNum].updateRegion(regionNum)
		
	def drawScreen(self, screen): 
		screen.fill((0,0,0))
		# for region in self.map: region.drawRegion(screenSize[0] // (screenSize[1]//10))
		for regionNum in range(len(self.map)): self.map[regionNum].drawRegion(regionNum)

		screen.blit(self.playerAssets[self.playerState], (self.playerPosition[0], self.playerPosition[1]))

	def generateRegions(self, map): # Previous tile based generation
		chance = random.randint(0, 100)
		if len(map) == 0: 
			if chance < 20: map.append(WaterRegion(self.mapDimensions[0]))
			elif chance < 65: map.append(RoadRegion(self.mapDimensions[0]))
			elif chance < 80: map.append(RailRegion(self.mapDimensions[0]))
			else: map.append(SafeRegion(self.mapDimensions[0]))
		
		elif isinstance(map[len(map)-2], SafeRegion): # Last region was Safe 
			if chance < 45: map.append(WaterRegion(self.mapDimensions[0]))
			elif chance < 80: map.append(RoadRegion(self.mapDimensions[0]))
			elif chance < 85: map.append(RailRegion(self.mapDimensions[0]))
			else: map.append(SafeRegion(self.mapDimensions[0]))

		elif isinstance(map[len(map)-2], RoadRegion): # Last region was Road
			if chance < 20: map.append(WaterRegion(self.mapDimensions[0]))
			# elif chance < 45: map.append(RoadRegion(self.mapDimensions[0])) # 0% chance 
			elif chance < 35: map.append(RailRegion(self.mapDimensions[0]))
			else: map.append(SafeRegion(self.mapDimensions[0]))

		elif isinstance(map[len(map)-2], RailRegion): # Last region was Rail 
			if chance < 25: map.append(WaterRegion(self.mapDimensions[0]))
			elif chance < 25: map.append(RoadRegion(self.mapDimensions[0]))
			# elif chance < 45: map.append(RailRegion(self.mapDimensions[0])) # 0% chance 
			else: map.append(SafeRegion(self.mapDimensions[0]))

		elif isinstance(map[len(map)-2], WaterRegion): # Last region was Water 
			# if chance < 45: map.append(WaterRegion(self.mapDimensions[0])) # 0% chance 
			if chance < 25: map.append(RoadRegion(self.mapDimensions[0]))
			elif chance < 10: map.append(RailRegion(self.mapDimensions[0]))
			else: map.append(SafeRegion(self.mapDimensions[0]))

		# map.append(SafeRegion.spawnRegion(self.mapDimensions[0]))
		
class StartScreen(AbstractScreen): 
	def __init__(self): 
		self.startGame = False

	def handleInput(self, event):
		if event.type == pygame.KEYDOWN:
			if not event.key == pygame.K_LSHIFT and not event.key == pygame.K_F11: self.startGame = True 
		
	def drawScreen(self, screen):
		screen.fill((255, 255, 255)) 

		if self.startGame == True: screen = pygame.display.set_mode((screenSize[0], screenSize[1])) # Does not allow resizing during gameplay

	def nextScreen(self):
		if self.startGame == True: return GameScreen()
		return self  

        


endProgram = False
currentScreen = StartScreen()

fullScreen = False
resizeHeight = False

while endProgram == False:
	for e in pygame.event.get():
		if e.type == pygame.QUIT:
			endProgram = True

		elif e.type == pygame.VIDEORESIZE: # Handles a window resize 
			if not fullScreen:
				if e.w < 500: e.w = 500 # Prevent too small of a window
				if e.h < 500: e.h = 500
				
				if e.w > (e.h * 1.5): 
					if not resizeHeight: e.w = e.h * 1.5 #If the width is larger than 50% of height  
					else: e.h = e.w // 1.5 # If the shift key is held then the height will change to match the width requirements

				if e.w > screenSize[0]: e.w += e.h//10 - (e.w % (e.h//10)) # If the player is trying to enlarge window, it rounds up 
				else: e.w -= e.w % (e.h//10) # Else, trying to shrink; therefore, it rounds down 
					
				screenSize = [e.w, e.h] # Issue the relevant changes 
				screen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)

		elif e.type == pygame.KEYDOWN:
			if e.key == pygame.K_F11: # Toggles fullscreen 
				if fullScreen: screen = pygame.display.set_mode((screenSize[0], screenSize[1]), pygame.RESIZABLE)
				else: screen = pygame.display.set_mode((monitorSize[0], monitorSize[1]), pygame.FULLSCREEN)
				fullScreen = not fullScreen

			elif e.key == pygame.K_LSHIFT:
				resizeHeight = True 

		elif e.type == pygame.KEYUP: 
			if e.key == pygame.K_LSHIFT: 
				resizeHeight = False  
				
		currentScreen.handleInput(e)
	
	currentScreen.updateScreen()
	currentScreen.drawScreen(screen)
	currentScreen = currentScreen.nextScreen()
	
	pygame.display.flip()
	clock.tick(30)

pygame.quit()
quit()