import os
import shutil
import struct
import fnmatch

import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

game_save_path = os.path.expandvars(r"%AppData%\Dominions6\savedgames")
backup_path = os.path.expandvars(r"%AppData%\Dom6_autosave\backup")

# return tuple of name of dir and its path
def get_save_dirs():
    content = os.listdir(game_save_path)
    return [(name, os.path.join(game_save_path, name)) for name in content if os.path.isdir(os.path.join(game_save_path, name))]

def get_backup_dirs():
    content = os.listdir(backup_path)
    return [(name, os.path.join(backup_path, name)) for name in content if os.path.isdir(os.path.join(backup_path, name))]

# name of dir and its path
game_save_list = get_save_dirs()
game_backup_list = get_backup_dirs()

def get_turn_number(filepath):
    
    if not os.path.exists(filepath):
        return None
        
    with open(filepath, "rb") as f:
        f.seek(14)
        
        chunk = f.read(2)
        
        return struct.unpack('<H', chunk)[0]


# save game turn
def save_turn(game_index):
    game_name = game_save_list[game_index][0]
    src_path = game_save_list[game_index][1]
    dst_path = os.path.join(backup_path, game_save_list[game_index][0])
    print(f"Saving {game_name}")
    
    # First find the directory for the game in backup folder, create if doesn't exist
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    
    # Copy over everything that is not trn or 2h. 
    shutil.copytree(src_path, dst_path, ignore = shutil.ignore_patterns('*.trn', '*.2h'), dirs_exist_ok = True)
    
    # Find the turn number
    # TURN_NUMBER=$(hexdump -n 2 -s 14 -e '1/2 "%d"' $TURN_FILE) This is the turn number in the trn file. 2 bytes at the 14th offset. 
    # @ben_sphynx told me about this on Reddit Dominions
    # Err if trn file or 2h doesn't exist
    
    turn_number = -1
    
    for file in os.listdir(src_path):
            if file.endswith('.trn'):
                # print whole path of files
                turn_number = get_turn_number(os.path.join(src_path, file))
                break
    
    if turn_number == -1:
        print('Reading turn number from trn file failed.')
        return
    
    # Copy the trn and 2h files into the turn specific folder 
    # Overwriting existing turn.
    
    # Copy the trn and 2h files into the turn specific folder 
    # Overwriting existing turn.
    print("1 Save name is current turn number")
    print("2 Enter save name")
    user_input = input()
    
    if not user_input.isdigit():
        print("Please input an interger")
        return
        
    user_input = int(user_input)
    if user_input == 1:    
        save_name = f"turn_{turn_number}"
    elif user_input == 2:
        save_name = input("Enter save name: ")
    else:
        print("Invalid save name.")
    
    save_path = os.path.join(dst_path, save_name)
    if save_name in os.listdir(dst_path):
        print("overwriting existing turn")
        shutil.rmtree(save_path)
        
    os.makedirs(save_path)
    
    for name in os.listdir(src_path):
        if name.endswith('.trn') or name.endswith('.2h'):
            shutil.copy2(os.path.join(src_path, name), 
                        os.path.join(save_path, name))
    return


# load game turn
def load_turn(game_index):
    game_name = game_backup_list[game_index][0]
    src_path = game_backup_list[game_index][1] 
    dst_path = os.path.join(game_save_path, game_name)
    
    print(f"Loading {game_name}")
    # Ask for save to load, print all the ones available
    saves = []
    for name in os.listdir(src_path):
        if os.path.isdir(os.path.join(src_path, name)):
            saves.append(name)
    
    for i in range(len(saves)):
        print(i, saves[i])
    
    user_input = input("Select save to load: ")
    if not user_input.isdigit():
        print("Please input an interger")
        return
    
    user_input = int(user_input)
    
    if game_name in os.listdir(game_save_path):
        print("overwriting existing turn")
        shutil.rmtree(dst_path)
        
    os.mkdir(dst_path)
    
    # copy over all the stuff in the folder
    for file in os.listdir(src_path):
        if not os.path.isdir(os.path.join(src_path, file)):
            shutil.copy2(os.path.join(src_path, file), 
                        os.path.join(dst_path, file))
    
    # copy over the 2h and trn file in the turn folder
    save_name = saves[user_input]
    save_path = os.path.join(src_path, save_name)
    for file in os.listdir(save_path):
        shutil.copy2(os.path.join(save_path, file), 
                        os.path.join(dst_path, file))
    
    return

def delete_backup_save(game_index):
    src_path = game_backup_list[game_index][1]
    saves = []
    for name in os.listdir(src_path):
        if os.path.isdir(os.path.join(src_path, name)):
            saves.append(name)
    
    for i in range(len(saves)):
        print(i, saves[i])
    
    user_input = input("Select save to delete: ")
    if not user_input.isdigit():
        print("Please input an interger")
        return
    
    user_input = int(user_input)
    shutil.rmtree(os.path.join(src_path, saves[user_input]))
    
    has_save = False
    for name in os.listdir(src_path):
        if os.path.isdir(os.path.join(src_path, name)):
            has_save = True
            return
    
    if not has_save:
        shutil.rmtree(src_path)

if __name__ == "__main__":

    if not os.path.exists(backup_path):
        os.makedirs(backup_path)
    
     
    
    while True:
    
        # Title
        print(r"""
    ________                   ________   _________                         
    \______ \   ____   _____  /  _____/  /   _____/____ ___  __ ___________ 
    |    |  \ /  _ \ /     \/   __  \   \_____  \\__  \\  \/ // __ \_  __ \
    |_   `   (  <_> )  Y Y  \  |__\  \  /        \/ __ \\   /\  ___/|  | \/
    /_______  /\____/|__|_|  /\_____  / /_______  (____  /\_/  \___  >__|   
            \/             \/       \/          \/     \/          \/                                                                                   
                                                                                                                                                            
                """)   
        
        game_list = get_save_dirs()
        game_backup_list = get_backup_dirs()

        print("0 Create backup save")
        print("1 Load backup save")
        print("2 Delete backup save")
        print("3 Exit")
        
        user_input = input("Select option: ")
        print("--------------------------------")
        if not user_input.isdigit():
            print("Please input an interger")
            continue
        
        user_input = int(user_input)
        if user_input not in range(0, 4):
            print("invalid input")
            continue
        
        #Save sequence
        
        if user_input == 0:
            for i in range(len(game_list)):
                print(i, game_list[i][0])
            
            user_input = input("Select game to save: ")
            if not user_input.isdigit():
                print("Please input an interger")
                continue
                
            user_input = int(user_input)
            if user_input not in range(0, len(game_list)):
                print("No such game")
                continue
            
            save_turn(user_input)
        
        # Load Sequence
        elif user_input == 1:
            for i in range(len(game_backup_list)):
                print(i, game_backup_list[i][0])
            
            user_input = input("Select game to load: ")
            if not user_input.isdigit():
                print("Please input an interger")
                continue
                
            user_input = int(user_input)
            if user_input not in range(0, len(game_backup_list)):
                print("No such game")
                continue

            load_turn(user_input)
        
        
        # Delete Save Sequence
        elif user_input == 2:
            game_backup_list = get_backup_dirs()
            for i in range(len(game_backup_list)):
                print(i, game_backup_list[i][0])
            
            user_input = input("Select game to delete backup save for: ")
            if not user_input.isdigit():
                print("Please input an interger")
                continue
                
            user_input = int(user_input)
            if user_input not in range(0, len(game_backup_list)):
                print("No such game")
                continue
            
            delete_backup_save(user_input)
        
        else: 
            exit()
        
        
    
    
    # TODO 
    # Log changes in folders, if the folder changed has different turn number that's not recorded, save the turn. 
    ################# Observe changes, autosave ######################
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s - %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S')

    # event_handler = LoggingEventHandler()

    # observer = Observer()
    # observer.schedule(event_handler, save_path, recursive = True)

    # observer.start()
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()
    # observer.join()
    