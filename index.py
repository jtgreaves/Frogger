import random, pygame, os, sqlite3

pygame.init()
monitorSize = [pygame.display.Info().current_w, pygame.display.Info().current_h]
screenSize = [750, 750]
screen = pygame.display.set_mode((screenSize[0], screenSize[1]), pygame.RESIZABLE)
pygame.display.set_caption("Frogger - Joshua Greaves")

clock = pygame.time.Clock()

current_path = os.path.dirname(__file__)
assets_path = os.path.join(current_path, 'assets')

courierTitleFont = pygame.font.SysFont('Courier New', 45)
courierSubFont = pygame.font.SysFont('Courier New', 30)
fixedsysSubFont = pygame.font.SysFont('Fixedsys Regular', 50)

class DatabaseHandler: 
	def __init__(self):
		self.conn = DatabaseHandler.loadDatabase("data")
		self.cur = self.conn.cursor()
	
	def loadDatabase(name):
		conn = sqlite3.connect(name + '.db')
		cur = conn.cursor()
		skinTableCreated = False 

		# Create playerData table
		tb_exists = "SELECT name FROM sqlite_master WHERE type='table' AND name='playerData'"
		tb_create = '''CREATE TABLE playerData (
				playerName tinytext NOT NULL,
				totalScore int,
				highScore int,
				skin tinytext,
				coins float,
				totalGamesPlayed numeric,

				CONSTRAINT playerName PRIMARY KEY (playerName)
				);'''
		
		if not cur.execute(tb_exists).fetchone():
			cur.execute(tb_create)
		
		# Create skinAccess table
		tb_exists = "SELECT name FROM sqlite_master WHERE type='table' AND name='skinAccess'"
		tb_create = '''CREATE TABLE skinAccess (
				playerName tinytext NOT NULL,
				skinID tinytext NOT NULL
				);'''
		
		if not cur.execute(tb_exists).fetchone():
			cur.execute(tb_create)
			skinTableCreated = True 


		# Create skins table
		tb_exists = "SELECT name FROM sqlite_master WHERE type='table' AND name='skinData'"
		tb_create = '''CREATE TABLE skinData (
				skinID  tinytext NOT NULL,
				cost int,

				CONSTRAINT skinID PRIMARY KEY (skinID)
				);'''
		
		if not cur.execute(tb_exists).fetchone():
			cur.execute(tb_create)

		conn.commit()

		if skinTableCreated: 
			DatabaseHandler.generateSkins(conn, cur)

		return conn 
	
	def getCurrentSkin(self, name):
		name = name.lower()
		self.cur.execute("SELECT skin FROM playerData WHERE playerName=?", (name, ))
		results = self.cur.fetchone()
		return results[0]

	def generateSkins(conn, cur): 
		skinPaths = []
		for dirs in os.listdir(os.path.join(assets_path, 'entities', 'frog')):
			skinPaths.append(dirs) # Loops through the skin directory and adds to database

		cost = 500
		for skin in skinPaths:
			cur.execute("INSERT INTO skinData (skinID, cost) VALUES (?, ?)", (skin, cost))
			cost += 150

		conn.commit()
	
	def getSkins(self):
		self.cur.execute("SELECT skinID FROM skinData")
		results = self.cur.fetchall()
		return results

	def checkSkinAccess(self, name, skin): 
		name = name.lower()
		print("!", skin)
		self.cur.execute("SELECT skinID FROM skinAccess WHERE playerName=? and skinID=?", (name, skin ))
		results = self.cur.fetchone()
		if results == None: 
			return False
		else: 
			return True

	def addAccess(self, name, skin): 
		name = name.lower()
		self.cur.execute("SELECT playerName FROM skinAccess WHERE playerName=? AND skinID=?", (name, skin))
		results = self.cur.fetchone()
		if results == None: 
			self.cur.execute("INSERT INTO skinAccess (playerName, skinID) VALUES (?, ?)", (name, skin))
			self.conn.commit()

	def loadSkin(self, name, skin):
		name = name.lower()
		self.cur.execute("UPDATE playerData SET skin=? WHERE playerName=?", (skin, name))
		self.conn.commit()
	
	def fetchSkinCost(self, name):
		name = name.lower()
		self.cur.execute("SELECT cost FROM skinData WHERE skinID=?", (name, ))
		results = self.cur.fetchone()
		return results[0]

	def unlockSkin(self, name, skin): 
		name = name.lower()
		self.cur.execute("INSERT INTO skinAccess (playerName, skinID) VALUES (?, ?)", (name, skin))
		self.conn.commit()

	def initiatePlayer(self, name):
		name = name.lower()
		self.cur.execute("SELECT playerName FROM playerData WHERE playerName=?", (name, ))
		results = self.cur.fetchone()
		if results == None: 
			self.createPlayer(name)

	def loadPlayer(self, name):
		name = name.lower()
		self.cur.execute("SELECT * FROM playerData WHERE playerName=?", (name, ))
		results = self.cur.fetchone()
		
		if results == None: 
			return False 
		else: 
			return results
	
	def getPlayerCoins(self, name):
		name = name.lower()
		self.cur.execute("SELECT coins FROM playerData WHERE playerName=?", (name, ))
		results = self.cur.fetchone()
		return results[0]


	def createPlayer(self, name):
		name = name.lower()
		self.cur.execute("SELECT playerName FROM playerData WHERE playerName=?", (name, ))
		results = self.cur.fetchone()

		if results == None: 
			self.cur.execute("""
			INSERT INTO playerData (playerName, totalScore, highScore, skin, coins, totalGamesPlayed)
			VALUES(?, ?, ?, ?, ?, ?);
			""", (name, 0, 0, "default", 0, 0))
			self.conn.commit()
		else: 
			return False 		

	def updatePlayer(self, name, intent, value): 
		name = name.lower()

		if intent == "updateName": 
			self.cur.execute("SELECT playerName FROM playerData WHERE playerName=?", (name, ))
			results = self.cur.fetchone()
			if results == None: 
				sql = ''' UPDATE playerData
             		SET playerName = ?
              		WHERE playerName = ?'''
				self.cur.execute(sql, (value, name, ))
				self.conn.commit()
				return True 
			else:
				return False 

		elif intent == "totalScoreIncrement": 
			self.cur.execute("SELECT totalScore FROM playerData WHERE playerName=?", (name, ))
			results = self.cur.fetchone()
			if results != None: 
				sql = ''' UPDATE playerData
             		SET totalScore = ?
              		WHERE playerName = ?'''
				self.cur.execute(sql, ((value + results[0]), name, ))
				self.conn.commit()
				return True 
			else:
				return False 
		elif intent == "highScoreUpdate": 
			self.cur.execute("SELECT playerName FROM playerData WHERE playerName=?", (name, ))
			results = self.cur.fetchone()
			if results != None: 
				sql = ''' UPDATE playerData
             		SET highScore = ?
              		WHERE playerName = ?'''
				self.cur.execute(sql, (value, name, ))
				self.conn.commit()
				return True 
			else:
				return False 
		
		elif intent == "currentSkin": 
			self.cur.execute("SELECT playerName FROM playerData WHERE playerName=?", (name, ))
			results = self.cur.fetchone()
			if results != None: 
				sql = ''' UPDATE playerData
             		SET skin = ?
              		WHERE playerName = ?'''
				self.cur.execute(sql, (value, name, ))
				self.conn.commit()
				return True 
			else:
				return False 

		elif intent == "totalGamesIncrement": 
			self.cur.execute("SELECT playerName, totalGamesPlayed FROM playerData WHERE playerName=?", (name, ))
			results = self.cur.fetchone()
			if results != None: 
				sql = ''' UPDATE playerData
			 		SET totalGamesPlayed = ?
			  		WHERE playerName = ?'''
				self.cur.execute(sql, ((value + results[1]), name, ))
				self.conn.commit()
				return True 
			else:
				return False

		elif intent == "coinsAddition": 
			if value == None: return False 
			self.cur.execute("SELECT playerName, coins FROM playerData WHERE playerName=?", (name, ))
			results = self.cur.fetchone()
			if results != None:
				sql = ''' UPDATE playerData
					SET coins = ?
					WHERE playerName = ?'''
				self.cur.execute(sql, ((value + results[1]), name, ))
				self.conn.commit()
				return True
			else:
				return False

		elif intent == "coinsSubtraction": 
			if value == None: return False 
			self.cur.execute("SELECT playerName, coins FROM playerData WHERE playerName=?", (name, ))
			results = self.cur.fetchone()
			if results != None:
				sql = ''' UPDATE playerData
					SET coins = ?
					WHERE playerName = ?'''
				self.cur.execute(sql, ((results[1] - value), name, ))
				self.conn.commit()
				return True
			else:
				return False
		

	def closeConnection(self):
		self.conn.commit()
		self.conn.close()

class AbstractEntity: 
	def spawnEntity(): 
		pass 
	
	def updateEntity(self, player):
		pass

	def drawEntity(self, pos): 
		pass

class TractorEntity(AbstractEntity):
	entityAssets = [] 

	def __init__(self, imageAsset, entityX, direction):
		self.x = entityX
		self.direction = direction
		self.imageAsset = imageAsset
		self.speed = screenSize[0]//(2 * 30) # 5 being speed; 30 being refresh rate
		self.mask = pygame.mask.from_surface(self.imageAsset)
		self.rect = None

	def spawnOriginEntities(): 
		direction = random.randint(0,1)
		if direction == 0: entityX = random.randint(200, 350)
		else: entityX = screenSize[0] - 100 - random.randint(200, 350)
		
		imageAsset = TractorEntity.entityAssets[direction][random.randint(0,3)]
		
		return TractorEntity(imageAsset, entityX, direction)

	def spawnEntity():
		direction = random.randint(0,1)
		if direction == 0: entityX = -250
		else: entityX = screenSize[0] + 250		
		assetNumber = random.randint(0,3)	
	
		imageAsset = TractorEntity.entityAssets[direction][assetNumber]
		return TractorEntity(imageAsset, entityX, direction)

	def updateEntity(self, player):
		if self.direction == 0: self.x += self.speed
		else: self.x -= self.speed

		if self.x < -250 or self.x > screenSize[0] + 250: 
			return 1 # Remove entity 
		
		if not self.rect == None: 
			if player.checkCollision(self.rect, self.mask):
				player.state = "dead" 
				player.dead()

	def drawEntity(self, pos):
		self.rect = screen.blit(self.imageAsset, (self.x, screenSize[1] - (pos * (screenSize[1] // 10))))		

class CarEntity(AbstractEntity): 
	entityAssets = []
	
	def __init__(self, imageAsset, entityX, direction): 
		self.x = entityX
		self.imageAsset = imageAsset 
		self.direction = direction
		self.speed = screenSize[0]//(2 * 30) # 5 being speed; 30 being refresh rate
		self.mask = pygame.mask.from_surface(self.imageAsset)
		self.rect = None

		
	def spawnEntity(laneDirection):
		if laneDirection == 0: entityX = -100
		else: entityX = screenSize[0]		

		chance = random.randint(0,50)

		if chance < 10: assetNumber = random.randint(3,7) # 1/5 chance of spawning a lorry  
		else: assetNumber = random.randint(0, 3) # The rest of the time, spawn a car 
		
		imageAsset = CarEntity.entityAssets[laneDirection][assetNumber]

		return CarEntity(imageAsset, entityX, laneDirection)

	def spawnOriginEntities(laneDirection): 
		entities = [] 

		lastX = 0 
		for entity in range(random.randint(0,5)): 
			if laneDirection == 0: entityX = lastX + random.randint(200, 350)
			else: entityX = lastX + screenSize[0] - 100 - random.randint(200, 350)
			imageAsset = CarEntity.entityAssets[laneDirection][random.randint(0,7)]

			lastX = entityX
			entities.append(CarEntity(imageAsset, entityX, laneDirection))
		
		return entities

	def updateEntity(self, player):
		if self.direction == 0: self.x += self.speed
		else: self.x -= self.speed

		if self.x < -100 or self.x > screenSize[0]: 
			return 1 # Remove entity 
		
		if not self.rect == None: 
			if player.checkCollision(self.rect, self.mask):
				player.state = "dead" 
				player.dead()

	def drawEntity(self, pos):
		self.rect = screen.blit(self.imageAsset, (self.x, screenSize[1] - (pos * (screenSize[1] // 10))))

class TrainEntity(AbstractEntity): 
	entityAssets = []

	def __init__(self, x, type, direction, speed): 
		self.x = x
		self.type = type
		self.direction = direction 
		self.speed = speed
		self.imageAsset = type
		self.mask = pygame.mask.from_surface(self.imageAsset)
		self.rect = None
	
	def spawnEntity():
		entities = []
		direction = random.randint(0, 1)
		length = random.randint(2, 8)
		speed = screenSize[0]//(2 * random.randint(10, 30))
		for carriageNum in range(length): 
			if carriageNum == 0: type = 0
			else: type = random.randint(1,4)
			
			carriageNum += 1
			if direction == 0: 
				entityX = -100 - (carriageNum * (2 * screenSize[1]//10))
				type = TrainEntity.entityAssets[0][type]
			else:
				entityX = screenSize[0] + (carriageNum * (2 * screenSize[1]//10))
				type = TrainEntity.entityAssets[1][type]
			
			entities.append(TrainEntity(entityX, type, direction, speed))

		return entities 
	
	def updateEntity(self, player):
		if self.direction == 1: self.x -= self.speed
		else: self.x += self.speed

		if self.direction == 0 and self.x > screenSize[0] + 250: return True
		elif self.direction == 1 and self.x < -250: return True
		
		if not self.rect == None: 
			if player.checkCollision(self.rect, self.mask):
				player.state = "dead" 
				player.dead()


	def drawEntity(self, pos):
		self.rect = screen.blit(self.imageAsset, (self.x, screenSize[1] - (pos * (screenSize[1] // 10))))

class LogEntity(AbstractEntity): 
	entityAssets = {} 

	def __init__(self, x, imageAsset, direction, speed):
		self.x = x 
		self.imageAsset = imageAsset
		self.direction = direction  
		self.speed = speed

		self.rect = None

	def updateEntity(self, player): 

		if self.direction == 1: self.x -= self.speed
		else: self.x += self.speed

		if self.direction == 0 and self.x > screenSize[0] + 250: return True
		elif self.direction == 1 and self.x < -250: return True
		

	def checkPlayerCollision(self, player): 
		if not self.rect == None:
			playerArea = pygame.Rect(player.position[0] + (screenSize[1]//20), player.position[1], 1, (screenSize[1]//20))
			if self.rect.colliderect(playerArea):
				return True 
			else: return False 

	def spawnRandomEntity(direction, speed):
		entities = []
		length = random.randint(2,4)

		if length == 2: type = ["F2"]
		elif length == 3: type = ["F1", "T1"]
		elif length == 4: type = ["F1", "T2"]

		for sectionNum in range(len(type)):
			imageAsset = LogEntity.entityAssets[type[sectionNum]]
			
			if direction == 0: x = -100 - (sectionNum * (screenSize[1]//10))
			else: x = screenSize[0] + 250 - (sectionNum * (screenSize[1]//10))
			
			entities.append(LogEntity(x, imageAsset, direction, speed))
		
		return entities
	
	def drawEntity(self, pos):
		self.rect = screen.blit(self.imageAsset, (self.x, screenSize[1] - (pos * (screenSize[1] // 10))))

class AbstractRegion:
	def updateRegion(self):
		pass 

	def drawRegion(self, pos): # Pos being row on screen
		pass

	def updateRegion(self, pos, player): # Pos being row on screen
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
		for tileNum in range(len(self.tiles)): screen.blit(SafeRegion.tileAssets[self.tiles[tileNum]], (((screenSize[0] // self.regionWidth) * tileNum), screenSize[1] - (pos * (screenSize[1] // 10))))
	
	def spawnRegion(mapWidth):
		return [SafeRegion(mapWidth)]
			
class RoadRegion(AbstractRegion):
	tileAssets = {}

	def __init__(self, mapWidth, tileType, direction): 
		self.tileType = tileType
		self.direction = direction #0 = W; 1 = E
		self.regionWidth = mapWidth
		self.lastSpawn = 0 
		self.entities = CarEntity.spawnOriginEntities(direction)
	
	def spawnRegion(mapWidth):
		lanes = []
		chance = random.randint(0, 100) # Random chance of spawning a road of a certain width 
		if chance < 15: width = 1 
		elif chance < 40: width = 2 
		elif chance < 50: width = 3
		elif chance < 75: width = 4 
		elif chance < 85: width = 5
		else: width = 6 
		
		previousLaneType = 0
		laneDirections = []
		for x in range(width): laneDirections.append(random.randint(0, 1)) # Declares each lane's direction beforehand.
		
		for lane in range(width):
			tilePath = "" 
			thisDirection = laneDirections[lane]
			
			laneType = random.randint(0, 1)

			if lane == 0: #If this is a bottom tile
				tilePath += "B"
				if width > 1:
					if laneDirections[lane+1] == thisDirection: tilePath += "_W" # Next lane, same direction
					else: tilePath += "_Y"

					if laneType == 0: tilePath += "_D"
					else: tilePath += "_S"	

			elif lane == width-1: # If this is the top tile 
				tilePath += "T"
				
				if laneDirections[lane-1] == thisDirection: tilePath += "_W"
				else: tilePath += "_Y"

				if previousLaneType == 0: tilePath += "_D"
				else: tilePath += "_S"

			else: 
				tilePath += "M"

				if laneDirections[lane-1] == thisDirection: tilePath += "_W"
				else: tilePath += "_Y"

				if laneDirections[lane+1] == thisDirection: tilePath += "W"
				else: tilePath += "Y"

				if previousLaneType == 0: tilePath += "_D"
				else: tilePath += "_S"

				if laneType == 0: tilePath += "D"
				else: tilePath += "S" 

			lanes.append(RoadRegion(mapWidth, tilePath, laneDirections[lane]))
			previousLaneType = laneType 

		return lanes 

	def updateRegion(self, pos, player):
		if FreePlay_GameScreen.timer - self.lastSpawn > 5 and random.randint(0, 50) == 0:
			self.entities.append(CarEntity.spawnEntity(self.direction))
			self.lastSpawn = FreePlay_GameScreen.timer
		
		for entity in self.entities: 
			if entity.updateEntity(player) == 1: self.entities.remove(entity)


	def drawRegion(self, pos):
		for tileNum in range(self.regionWidth): 
			screen.blit(RoadRegion.tileAssets[self.tileType], (((screenSize[0] // self.regionWidth) * tileNum), screenSize[1] - (pos * (screenSize[1] // 10))))
		
		for entity in self.entities: entity.drawEntity(pos)

class RailRegion(AbstractRegion): 
	tileAssets = {}

	def __init__(self, mapWidth): 
		self.tiles = [] # Array of numbers (standing for type)
		self.regionWidth = mapWidth
		
		self.incomingTrain = False # Whether a train is coming in 
		self.declaredTimer = 0 # Since a train declared 
		self.alertsActive = False # Blinking lights 
		self.trainArrived = False # Whether the train is on the screen
		self.lastSpawn = 0 # Since the last train passed

		self.entities = []

		for tile in range(mapWidth):
			if tile == 0: self.tiles.append("left")
			if tile == (mapWidth-2): self.tiles.append("right")
			else: self.tiles.append("middle")
	
	def updateRegion(self, pos, player):
		if self.incomingTrain:
			if self.declaredTimer % 15 == 0: 
				self.alertsActive = not self.alertsActive
				if self.alertsActive == True: 
					self.tiles[0] = "left_alarm"
					self.tiles[len(self.tiles) - 2] = "right"
				else: 
					self.tiles[len(self.tiles) - 2] = "right_alarm"
					self.tiles[0] = "left"
				
			self.declaredTimer += 1
			
			if self.declaredTimer > random.randint(50, 150) and not self.trainArrived:
				self.trainArrived = True 
				self.entities = TrainEntity.spawnEntity()
			
		elif random.randint(0, 100) == 0:
		# elif FreePlay_GameScreen.timer - self.lastSpawn > 0:
			self.trainDelcared = FreePlay_GameScreen.timer
			self.incomingTrain = True 
		
		for entity in self.entities: 
			if entity.updateEntity(player):
				self.entities.remove(entity)

				# Clear Variables
				self.lastSpawn = FreePlay_GameScreen.timer
				self.incomingTrain = False 
				self.trainArrived = False 
				self.alertsActive = False 
				self.declaredTimer = 0
				self.tiles[0] = "left"
				self.tiles[len(self.tiles) - 2] = "right"



	def drawRegion(self, pos):
		for tileNum in range(len(self.tiles)): screen.blit(RailRegion.tileAssets[self.tiles[tileNum]], (((screenSize[0] // self.regionWidth) * tileNum), screenSize[1] - (pos * (screenSize[1] // 10))))
		for entity in self.entities: entity.drawEntity(pos)

	def spawnRegion(mapWidth):
		return [RailRegion(mapWidth)]

class TractorRegion(AbstractRegion): 
	tileAsset = None

	def __init__(self, mapWidth): 
		self.lastSpawn = 0 # Since the last train passed
		self.entities = []
		self.regionWidth = mapWidth

	def updateRegion(self, pos, player):
		if len(self.entities) == 0:
			self.entities.append(TractorEntity.spawnEntity())
			self.lastSpawn = FreePlay_GameScreen.timer
		
		for entity in self.entities: 
			if entity.updateEntity(player): self.entities.remove(entity)

	def drawRegion(self, pos):
		for tileNum in range(self.regionWidth): screen.blit(TractorRegion.tileAsset, (((screenSize[0] // self.regionWidth) * tileNum), screenSize[1] - (pos * (screenSize[1] // 10))))
		for entity in self.entities: entity.drawEntity(pos)

	def spawnRegion(mapWidth):
		return [SafeRegion(mapWidth), TractorRegion(mapWidth), SafeRegion(mapWidth)]

class WaterRegion(AbstractRegion):
	tileAssets = []

	def __init__(self, mapWidth, tileType, direction, speed): #
		self.entities = [] 

		self.tileType = tileType #0 = Logs; 1 = Turtles; (3 = Crocadile) 
		self.direction = direction #0 = W; 1 = E
		self.regionWidth = mapWidth		
		self.length = None 
		self.speed = speed

		self.lastSpawn = -200
		self.playerDeath = False 


	def updateRegion(self, pos, player):
		timeDifference = FreePlay_GameScreen.timer - self.lastSpawn
		spawn = False 
		if timeDifference < 80: pass 
		elif timeDifference < 250 and random.randint(0,6) == 0 and spawn == False: spawn = True
		elif timeDifference < 500 and random.randint(0,4) == 0 and spawn == False: spawn = True
		else: spawn = True
		
		if spawn == True:
			self.lastSpawn = FreePlay_GameScreen.timer
			self.entities += LogEntity.spawnRandomEntity(self.direction, self.speed) # Not a predefined length
		
		for entity in self.entities: 
			if entity.updateEntity(player): self.entities.remove(entity)

	
	def checkWaterDeath(self, player): 
		onLog = False 
		for entity in self.entities: 
			if entity.checkPlayerCollision(player): onLog = True 
		
		if onLog == True: 
			player.floating = True
			self.playerDeath = False
			if self.direction: player.position[0] -= self.speed
			else: player.position[0] += self.speed
			return False 
		else: 
			player.floating = False
			if self.playerDeath: 
				return True
			else: 
				self.playerDeath = True 



	def drawRegion(self, pos):
		for tileNum in range(self.regionWidth): 
			screen.blit(WaterRegion.tileAssets[self.tileType], (((screenSize[0] // self.regionWidth) * tileNum), screenSize[1] - (pos * (screenSize[1] // 10))))
		
		for entity in self.entities: entity.drawEntity(pos)

	def spawnRegion(mapWidth):
		rows = []

		direction = random.randint(0,1)
		speed = screenSize[0]//(random.randint(120, 200)) 
		tileType = random.randint(0,1)

		for x in range(random.randint(1,3)): 
			rows.append(WaterRegion(mapWidth, tileType, direction, speed))
			if direction == 0: direction = 1 
			else: direction = 0
		
		return rows

class Player(): 
	playerAssets = {}

	def __init__(self): 
		self.state = "forwards"
		self.position = [(screenSize[0] // 10) * 5, screenSize[1] - (screenSize[1] // 10)]
		self.animationTimer = 0 
		self.mask = None
		self.pendingMove = None
		
		self.floating = False 

		self.alive = True
		self.lives = 1
		self.score = 0 
	
	def update(self): 
		self.mask = pygame.mask.from_surface(Player.playerAssets["forwards"])
		
	
	def draw(self):
		self.rect = screen.blit(Player.playerAssets[self.state], (self.position[0], self.position[1]))

	def checkCollision(self, entityRect, entityMask): 
		if not self.mask == None: 
			offset = (self.rect.center[0]-entityRect.center[0], self.rect.center[1]-entityRect.center[1])

			if self.mask.overlap(entityMask, offset): 
				return True 
	
	def dead(self): 
		self.lives -= 1

		if self.lives < 1: 
			self.alive = False

	def getRow(self): 
		tileSize = screenSize[1] // 10 
		if (self.position[1] - (screenSize[1] - (tileSize))) < 5 and (self.position[1] - (screenSize[1] - (tileSize))) >= 0: return 1
		elif (self.position[1] - (screenSize[1] - (tileSize * 2))) < 5 and (self.position[1] - (screenSize[1] - (tileSize * 2))) >= 0: return 2
		elif (self.position[1] - (screenSize[1] - (tileSize * 3))) < 5: return 3
		else: return None

class AbstractScreen:
	def updateScreen(self): 
		pass 

	def drawScreen(self, screen):
		pass
	
	def handleInput(self, e):
		pass

	def nextScreen(self):
		return self

class GameOverScreen(AbstractScreen): 
	def __init__(self, coins, currentPlayer): 
		self.restartGame = False
		self.exit = False
		self.coinsEarned = coins
		self.currentPlayer = currentPlayer

	def handleInput(self, e):
		if e.type == pygame.KEYDOWN: 
			if e.key == pygame.K_SPACE: 
				self.restartGame = True 
			elif e.key == pygame.K_ESCAPE: 
				self.exit = True 


	def drawScreen(self, screen): 
		text = courierTitleFont.render("Game Over!", True, (255, 255, 255))
		screen.blit(text, text.get_rect(center=(screenSize[0]//2, screenSize[1]//10 * 3))) 
		text = courierTitleFont.render("Coins: " + str(self.coinsEarned), True, (255, 255, 255))
		screen.blit(text, text.get_rect(center=(screenSize[0]//2, screenSize[1]//10 * 4))) 
		text = courierSubFont.render("Press SPACE to player again", True, (255, 255, 255))
		screen.blit(text, text.get_rect(center=(screenSize[0]//2, screenSize[1]//10 * 6))) 
		text = courierSubFont.render("Press ESC to return to menu", True, (255, 255, 255))
		screen.blit(text, text.get_rect(center=(screenSize[0]//2, screenSize[1]//10 * 6.5))) 
		pass
	
	def nextScreen(self):
		if self.restartGame: return FreePlay_GameScreen(self.currentPlayer)
		elif self.exit: return StartScreen(self.currentPlayer)
		
		return self 
		
class PausedScreen(AbstractScreen): 
	def __init__(self, gameScreen):
		self.unpause = False 
		self.gameScreen = gameScreen
	
	def handleInput(self, e):
		if e.type == pygame.KEYDOWN: 
			self.unpause = True 
	
	def drawScreen(self, screen):
		screen.fill((100, 100, 255))

	def nextScreen(self):
		if self.unpause == True: 
			return self.gameScreen()
		
		return self 

class FreePlay_GameScreen(AbstractScreen):
	timer = 0 

	def __init__(self, currentPlayer):
		self.playerData = database.loadPlayer(currentPlayer)
		self.currentPlayer = currentPlayer
		FreePlay_GameScreen.loadAssets(self)
		
		self.map = []
		self.mapDimensions = [int(screenSize[0] // (screenSize[1]//10)), 10]
		self.player = Player()
		self.pause = False 

		self.gameOver = False
		self.fade = 255

	def loadAssets (self): 
		# Asset loading 
		SafeRegion.tileAssets = [pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '0.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '1.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '2.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '3.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '4.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '5.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'SafeRegion', '6.png')), (screenSize[1]//10, screenSize[1]//10))] # Loads here, once the scale for the window has been locked
		WaterRegion.tileAssets = [pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'WaterRegion', '0.png')), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'WaterRegion', '1.png')), (screenSize[1]//10, screenSize[1]//10))]		
		TractorRegion.tileAsset = pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'TractorRegion', '0.png')), (screenSize[1]//10, screenSize[1]//10))	
		
		Player.playerAssets = {
		"forwards": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'forwards.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)),
		"forwards_jump1": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'forwards_jump1.png')), (screenSize[1]//10, screenSize[1]//10)),
		"forwards_jump2": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'forwards_jump2.png')), (screenSize[1]//10, screenSize[1]//10)),
		"backwards": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'backwards.png')), (screenSize[1]//10, screenSize[1]//10)),
		"backwards_jump1": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'backwards_jump1.png')), (screenSize[1]//10, screenSize[1]//10)),
		"backwards_jump2": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'backwards_jump2.png')), (screenSize[1]//10, screenSize[1]//10)),
		"forwards_tongue": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'forwards_tongue.png')), (screenSize[1]//10, screenSize[1]//10)),
		"dead": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'dead.png')), (screenSize[1]//10, screenSize[1]//10)),
		"right": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'right.png')), (screenSize[1]//10, screenSize[1]//10)),
		"right_jump1": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'right_jump1.png')), (screenSize[1]//10, screenSize[1]//10)),
		"right_jump2": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'right_jump2.png')), (screenSize[1]//10, screenSize[1]//10)),
		"left": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'left.png')), (screenSize[1]//10, screenSize[1]//10)),
		"left_jump1": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3], 'left_jump1.png')), (screenSize[1]//10, screenSize[1]//10)),
		"left_jump2": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', self.playerData[3],  'left_jump2.png')), (screenSize[1]//10, screenSize[1]//10))
		}

		RoadRegion.tileAssets = {
		"B": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'B.png')), (screenSize[1]//10, screenSize[1]//10)),
		"B_W_D": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'B_W_D.png')), (screenSize[1]//10, screenSize[1]//10)),
		"B_W_S": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'B_W_S.png')), (screenSize[1]//10, screenSize[1]//10)),
		"B_Y_D": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'B_Y_D.png')), (screenSize[1]//10, screenSize[1]//10)),
		"B_Y_S": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'B_Y_S.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_WW_DD": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_WW_DD.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_WW_DS": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_WW_DS.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_WW_SD": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_WW_SD.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_WW_SS": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_WW_SS.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_WY_DD": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_WY_DD.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_WY_DS": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_WY_DS.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_WY_SD": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_WY_SD.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_WY_SS": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_WY_SS.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_YW_DD": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_YW_DD.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_YW_DS": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_YW_DS.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_YW_SD": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_YW_SD.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_YW_SS": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_YW_SS.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_YY_DD": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_YY_DD.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_YY_DS": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_YY_DS.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_YY_SD": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_YY_SD.png')), (screenSize[1]//10, screenSize[1]//10)),
		"M_YY_SS": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'M_YY_SS.png')), (screenSize[1]//10, screenSize[1]//10)),
		"T_W_D": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'T_W_D.png')), (screenSize[1]//10, screenSize[1]//10)),
		"T_W_S": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'T_W_S.png')), (screenSize[1]//10, screenSize[1]//10)),
		"T_Y_D": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'T_Y_D.png')), (screenSize[1]//10, screenSize[1]//10)),
		"T_Y_S": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RoadRegion', 'T_Y_S.png')), (screenSize[1]//10, screenSize[1]//10))
		}

		RailRegion.tileAssets = { 
			"left": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RailRegion', 'Left.png')), (screenSize[1]//10, screenSize[1]//10)),
			"left_alarm": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RailRegion', 'Left_Alarm.png')), (screenSize[1]//10, screenSize[1]//10)),
			"middle": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RailRegion', 'Middle.png')), (screenSize[1]//10, screenSize[1]//10)),
			"right": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RailRegion', 'Right.png')), (screenSize[1]//10, screenSize[1]//10)),
			"right_alarm": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'tiles', 'RailRegion', 'Right_Alarm.png')), (screenSize[1]//10, screenSize[1]//10))
		}

		# Asset Loading - Entities 
		CarEntity.entityAssets = [[pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'right', '0.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'right', '1.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'right', '2.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'right', '3.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'right', '3.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'right', '4.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'right', '5.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'right', '6.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'right', '7.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10))], [pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'left', '0.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'left', '1.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'left', '2.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'left', '3.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'left', '4.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'left', '5.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'left', '6.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10)) ,pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'cars', 'left', '7.png')).convert_alpha(), (screenSize[1]//10, screenSize[1]//10))]]	
		TractorEntity.entityAssets = [[pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'tractor', 'right', '0.png')).convert_alpha(), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'tractor', 'right', '1.png')).convert_alpha(), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'tractor', 'right', '2.png')).convert_alpha(), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'tractor', 'right', '3.png')).convert_alpha(), (screenSize[1]//5, screenSize[1]//10))], [pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'tractor', 'left', '0.png')).convert_alpha(), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'tractor', 'left', '1.png')).convert_alpha(), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'tractor', 'left', '2.png')).convert_alpha(), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'tractor', 'left', '3.png')).convert_alpha(), (screenSize[1]//5, screenSize[1]//10))]]
		TrainEntity.entityAssets = [[pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'rail', 'right', '0.png')), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'rail', 'right', '1.png')), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'rail', 'right', '2.png')), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'rail', 'right', '3.png')), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'rail', 'right', '4.png')), (screenSize[1]//5, screenSize[1]//10))], [pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'rail', 'left', '0.png')), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'rail', 'left', '1.png')), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'rail', 'left', '2.png')), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'rail', 'left', '3.png')), (screenSize[1]//5, screenSize[1]//10)), pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'rail', 'left', '4.png')), (screenSize[1]//5, screenSize[1]//10))]]
		LogEntity.entityAssets = { 
			"F1": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'logs', 'F1.png')), (screenSize[1]//10, screenSize[1]//10)).convert_alpha(),
			"F2": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'logs', 'F2.png')), (screenSize[1]//10, screenSize[1]//10)).convert_alpha(),
			"T1": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'logs', 'T1.png')), (screenSize[1]//10, screenSize[1]//10)).convert_alpha(),
			"T2": pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'logs', 'T2.png')), (screenSize[1]//10, screenSize[1]//10)).convert_alpha()
		}

	def handleInput(self, e):
		if e.type == pygame.KEYDOWN: 
			if (e.key == pygame.K_UP or e.key == pygame.K_w) and self.player.alive == True: 
				if not self.player.pendingMove == None: 
					self.player.position = self.player.pendingMove
					self.player.pendingMove = None

				self.player.position[1] -= (screenSize[1]//20)
				self.player.state = "forwards_jump1"
				self.player.animationTimer = 5

				self.player.pendingMove = self.player.position 
				self.player.pendingMove[1] -= (screenSize[1]//20)
				
				if  self.player.pendingMove[1] < (screenSize[1]//10)*7:
					self.player.score += 1 
					self.map.pop(0)
					self.player.pendingMove[1] += (screenSize[1]//20)*2
				elif self.player.score < 4: 
					self.player.score += 1 


				
			elif (e.key == pygame.K_LEFT or e.key == pygame.K_a) and self.player.alive == True:
				if not (self.player.position[0] - (screenSize[1]//10) <= 0):
					if not self.player.pendingMove == None: 
						self.player.position = self.player.pendingMove
						self.player.pendingMove = None   

					self.player.position[0] -= (screenSize[1]//20)
					self.player.state = "left_jump1"
					self.player.animationTimer = 5

					self.player.pendingMove = self.player.position 
					self.player.pendingMove[0] -= (screenSize[1]//20)




			elif (e.key == pygame.K_DOWN or e.key == pygame.K_s) and self.player.alive == True:
				if not (self.player.position[1] + (screenSize[1]//10) >= screenSize[1]):
					if not self.player.pendingMove == None: 
						self.player.position = self.player.pendingMove
						self.player.pendingMove = None 

					self.player.position[1] += (screenSize[1]//20)
					self.player.state = "backwards_jump1"
					self.player.animationTimer = 5

					self.player.pendingMove = self.player.position 
					self.player.pendingMove[1] += (screenSize[1]//20)


			elif (e.key == pygame.K_RIGHT or e.key == pygame.K_d) and self.player.alive == True:
				if not (self.player.position[0] + (screenSize[1]//10) > screenSize[0]):
					if not self.player.pendingMove == None: 
						self.player.position = self.player.pendingMove
						self.player.pendingMove = None   

					self.player.position[0] += (screenSize[1]//20)
					self.player.state = "right_jump1"
					self.player.animationTimer = 5

					self.player.pendingMove = self.player.position 
					self.player.pendingMove[0] += (screenSize[1]//20)

	def updateScreen(self):
		self.player.update()
		if len(self.map) < 12: self.generateRegions(self.map)
		for regionNum in range(len(self.map)): self.map[regionNum].updateRegion(regionNum, self.player)

		playerPosition = self.player.getRow()
		if isinstance(playerPosition, int): 
			if isinstance(self.map[playerPosition], WaterRegion): 
				if self.map[playerPosition].checkWaterDeath(self.player): 
					self.player.dead()		 

		if self.player.state == "forwards_jump1" and self.player.animationTimer == 0:
			self.player.position = self.player.pendingMove
			self.player.pendingMove = None 
			self.player.state = "forwards_jump2"
			self.player.animationTimer = 5

		elif self.player.state == "left_jump1" and self.player.animationTimer == 0:
			self.player.position = self.player.pendingMove
			self.player.pendingMove = None 
			self.player.state = "left_jump2"
			self.player.animationTimer = 5

		elif self.player.state == "right_jump1" and self.player.animationTimer == 0:
			self.player.position = self.player.pendingMove
			self.player.pendingMove = None 
			self.player.state = "right_jump2"
			self.player.animationTimer = 5
			
		elif self.player.state == "backwards_jump1" and self.player.animationTimer == 0:
			self.player.position = self.player.pendingMove
			self.player.pendingMove = None 
			self.player.state = "backwards_jump2"
			self.player.animationTimer = 5
		
		# Others
		elif self.player.state == "forwards_jump2" and self.player.animationTimer == 0: 
			self.player.state = "forwards"
		elif self.player.state == "left_jump2" and self.player.animationTimer == 0: 
			self.player.state = "left"
		elif self.player.state == "right_jump2" and self.player.animationTimer == 0: 
			self.player.state = "right"
		elif self.player.state == "backwards_jump2" and self.player.animationTimer == 0: 
			self.player.state = "backwards"
		

		
		if self.player.lives < 1: self.gameOver = True  

		if self.player.animationTimer > 0: self.player.animationTimer -= 1 
		FreePlay_GameScreen.timer += 1 
		if self.gameOver and self.fade < 125: self.fade += 5
		elif self.fade > 0: self.fade -= 10
		
	def drawScreen(self, screen): 
		screen.fill((0,0,0))
		# for region in self.map: region.drawRegion(screenSize[0] // (screenSize[1]//10))

		for regionNum in range(len(self.map)): self.map[regionNum].drawRegion(regionNum)
		self.player.draw()

		if self.gameOver or self.fade > 0: 
			s = pygame.Surface((screenSize[0], screenSize[1]))  # the size of your rect
			s.set_alpha(self.fade)                # alpha level
			s.fill((0,0,0))
			screen.blit(s, (0,0))  

		topBar = pygame.Surface((screenSize[0], screenSize[1]//10))  # the size of your rect
		topBar.set_alpha(75)                # alpha level
		topBar.fill((0,0,0))
		screen.blit(topBar, (0,0))  

		scoreText = courierTitleFont.render("Score " + str(self.player.score), True, (255, 255, 255))
		screen.blit(scoreText, scoreText.get_rect(center=(screenSize[0]//2, screenSize[1]//20))) 

	def generateRegions(self, map): # Previous tile based generation
		chance = random.randint(0, 100)
		if len(map) == 0:
			map += SafeRegion.spawnRegion(self.mapDimensions[0])
			map += SafeRegion.spawnRegion(self.mapDimensions[0])
		
		elif isinstance(map[len(map)-2], SafeRegion): # Last region was Safe 
			if chance < 25: map += WaterRegion.spawnRegion(self.mapDimensions[0])
			elif chance < 65: map += RoadRegion.spawnRegion(self.mapDimensions[0])
			elif chance < 85: map += RailRegion.spawnRegion(self.mapDimensions[0])
			elif chance < 95: map += TractorRegion.spawnRegion(self.mapDimensions[0])
			else: map += SafeRegion.spawnRegion(self.mapDimensions[0])

		elif isinstance(map[len(map)-2], RoadRegion): # Last region was Road
			if chance < 30: map += WaterRegion.spawnRegion(self.mapDimensions[0])
			# elif chance < 45: map += RoadRegion.spawnRegion(self.mapDimensions[0]) # 0% chance 
			elif chance < 50: map += RailRegion.spawnRegion(self.mapDimensions[0])
			elif chance < 80: map += TractorRegion.spawnRegion(self.mapDimensions[0])
			else: map += SafeRegion.spawnRegion(self.mapDimensions[0])

		elif isinstance(map[len(map)-2], TractorRegion): # Last region was Tractor
			if chance < 30: map += WaterRegion.spawnRegion(self.mapDimensions[0])
			# elif chance < 45: map += RoadRegion.spawnRegion(self.mapDimensions[0]) # 0% chance 
			elif chance < 50: map += RailRegion.spawnRegion(self.mapDimensions[0])
			else: map += SafeRegion.spawnRegion(self.mapDimensions[0])

		elif isinstance(map[len(map)-2], RailRegion): # Last region was Rail 
			if chance < 25: map += WaterRegion.spawnRegion(self.mapDimensions[0])
			elif chance < 50: map += RoadRegion.spawnRegion(self.mapDimensions[0])
			# elif chance < 45: map += RailRegion.spawnRegion(self.mapDimensions[0]) # 0% chance 
			elif chance < 80: map += TractorRegion.spawnRegion(self.mapDimensions[0])
			else: map += SafeRegion.spawnRegion(self.mapDimensions[0])

		elif isinstance(map[len(map)-2], WaterRegion): # Last region was Water 
			# if chance < 45: map += WaterRegion.spawnRegion(self.mapDimensions[0]) # 0% chance 
			if chance < 35: map += RoadRegion.spawnRegion(self.mapDimensions[0])
			elif chance < 50: map += RailRegion.spawnRegion(self.mapDimensions[0])
			elif chance < 80: map += TractorRegion.spawnRegion(self.mapDimensions[0])
			else: map += SafeRegion.spawnRegion(self.mapDimensions[0])
	
	

	def nextScreen(self):
		if self.gameOver == True and self.fade >= 125:
			multiplier = (random.randint(0, 100) / 100) + 1 
			gameCoins = round(self.player.score * multiplier)

			if self.playerData[2] < self.player.score: 
				database.updatePlayer(self.currentPlayer, "highScoreUpdate", self.player.score)
			database.updatePlayer(self.currentPlayer, "totalScoreIncrement", self.player.score)
			database.updatePlayer(self.currentPlayer, "totalGamesIncrement", 1)
			database.updatePlayer(self.currentPlayer, "coinsAddition", gameCoins)
			
			return GameOverScreen(gameCoins, self.currentPlayer)
		elif self.pause == True: 
			self.pause = False 
			return PausedScreen(self)
		return self 

class Progressive_GameScreen(AbstractScreen): 
	def updateScreen(self): 
		pass 

	def drawScreen(self, screen):
		pass
	
	def handleInput(self, e):
		pass

	def nextScreen(self):
		return self

class StartScreen(AbstractScreen): 
	def __init__(self, currentPlayer=""): 

		# Change screen states
		self.FreePlay_GameStart = False
		self.Progressive_GameStart = False
		self.skinsScreen = False 
		self.statsScreen = False 

		# Button locations
		self.buttons = []
		self.FPBtn_colour = (255, 255, 255)
		self.PBtn_colour = (255, 255, 255)
		self.skinsBtn_colour = (255, 255, 255)
		self.statsBtn_colour = (255, 255, 255)

		self.userInput_colour = (255, 255, 255)
		self.userInput_colour_count = 255
		
		if currentPlayer == "": 
			self.userInput = "Enter Username"
		else: self.userInput = currentPlayer

	def handleInput(self, event):
		if event.type == pygame.KEYDOWN:
				if self.userInput == "Enter Username": # Reset the username box 
					self.userInput = ""
				
				if event.unicode.isalpha():
					self.userInput += e.unicode
				elif event.key == pygame.K_BACKSPACE:
						self.userInput = self.userInput[:-1]
		if event.type == pygame.MOUSEBUTTONDOWN: 
			if pygame.mouse.get_pressed() == (1, 0, 0): #LMB
				i = 0
				while i < len(self.buttons):
					if self.buttons[i].collidepoint(pygame.mouse.get_pos()): 
						if i == 0: self.FreePlay_GameStart = True
						elif i == 1: self.Progressive_GameStart = False # Hard coded off - not added yet 
						elif i == 2: self.skinsScreen = True 
						elif i == 3: self.statsScreen = True
					i += 1
	
	def updateScreen(self):
		self.FPBtn_colour = (255, 255, 255)
		self.PBtn_colour = (255, 255, 255)
		self.skinsBtn_colour = (255, 255, 255)
		self.statsBtn_colour = (255, 255, 255)

		i = 0 
		while i < len(self.buttons):
			if self.buttons[i].collidepoint(pygame.mouse.get_pos()):
				if i == 0: self.FPBtn_colour = (175, 175, 175)
				elif i == 1: self.PBtn_colour = (175, 175, 175)
				elif i == 2: self.skinsBtn_colour = (175, 175, 175)
				elif i == 3: self.statsBtn_colour = (175, 175, 175)
			i += 1

							
	def drawScreen(self, screen):
		screen.fill((0, 0, 0)) 
		segmentSize = screenSize[1]//10

		titleText = courierTitleFont.render("Frogger", True, (255, 255, 255))
		screen.blit(titleText, titleText.get_rect(center=(segmentSize * 5, segmentSize * 1)))
		usernameText = courierSubFont.render("Username: " + self.userInput, True, (self.userInput_colour))
		screen.blit(usernameText, usernameText.get_rect(center=(segmentSize * 5, segmentSize * 2)))

		FreePlay_StartButton = fixedsysSubFont.render("Free Play", True, self.FPBtn_colour)
		FPBtn = (screen.blit(FreePlay_StartButton, FreePlay_StartButton.get_rect(center=(segmentSize * 2, segmentSize * 4))))
		Progressive_StartButton = fixedsysSubFont.render("Progressive", True, self.PBtn_colour)
		PBtn = (screen.blit(Progressive_StartButton, Progressive_StartButton.get_rect(center=(segmentSize * 8, segmentSize * 4))))
		skinsButton = fixedsysSubFont.render("Skins", True, self.skinsBtn_colour)
		skinsBtn = (screen.blit(skinsButton, skinsButton.get_rect(center=(segmentSize * 2, segmentSize * 6))))
		statsButton = fixedsysSubFont.render("Statistics", True, self.statsBtn_colour)
		statsBtn = (screen.blit(statsButton, statsButton.get_rect(center=(segmentSize * 8, segmentSize * 6)))) 
		
		if len(self.buttons) < 4: 
			self.buttons.append(FPBtn)
			self.buttons.append(PBtn)
			self.buttons.append(skinsBtn)
			self.buttons.append(statsBtn)
		
		if self.userInput_colour_count < 255:
			self.userInput_colour = (255, self.userInput_colour_count, self.userInput_colour_count)
			self.userInput_colour_count += 10

		if self.FreePlay_GameStart == True and (self.userInput != "" and self.userInput != "Enter Username") and not fullScreen: screen = pygame.display.set_mode((screenSize[0], screenSize[1])) # Does not allow resizing during gameplay

	def nextScreen(self):
		if (self.FreePlay_GameStart or self.Progressive_GameStart or self.skinsScreen or self.statsScreen): 
			if (self.userInput != "" and self.userInput != "Enter Username"):
				currentPlayer = self.userInput.lower()
				database.initiatePlayer(currentPlayer)

				if self.FreePlay_GameStart == True: return FreePlay_GameScreen(currentPlayer)
				# elif self.Progressive_GameStart == True: return Progressive_GameScreen()
				elif self.Progressive_GameStart == True: return self
				elif self.skinsScreen == True: return skinsScreen(currentPlayer)
				elif self.statsScreen == True: return statsScreen(currentPlayer)
			else:
				self.userInput_colour = (255, 0, 0)
				self.userInput_colour_count	= 0

				self.FreePlay_GameStart = False
				self.Progressive_GameStart = False
				self.skinsScreen = False 
				self.statsScreen = False 	
				
		return self  

class skinsScreen(AbstractScreen): 
	def __init__(self, currentPlayer=""): 

		# Change screen states
		self.mainScreen = False 
		self.currentPlayer = currentPlayer

		self.skins = []
		self.coins = database.getPlayerCoins(currentPlayer)
		self.currentSkin = database.getCurrentSkin(currentPlayer)
		
		self.balance_colour = (255, 255, 255)
		self.balance_colour_count = 255

		# Button locations
		self.skins.append(["default", True, None])
		for skin in database.getSkins():
			if skin[0] != "default": 
				if database.checkSkinAccess(currentPlayer, skin[0]): 
					self.skins.append([skin[0], True, None])
				else: 
					self.skins.append([skin[0], False, database.fetchSkinCost(skin[0])])

		self.assets = []
		for skin in self.skins: 
			self.assets.append(pygame.transform.scale(pygame.image.load(os.path.join(assets_path,'entities', 'frog', skin[0], 'forwards.png')).convert_alpha(), (screenSize[1]//5, screenSize[1]//5)))

		self.buttons = []

	def handleInput(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_BACKSLASH or event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN: 
				self.mainScreen = True 
		if event.type == pygame.MOUSEBUTTONDOWN: 
			if pygame.mouse.get_pressed() == (1, 0, 0): #LMB
				i = 0
				while i < len(self.buttons)-1:
					if self.buttons[i].collidepoint(pygame.mouse.get_pos()): 
						if self.skins[i][1] == True:
							database.updatePlayer(self.currentPlayer, "currentSkin", self.skins[i][0])
							self.currentSkin = self.skins[i][0]

						elif self.coins >= self.skins[i][2]: 
							print(self.skins[i])
							database.unlockSkin(self.currentPlayer, self.skins[i][0])
							database.updatePlayer(self.currentPlayer, "currentSkin", self.skins[i][0])
							database.updatePlayer(self.currentPlayer, "coinsSubtraction", self.skins[i][2])
							self.currentSkin = self.skins[i][0]
							self.coins -= self.skins[i][2]
							self.skins[i][2] = None
							self.skins[i][1] = True
						
						else:
							self.balance_colour = (255, 0, 0)
							self.balance_colour_count = 0

						
					i += 1
	
	def updateScreen(self):
		if self.balance_colour_count < 255:
			self.balance_colour = (255, self.balance_colour_count, self.balance_colour_count)
			self.balance_colour_count += 10

				
	def drawScreen(self, screen):
		screen.fill((0, 0, 0)) 
		segmentSize = screenSize[1]//5

		titleText = courierTitleFont.render("Skins", True, (255, 255, 255))
		screen.blit(titleText, titleText.get_rect(center=(segmentSize * 2.5, segmentSize * 0.5)))
		balanceText = courierSubFont.render("Balance: " + str(self.coins), True, self.balance_colour)
		screen.blit(balanceText, balanceText.get_rect(center=(segmentSize * 2.5, segmentSize * 0.75)))

		for skin in range(0, len(self.skins)):
			x = (skin % 3) * segmentSize
			y = (skin // 3) * segmentSize
			button = screen.blit(self.assets[skin], (x + segmentSize, y + segmentSize))
			if not self.skins[skin][1]: 
				costText = courierSubFont.render(str(self.skins[skin][2]), True, (255, 255, 255))
				screen.blit(costText, costText.get_rect(center=(x + segmentSize*1.5, y + segmentSize*2)))

			if len(self.buttons) < len(self.skins) + 1:
				self.buttons.append(button)

	def nextScreen(self):
		if self.mainScreen == True: return StartScreen(self.currentPlayer)
		
		return self  

class skinsCrate(AbstractScreen): 
	def updateScreen(self): 
		pass 

	def drawScreen(self, screen):
		pass
	
	def handleInput(self, e):
		pass

	def nextScreen(self):
		return self

class statsScreen(AbstractScreen): 
	def __init__(self, currentPlayer=""): 
		self.currentPlayer = currentPlayer
		self.playerData = database.loadPlayer(currentPlayer)
		self.mainScreen = False

	def updateScreen(self): 
		pass 

	def drawScreen(self, screen):
		screen.fill((0, 0, 0))
		segmentSize = screenSize[1]//5

		titleText = courierTitleFont.render("Stats", True, (255, 255, 255))
		screen.blit(titleText, titleText.get_rect(center=(segmentSize * 2.5, segmentSize * 0.5)))

		totalScoreText = courierSubFont.render("Total Score: " + str(self.playerData[1]), True, (255, 255, 255))
		screen.blit(totalScoreText, totalScoreText.get_rect(center=(segmentSize * 2.5, segmentSize * 0.75)))
		highScoreText = courierSubFont.render("High Score: " + str(self.playerData[2]), True, (255, 255, 255))
		screen.blit(highScoreText, highScoreText.get_rect(center=(segmentSize * 2.5, segmentSize * 1)))
		coinsText = courierSubFont.render("Coins: " + str(self.playerData[4]), True, (255, 255, 255))
		screen.blit(coinsText, coinsText.get_rect(center=(segmentSize * 2.5, segmentSize * 1.25)))
		totalGamesText = courierSubFont.render("Total Games: " + str(self.playerData[5]), True, (255, 255, 255))
		screen.blit(totalGamesText, totalGamesText.get_rect(center=(segmentSize * 2.5, segmentSize * 1.5)))

	def handleInput(self, e):
		if e.type == pygame.KEYDOWN:
			if e.key == pygame.K_BACKSLASH or e.key == pygame.K_ESCAPE or e.key == pygame.K_RETURN: 
				self.mainScreen = True

	def nextScreen(self):
		if self.mainScreen == True: return StartScreen(self.currentPlayer)
		return self

endProgram = False
currentScreen = StartScreen()

fullScreen = False
resizeHeight = False

database = DatabaseHandler()

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

database.closeConnection()
pygame.quit()
quit()