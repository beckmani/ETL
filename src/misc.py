import random


def roll_dice_for_corrupted_files(files_json):
    files = [{'file_name': f, 'corrupted': False} for f in files_json['Files']]
    files_json['Files'] = files
    if random.randint(0, 100) < 10:
        i = random.randint(0, len(files))
        print("Corrupted file in {0}".format(i))
        files_json['Files'][i]['corrupted'] = True
    return files_json