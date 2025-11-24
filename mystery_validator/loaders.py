import csv
from pathlib import Path
from typing import Dict, List
from models import Character, SceneEvidence, Dialogue


def _str_to_bool(value: str) -> bool:
    """Convert CSV string values to boolean."""
    return value.strip().upper() == 'TRUE'


def _str_to_optional(value: str) -> str | None:
    """Convert empty strings to None."""
    value = value.strip()
    return value if value else None


def _str_to_int(value: str) -> int | None:
    """Convert string to int, return None if empty or invalid."""
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def load_characters(file_path: str | Path) -> Dict[str, Character]:
    """Load characters from CSV file. Returns dict with character name as key."""
    characters = {}

    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row['characterName'].strip()

                if name in characters:
                    print(f"Warning: Duplicate character found: {name}")
                    continue

                characters[name] = Character(
                    name=name,
                    role=row['role'].strip(),
                    nationality=row['nationality'].strip(),
                    build=row['build'].strip(),
                    cause_of_death=_str_to_optional(row['causeOfDeath']),
                    killer=_str_to_optional(row['responsibleParty']),
                    death_scene=_str_to_int(row['deathSceneNumber'])
                )
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        raise
    except KeyError as e:
        print(f"Error: Missing expected column in characters CSV: {e}")
        raise

    return characters


def load_scene_evidence(file_path: str | Path) -> List[SceneEvidence]:
    """Load scene evidence/clues from CSV file."""
    evidence = []

    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                evidence.append(SceneEvidence(
                    character_name=row['characterName'].strip(),
                    scene_number=int(row['sceneNumber']),
                    dies_in_this_scene=_str_to_bool(row['diesInThisScene']),
                    uniform_visible=_str_to_bool(row['uniformVisible']),
                    holding_something_distinctive=_str_to_bool(row['holdingSomethingDistinctive']),
                    held_item_description=_str_to_optional(row['heldItemDescription']),
                    distinctive_features_visible=_str_to_bool(row['distinctiveFeaturesVisible']),
                    distinctive_features_description=_str_to_optional(row['distinctiveFeaturesDescription']),
                    body_position_relevant=_str_to_bool(row['bodyPositionRelevant']),
                    body_position_description=_str_to_optional(row['bodyPositionDescription']),
                    accent_audible=_str_to_bool(row['accentAudible']),
                    name_mentioned_in_dialogue=_str_to_bool(row['nameMentionedInDialogue']),
                    relationship_mentioned=_str_to_bool(row['relationshipMentioned']),
                    relationship_description=_str_to_optional(row['relationshipDescription']),
                    role_mentioned=_str_to_bool(row['roleMentioned']),
                    role_behaviour_visible=_str_to_bool(row['roleBehaviourVisible']),
                    spatial_relationship_visible=_str_to_bool(row['spatialRelationshipVisible']),
                    spatial_relationship_description=_str_to_optional(row['spatialRelationshipDescription']),
                    environmental_context_relevant=_str_to_bool(row['environmentalContextRelevant']),
                    environmental_context_description=_str_to_optional(row['environmentalContextDescription']),
                    additional_visual_clues=_str_to_optional(row['additionalVisualClues']),
                    additional_dialogue_clues=_str_to_optional(row['additionalDialogueClues']),
                    additional_contextual_clues=_str_to_optional(row['additionalContextualClues'])
                ))
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        raise
    except KeyError as e:
        print(f"Error: Missing expected column in scene evidence CSV: {e}")
        raise
    except ValueError as e:
        print(f"Error: Invalid data in scene evidence CSV: {e}")
        raise

    return evidence


def load_dialogue(file_path: str | Path) -> List[Dialogue]:
    """Load dialogue from CSV file."""
    dialogue = []

    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                dialogue.append(Dialogue(
                    scene_number=int(row['sceneNumber']),
                    line_number=int(row['lineNumber']),
                    speaker=row['speaker'].strip(),
                    text=row['text'].strip(),
                    display_time=_str_to_optional(row['displayTime'])
                ))
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        raise
    except KeyError as e:
        print(f"Error: Missing expected column in dialogue CSV: {e}")
        raise
    except ValueError as e:
        print(f"Error: Invalid data in dialogue CSV: {e}")
        raise

    return dialogue
