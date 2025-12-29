import os
import shutil
import struct
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

game_save_path = os.path.expandvars(r"%AppData%\Dominions6\savedgames")
backup_path = os.path.expandvars(r"%AppData%\Dom6_autosave\backup")


def get_save_dirs():
    content = os.listdir(game_save_path)
    return [(name, os.path.join(game_save_path, name))
            for name in content
            if os.path.isdir(os.path.join(game_save_path, name))]


def get_backup_dirs():
    content = os.listdir(backup_path)
    return [(name, os.path.join(backup_path, name))
            for name in content
            if os.path.isdir(os.path.join(backup_path, name))]


def get_turn_number(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as f:
        f.seek(14)
        chunk = f.read(2)
        return struct.unpack('<H', chunk)[0]


def save_turn(game_index):
    game_save_list = get_save_dirs()
    game_name = game_save_list[game_index][0]
    src_path = game_save_list[game_index][1]
    dst_path = os.path.join(backup_path, game_name)

    print(f"\nSaving: {game_name}\n")

    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
        shutil.copytree(
            src_path,
            dst_path,
            ignore=shutil.ignore_patterns('*.trn', '*.2h'),
            dirs_exist_ok=True
        )

    turn_number = -1
    for file in os.listdir(src_path):
        if file.endswith('.trn'):
            turn_number = get_turn_number(os.path.join(src_path, file))
            break

    if turn_number == -1:
        print("\nFailed to read turn number from .trn file\n")
        return

    print("Choose save naming option:")
    print("1 Use current turn number")
    print("2 Enter custom save name\n")

    user_input = input("Select option (1–2): ")
    print()

    if not user_input.isdigit():
        print("Invalid input\n")
        return

    user_input = int(user_input)

    if user_input == 1:
        save_name = f"turn_{turn_number}"
    elif user_input == 2:
        save_name = input("Enter custom save name: ")
        print()
    else:
        print("Invalid selection\n")
        return

    save_path = os.path.join(dst_path, save_name)

    if save_name in os.listdir(dst_path):
        shutil.rmtree(save_path)

    os.makedirs(save_path)

    for name in os.listdir(src_path):
        if name.endswith('.trn') or name.endswith('.2h'):
            shutil.copy2(
                os.path.join(src_path, name),
                os.path.join(save_path, name)
            )


class AutoSaveEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.src_path.endswith('.trn'):
            return

        time.sleep(2)

        src_path = os.path.dirname(event.src_path)
        game_name = os.path.basename(os.path.normpath(src_path))
        dst_path = os.path.join(backup_path, game_name)

        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
            shutil.copytree(
                src_path,
                dst_path,
                ignore=shutil.ignore_patterns('*.trn', '*.2h'),
                dirs_exist_ok=True
            )

        turn_number = -1
        for file in os.listdir(src_path):
            if file.endswith('.trn'):
                turn_number = get_turn_number(os.path.join(src_path, file))
                break

        if turn_number == -1:
            return

        save_name = f"turn_{turn_number}"
        save_path = os.path.join(dst_path, save_name)

        if save_name not in os.listdir(dst_path):
            os.makedirs(save_path)
            for name in os.listdir(src_path):
                if name.endswith('.trn') or name.endswith('.2h'):
                    shutil.copy2(
                        os.path.join(src_path, name),
                        os.path.join(save_path, name)
                    )


def load_turn(game_index):
    game_backup_list = get_backup_dirs()
    game_name = game_backup_list[game_index][0]
    src_path = game_backup_list[game_index][1]
    dst_path = os.path.join(game_save_path, game_name)

    print(f"\nLoading: {game_name}\n")

    saves = [d for d in os.listdir(src_path)
             if os.path.isdir(os.path.join(src_path, d))]

    for i in range(len(saves)):
        print(i, saves[i])
    print(len(saves), "Back")

    print()
    user_input = input("Select backup to load: ")
    print()

    if not user_input.isdigit():
        print("Invalid input\n")
        return

    user_input = int(user_input)
    if user_input == len(saves):
        return
    if user_input not in range(len(saves)):
        print("Invalid selection\n")
        return

    if game_name in os.listdir(game_save_path):
        shutil.rmtree(dst_path)

    os.mkdir(dst_path)

    for file in os.listdir(src_path):
        if not os.path.isdir(os.path.join(src_path, file)):
            shutil.copy2(
                os.path.join(src_path, file),
                os.path.join(dst_path, file)
            )

    save_path = os.path.join(src_path, saves[user_input])
    for file in os.listdir(save_path):
        shutil.copy2(
            os.path.join(save_path, file),
            os.path.join(dst_path, file)
        )


def delete_backup_save(game_index):
    game_backup_list = get_backup_dirs()
    src_path = game_backup_list[game_index][1]

    saves = [d for d in os.listdir(src_path)
             if os.path.isdir(os.path.join(src_path, d))]

    for i in range(len(saves)):
        print(i, saves[i])
    print(len(saves), "Back")

    print()
    user_input = input("Select backup to delete: ")
    print()

    if not user_input.isdigit():
        print("Invalid input\n")
        return

    user_input = int(user_input)
    if user_input == len(saves):
        return
    if user_input not in range(len(saves)):
        print("Invalid selection\n")
        return

    shutil.rmtree(os.path.join(src_path, saves[user_input]))

    if not any(os.path.isdir(os.path.join(src_path, d)) for d in os.listdir(src_path)):
        shutil.rmtree(src_path)


if __name__ == "__main__":
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)

    autosaving = False
    observer = None

    while True:
        print("""
________                   ________   _________
\\______ \\   ____   _____  /  _____/  /   _____/____ ___  __ ___________
 |    |  \\ /  _ \\ /     \\/   __  \\   \\_____  \\\\__  \\\\  \\/ // __ \\_  __ \\
 |_   `   (  <_> )  Y Y  \\  |__\\  \\  /        \\/ __ \\\\   /\\  ___/|  | \\/
/_______  /\\____/|__|_|  /\\_____  / /_______  (____  /\\_/  \\___  >__|
        \\/             \\/       \\/          \\/     \\/          \\/
""")

        game_list = get_save_dirs()
        game_backup_list = get_backup_dirs()

        print("Main menu:")
        print("0 Create backup")
        print("1 Load backup")
        print("2 Delete backup")
        print("3 Disable autosaving" if autosaving else "3 Enable autosaving")
        print("4 Exit\n")

        user_input = input("Select option (0–4): ")
        print("\n--------------------------------\n")

        if not user_input.isdigit():
            continue

        user_input = int(user_input)

        if user_input == 0:
            for i in range(len(game_list)):
                print(i, game_list[i][0])
            print(len(game_list), "Back")

            print()
            sel = input("Select game to back up: ")
            print()

            if not sel.isdigit():
                continue
            sel = int(sel)
            if sel == len(game_list):
                continue
            if sel not in range(len(game_list)):
                continue

            save_turn(sel)

        elif user_input == 1:
            for i in range(len(game_backup_list)):
                print(i, game_backup_list[i][0])
            print(len(game_backup_list), "Back")

            print()
            sel = input("Select game to load: ")
            print()

            if not sel.isdigit():
                continue
            sel = int(sel)
            if sel == len(game_backup_list):
                continue
            if sel not in range(len(game_backup_list)):
                continue

            load_turn(sel)

        elif user_input == 2:
            for i in range(len(game_backup_list)):
                print(i, game_backup_list[i][0])
            print(len(game_backup_list), "Back")

            print()
            sel = input("Select game to delete backups for: ")
            print()

            if not sel.isdigit():
                continue
            sel = int(sel)
            if sel == len(game_backup_list):
                continue
            if sel not in range(len(game_backup_list)):
                continue

            delete_backup_save(sel)

        elif user_input == 3:
            if not autosaving:
                autosaving = True
                handler = AutoSaveEventHandler()
                observer = Observer()
                observer.schedule(handler, game_save_path, recursive=True)
                observer.start()
            else:
                autosaving = False
                observer.stop()
                observer.join()
                observer = None

        elif user_input == 4:
            if observer:
                observer.stop()
                observer.join()
            break
