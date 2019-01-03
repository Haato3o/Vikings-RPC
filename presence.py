import json
from pypresence import Presence
import os
import time
import psutil

client = '530154230913433622'

class presence:
    def __init__(self):
        self.rpc = Presence(client)
        self.connected = False
    
    def start(self):
        if self.connected == False:
            self.rpc.connect()
            self.connected = True

    def stop(self):
        if self.connected:
            self.rpc.close()
            self.connected = False

    def update(self, **kwargs):
        self.rpc.update(**kwargs)

class richPresence:
    def __init__(self):
        self.dRichPresence = presence()
        self.saveFile = os.getenv('LOCALAPPDATA')+'Low\\Games Farm s_r_o_\\Vikings_ Wolves of Midgard\\saves\\'
        self.parsed = None              # Json characters save
        self.revision = None            # Game's revision
        self.parsedSave = None          # Json latest save
        self.level = None               # Char level
        self.name = None                # Char name
        self.god = None                 # Class
        self.location = None            # Will use it later
        self.difficulty = None          # Game difficulty
        self.slot = None                # Char slot user is playing on
        self.isNewGamePlus = None       # Is new game+?
        self.saveToRead = None          # Latest game save
        self.gamePID = None             # Game PID
        self.playerIsInStance = False   # Checks if player is in main city or in a dungeon

    def init(self):
        bLoop = False
        bLooper = False
        while True:
            self.detectPid()
            if self.gamePID == None:
                self.dRichPresence.start()
                self.readSave()
                self.getInfo()
                self.readGameSave()
                self.getMoreInfo()
                self.updatePresence()
                time.sleep(15)
            else:
                if bLoop == False:
                    print('Game PID not found. Try opening the game.')
                    self.dRichPresence.stop()
                    bLoop = True
                time.sleep(10)

    def updatePresence(self):
        if self.playerIsInStance:
            stance = 'In dungeon'
            lgImage = 'dungeon'
        else:
            stance = 'Castra Ignis'
            lgImage = 'castraignis'
        self.dRichPresence.update(
            large_image = lgImage,
            large_text = stance,
            small_image = self.god.lower(),
            small_text = f'{self.name} - Lvl {self.level}',
            state = 'Playing solo',
            party_size = [1, 1],
            details = f'Difficulty: {self.difficulty}'
        )

    def detectPid(self):
        for program in psutil.process_iter():
            if program.name() == 'vikings.exe':
                self.gamePID = program.pid
                return
            else:
                self.gamePID = None
            
    def readSave(self):
        f = open(self.saveFile+'slots_r24.sav', 'r')
        self.parsed = json.load(f)
        f.close()

    def readGameSave(self):
        f = open(self.saveFile+self.format_file(), 'r')
        self.parsedSave = json.load(f)
        f.close()

    def getInfo(self):
        self.slot = self.parsed['currentSlot']
        n = list(self.parsed['slots'])[self.slot]
        self.name = n['name']
        self.revision = self.parsed['revision']
        self.saveToRead = n['readSnapshotIndex']

    def getMoreInfo(self):
        self.god = self.parsedSave['playerStorage']['data'][4]['startingGod']
        self.level = self.parsedSave['playerStorage']['data'][2]['level']
        self.difficulty = self.parsedSave['playerStorage']['data'][0]['difficultyStor']
        if len(self.parsedSave['sceneStorage']['data'][1]['challenges']) > 0:
            self.playerIsInStance = True
        else:
            self.playerIsInStance = False

    def format_file(self):
        return f'game_r{self.revision}_s{self.slot}_c{self.saveToRead}.sav'

if __name__ == '__main__':
    rpc = richPresence()
    rpc.init()
