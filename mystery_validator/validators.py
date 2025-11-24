import json

def check_everyone_appears(characters, scenes):
    """Check that every character appears in at least one scene."""
    appeared_characters = set()
    passed = True
    details = ""
    for scene in scenes.values():
        character_list = json.loads(scene.characters_present)
        appeared_characters.update(character_list)
        
    missing_characters = set(characters.keys()) - appeared_characters
    if missing_characters:
        passed = False
        details = f"There characters do not appear in any scenes: {', '.join(missing_characters)}"

    return (passed, details)


def check_every_death_has_a_scene(characters, scenes):
    """Check that every character who is dead has a death scene and scene is valid."""
    passed = True
    details = ""
    for character in characters.values():
        if character.cause_of_death != "alive":
            if character.death_scene == None or character.death_scene == "":
                details += f"Character {character.name} is dead but has no death scene.\n"
                passed = False
            if character.death_scene not in scenes:
                details += f"Character {character.name} has a death scene {character.death_scene} that does not exist in scenes.\n"
                passed = False

    if passed:
        details += "All dead characters have a death scene.\n"

    return (passed, details)


def check_every_scene_has_at_least_one_character(scenes):
    """Check that every scene has at least one character present."""
    passed = True
    details = ""
    for scene in scenes.values():
        if scene.characters_present is None:
            details += f"Scene {scene.name} has no characters present.\n"
            passed = False

    if passed:
        details += "All scenes have at least one character present.\n"

    return (passed, details)