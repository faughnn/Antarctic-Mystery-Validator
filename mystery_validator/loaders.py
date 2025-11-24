import csv
from models import Character, Clue, Scene

def load_characters(file_path):
    items = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['id'] in items:
                print(f"Duplicate character ID found: {row['id']}")
            else:
                items[row['id']] = Character(row['id'], row['name'], row['role'], row['death_scene'], row['cause_of_death'], row['killer'])
    return items


def load_clues(file_path):
    items = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['id'] in items:
                print(f"Duplicate clue ID found: {row['id']}")
            else:
                items[row['id']] = Clue(row['id'], row['discovery_scene_id'], row['fate_aspect'], row['clue_type'], row['target_character'], row['description'], row['difficulty'], row['prerequisites'])
    return items


def load_scenes(file_path):
    items = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['id'] in items:
                print(f"Duplicate scene ID found: {row['id']}")
            else:
                items[row['id']] = Scene(row['id'], row['name'], row['timeline_day'], row['order_shown_to_player'], row[' characters_present'], row['characters_dead'], row['dialogue_speakers'], row[' clues'])
    return items