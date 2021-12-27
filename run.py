import os, time, json
from termcolor import cprint
from terminaltables import SingleTable
from mutagen.mp3 import MP3
from playsound import playsound

# playsound('/home/moonman/Documents/Learning/python/00-simple-gui/sound/ann.mp3')
# playsound('/home/moonman/Documents/Learning/python/00-simple-gui/sound/ct.mp3')
# playsound('/home/moonman/Documents/Learning/python/00-simple-gui/sound/6.mp3')

def getTime(template):
    return time.strftime(template, time.localtime())

def findnext():    
    next = 0
    for i, key in enumerate(sorted_key):
        key = int(key)
        curr = int(getTime("%H%M"))
        if curr < key:
            next = i    
            break
    return next

def playpattern(pattern_name, config):
    soundlist = config["pattern"][pattern_name]
    for sound in soundlist:
        sound_path = config["sound"][sound]
        playsound(sound_path)


#== start == 
playsound('pattern-autoplay.mp3')
config = None 
if not os.path.exists('config.json'):
    with open('config.json', 'w') as file:
        config_init = {
            "sound": {},
            "pattern": {},
            "table": {}
        }
        json.dump(config_init, file)

with open('config.json', 'r') as file:
    config = json.load(file)   

#find next position of table according to current time
sorted_key = sorted(config["table"])
next = findnext()

while True:
    os.system('clear')    
    print(f'Pattern Autoplay v1 RTC [{getTime("%H:%M:%S")}]')
    if len(config['table']) == 0:
        cprint(f'No task in table please go to create some', 'yellow')
        time.sleep(1)
        continue
    table_data = [
        ['Status', 'Time(HHMM)', 'Pattern']
    ]
    for i, key in enumerate(sorted_key):
        if i == next:
            tbel = ['next', key, config["table"][key]]
        else:
            tbel = ['', key, config["table"][key]]
        table_data.append(tbel)
    print(SingleTable(table_data).table)

    # check time to play pattern
    if getTime("%H%M") == sorted_key[next]:#         
        pattern_name = config["table"][sorted_key[next]]
        playpattern(pattern_name, config)
        next = (next+1)%len(sorted_key)
    time.sleep(1)
