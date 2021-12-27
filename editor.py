import os, time, json
from termcolor import cprint
from terminaltables import SingleTable
from mutagen.mp3 import MP3

Error = []
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

def showSoundTable():    
    # print sound table
    sound_table_data = [['Name', 'Path']]
    for sound in config['sound'].keys():
        tbel = [sound, config['sound'][sound]]
        sound_table_data.append(tbel)
    print(SingleTable(sound_table_data, 'Sound Table').table)    
    print(f' Add new sound : add <sound-name> <sound-path>')
    print(f' Remove sound  : remove <sound-name>')
    cprint(f' *Caution: Remove sound will effect pattern and time relatively.', 'yellow')

def showPatternTable():
    # show sound for lookup
    asound_table_data = [['Name', 'Duration(sec)']]
    sound_num = len(config['sound'])
    for sound_key in config['sound'].keys():
        duration = MP3(config['sound'][sound_key]).info.length
        tbel = [sound_key, str('~' + str(round(duration, 2)))]
        asound_table_data.append(tbel)
    print(SingleTable(asound_table_data, f'Available sound({sound_num})').table)
    # print pattern table
    pattern_table_data = [['Name', 'Sound Chains', 'Duration(sec)']]
    for pattern in config['pattern'].keys():
        soundlist = ''
        duration = 0.0
        for sound in config['pattern'][pattern]:
            soundlist += ' ' + sound + ' '
            path = config['sound'][sound]
            duration += MP3(path).info.length        
        tbel = [pattern, soundlist, str('~' + str(round(duration, 2)))]
        pattern_table_data.append(tbel)
    print(SingleTable(pattern_table_data, 'Pattern Table').table)
    print(f' Add new pattern : add <pattern-name> <sound-chains>')
    print(f' Remove pattern  : remove <pattern-name>')    
    print(f'    example : add 6-call annouce/6am/get-class')
    cprint(f' *Caution: Remove sound will effect pattern and time relatively.', 'yellow')

def showTimeTable():
    pattern_table_data = [['Name', 'Duration(sec)']]
    pattern_num = len(config['pattern'])
    for pattern in config['pattern'].keys():
        duration = 0.0
        for sound in config['pattern'][pattern]:            
            path = config['sound'][sound]
            duration += MP3(path).info.length        
        tbel = [pattern, str('~' + str(round(duration, 2)))]
        pattern_table_data.append(tbel)
    print(SingleTable(pattern_table_data, f'Available pattern ({pattern_num})').table)
    # print time table
    time_table_data = [['Time', 'Pattern']]
    sorted_time = sorted(config['table'])
    for time in sorted_time:
        timedisp = time[0:2] + ':' + time[2:4]
        tbel = [timedisp, config['table'][time]]
        time_table_data.append(tbel)
    print(SingleTable(time_table_data, 'Time Table').table)
    print(f' Add new task : add <time HH:MM> <pattern-name>')
    print(f'    example : add 06:30 6-30-call')
    print(f' Remove task  : remove <time HH:MM>')    
    print(f'    example : remove 06:30')
    cprint(f' *Caution: Remove sound will effect pattern and time relatively.', 'yellow')

def tableSelection(topic):
    if topic == 'sound':
        showSoundTable()
    elif topic == 'pattern':
        showPatternTable()
    elif topic == 'time':
        showTimeTable()

def selectTopic(cl):
    if cl[0] == "select":
        if cl[1] == 'sound':
            return 'sound'
        elif cl[1] == 'pattern':
            return 'pattern'
        elif cl[1] == 'time':
            return 'time'
    else:
        return 'none'

def displayError():
    for err in Error:
        cprint(f' *{err}', 'yellow', 'on_red')

# sound
def addSound(name, path):
    if os.path.exists(path):
        if not "/" in name:
            if not name in config['sound'].keys():
                config['sound'].update({name:path})
            else:
                Error.append(f' {name} was used! pick another name')
        else:
            Error.append(f' name can not contains "/" ')
    else:
        Error.append(f' not found: {path}')
def removeSound(name):    
    pattern_to_remove, task_to_remove = relateToSound(name)
    cprint(f' *Removing sound "{name}" will effect to ', "red", "on_white")
    print(f'Patterns({len(pattern_to_remove)}) : {pattern_to_remove}')
    print(f'Task({len(task_to_remove)}) : {task_to_remove}')
    confirmation = input(f'Do you still want to remove this ?(y/n): ')
    if confirmation == 'y' or confirmation == "Y":
        for patt in pattern_to_remove:
            config['pattern'].pop(patt)
        for task in task_to_remove:
            config['table'].pop(task)
        config['sound'].pop(name)
    return
def relateToSound(name):
    relative_pattern = []
    # find pattern that relate to this sound
    for pattern_key in config['pattern'].keys():
        for sound in config['pattern'][pattern_key]:
            if sound == name:
                relative_pattern.append(pattern_key)
                break    
    relative_task = []
    for pattern_key in relative_pattern:
        relative_task += relateToPattern(pattern_key)
    # find task that relate to this sound    
    return relative_pattern, relative_task

# pattern
def addPattern(name, soundList):
    if name in config['pattern'].keys():
        Error.append(f'{name} was used! pick another name')
    else:
        print("not found")
        for sound in soundList:
            if not sound in config['sound'].keys():
                Error.append(f'{sound} was not exists')
                return
        config['pattern'].update({name:soundList})
    return
def removePattern(name):
    task_to_remove = relateToPattern(name)
    cprint(f' *Removing pattern "{name}" will effect to ', "red", "on_white")
    print(f'Task({len(task_to_remove)}) : {task_to_remove}')
    confirmation = input(f'Do you still want to remove this ?(y/n): ')
    if confirmation == 'y' or confirmation == "Y":
        for task in task_to_remove:
            config['table'].pop(task)
        config['pattern'].pop(name)
    return
def relateToPattern(name):
    relative_task = []
    # find task that relate to this pattern
    for task_key in config['table'].keys():
        if config['table'][task_key] == name:
            relative_task.append(task_key)
    return relative_task

# time or task
def addTask(time, pattern):
    # time = "HH:MM"
    if checktime(time) and pattern in config['pattern'].keys():
        h, m = time.split(':') 
        config['table'].update({str(h+m):pattern})
    else:
        Error.append(f'something wrong with your input')
def removeTask(time):
    if checktime(time):
        confirmation = input(f'Do you want to delete "{time}" (y/any): ')
        if confirmation == 'y' or confirmation == 'Y':
            h, m = time.split(":")
            config['table'].pop(str(h+m))
    else:
        Error.append("Wrong time format")
    return
def checktime(time):
    try:
        h, m = time.split(":")
        if len(h) != 2 or len(m) != 2:
            raise ValueError('Wrong time-format need to be HH:MM')
    except:
        Error.append(f'{ValueError}')
        return False
    h = int(h)
    m = int(m)
    if h >= 0 and h <= 23 and m >= 0 and m <= 59:
        return True
    else:
        return False

# save
def saveConfig():
    with open('config.json', 'w') as file:
        json.dump(config, file)

topic = 'none'
while True:
    os.system('clear')
    print("Pattern Autoplay v1 Commandline Editor")
    tableSelection(topic)
    displayError()
    Error=[]
    command = input(f'({topic}) < ')
    command_list = command.split()
    if len(command_list):
        if topic == 'none':
            topic = selectTopic(command_list)
        else:
            if command_list[0] == "exit":
                topic = 'none'
                command_list[0] = ''
            if topic == 'sound':
                if command_list[0] == 'add':
                    if len(command_list) == 3:
                        addSound(command_list[1], command_list[2])
                elif command_list[0] == 'remove':
                    if len(command_list) == 2:
                        removeSound(command_list[1])
            elif topic == 'pattern':
                if command_list[0] == 'add':
                    if len(command_list) == 3:
                        addPattern(command_list[1], command_list[2].split('/'))
                elif command_list[0] == 'remove':
                    if len(command_list) == 2:
                        removePattern(command_list[1])
            elif topic == 'time':
                if command_list[0] == 'add':
                    if len(command_list) == 3:
                        addTask(command_list[1], command_list[2])
                elif command_list[0] == 'remove':
                    if len(command_list) == 2:
                        removeTask(command_list[1])

        if command_list[0] == 'save':
            saveConfig()

        if command_list[0] == "exit":
            break    
   