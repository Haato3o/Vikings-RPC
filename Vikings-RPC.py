import json
import pypresence
import os
import time
import psutil

client = '530154230913433622'

supportedDungeons = [
'forgotten_isle', 
'utgard', 
'trial_of_gods', 
'jotan_fortress_camp',
'imperial_watchtowers',
'fjord',
'stone_circle',
'simul-s_lair',
'castra_ignis',
'ragged_dunes',
'dvergheim_blues'
]

class presence:
    def __init__(self):
        self.rpc = pypresence.Presence(client)
        self.connected = False
    
    def start(self):
        if self.connected == False:
            self.rpc.connect()
            print('Rich presence initialized!')
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
        self.location = None            # Player location
        self.lastLoc = None             # Player last location
        self.difficulty = None          # Game difficulty
        self.slot = None                # Char slot user is playing on
        self.isNewGamePlus = None       # Is new game+?
        self.saveToRead = None          # Latest game save
        self.gamePID = None             # Game PID
        self.playerIsInStance = False   # Checks if player is in main city or in a dungeon
        self.timer = None

    def stop(self):
        self.dRichPresence.stop()

    def init(self):
        bLoop = False
        bLooper = False
        while True:
            self.detectPid()
            if self.gamePID != None:
                if bLooper == False:
                    print('Initializing rich presence...')
                    bLoop = False
                    bLooper = True
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
                    bLooper = False
                time.sleep(10)

    def updatePresence(self):
        if self.lastLoc != self.location:
            self.timer = int(time.time())
            self.lastLoc = self.location
        if self.playerIsInStance:
            stance = self.locationFormatter(self.location)
            if self.location in supportedDungeons:
                lgImage = self.location
            else:
                print(f'Location: {self.location} not supported yet!')
                lgImage = 'dungeon'
        else:
            if self.location == 'trial_of_gods':
                stance = self.locationFormatter(self.location)
                lgImage = self.location
            else:
                stance = self.locationFormatter(self.location)
                lgImage = 'castraignis'
        
        self.dRichPresence.update(
            start = self.timer,
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
        self.location = self.getLocation(n)
        
    
    def locationFormatter(self, location):
        blacklist =  '0123456789'
        for c in blacklist:
            location = location.replace(c, '')
        result = location.replace('_', ' ').replace('-', '\'').title()
        for letter in range(len(result)-1):
            if result[letter] == '\'' and result[letter+1].isupper():
                result = result.replace(result[letter+1], result[letter+1].lower())
        result = list(result)
        if result[0].islower():
            result[0] = result[0].upper()
        return ''.join(result)

    def getLocation(self, save):
        epochTimes = {}
        epochTimesList = []
        for lSave in save['snapshots']:
            epochTimes[lSave['saveTime']] = lSave['sceneName']
            epochTimesList.append(lSave['saveTime'])
        epochTimesList.sort(reverse=True)
        if epochTimes[epochTimesList[0]].startswith('trial_'):
            return 'trial_of_gods'
        elif epochTimes[epochTimesList[0]] == 'simulslair':
            return "simul-s_lair"
        return epochTimes[epochTimesList[0]]

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
    try:
        rpc.init()
    except KeyboardInterrupt:
        rpc.stop()
        print('Exiting...')
