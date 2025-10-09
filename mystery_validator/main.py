import csv
import json
from models import Character
from loaders import load_characters, load_clues, load_scenes
from reports import generate_simple_report
import validators


characters = load_characters('mystery_validator\data\characters.csv')
clues = load_clues('mystery_validator\data\clues.csv')
scenes = load_scenes('mystery_validator\data\scenes.csv')

# for character in characters:
#     print("Character description: " + characters[character].get_description())
#     print("id:" + character + " - " + characters[character].name + " - " + characters[character].role + " - " + characters[character].death_scene + " - " + characters[character].cause_of_death + " - " + characters[character].killer)

# for clue in clues:
#     print("id:" + clue + " - Scene: " + clues[clue].discovery_scene_id + " - type: " + clues[clue].clue_type + " - target char: " + clues[clue].target_character + " - fate aspect: " + clues[clue].fate_aspect + " - Description: " + clues[clue].description + " - Difficulty: " + clues[clue].difficulty + " - prerequisites: " + clues[clue].prerequisites)

# for scene in scenes:
#     print("id:" + scene + " - " + scenes[scene].name + " - " + scenes[scene].timeline_day + " - " + scenes[scene].characters_present + " - Characters dead: " + scenes[scene].characters_dead + " - " + scenes[scene].dialogue_speakers)

validation_results = {
    "check_everyone_appears": validators.check_everyone_appears(characters, scenes),
    "check_every_death_has_a_scene": validators.check_every_death_has_a_scene(characters, scenes),
    "check_every_scene_has_at_least_one_character": validators.check_every_scene_has_at_least_one_character(scenes)
}


generate_simple_report(validation_results)

    
# 4. **Practice exercises:**
#    - Count how many characters died
#    - List all unique death causes
#    - Find which scene has the most deaths

# dead_characters = set()
# for scene in scenes:
#     dead_characters.update(scenes[scene]['characters_dead'].strip("[]").replace('"', '').replace("'", "").split(", "))

# print("dead characters: " + ", ".join(dead_characters))

# unique_death_causes = set()
# for character in characters:
#     if characters[character]['cause_of_death']:
#         unique_death_causes.add(characters[character]['cause_of_death'])

# print("unique death causes: " + ", ".join(unique_death_causes))

# death_counts = {}
# for scene in scenes:
#     dead_list = scenes[scene]['characters_dead'].strip("[]").replace('"', '').replace("'", "").split(", ")
#     death_counts[scene] = len([d for d in dead_list if d])
#     print(scene)
#     print(f"Scene {scenes[scene]['name']} has {death_counts[scene]} deaths")

# max_deaths_scene = max(death_counts, key=death_counts.get)
# print(f"Scene with most deaths: {scenes[max_deaths_scene]['name']} with {death_counts[max_deaths_scene]} deaths")