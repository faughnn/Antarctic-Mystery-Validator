from typing import Dict, List, Tuple
from models import Character, SceneEvidence, Dialogue


def check_everyone_appears(
    characters: Dict[str, Character],
    scene_evidence: List[SceneEvidence]
) -> Tuple[bool, str]:
    """Check that every character appears in at least one scene."""
    appeared_characters = set()

    for evidence in scene_evidence:
        appeared_characters.add(evidence.character_name)

    missing_characters = set(characters.keys()) - appeared_characters

    if missing_characters:
        details = f"These characters do not appear in any scenes: {', '.join(sorted(missing_characters))}"
        return (False, details)

    return (True, f"All {len(characters)} characters appear in at least one scene.")


def check_every_death_has_a_scene(
    characters: Dict[str, Character],
    scene_evidence: List[SceneEvidence]
) -> Tuple[bool, str]:
    """Check that every dead character has a valid death scene with evidence."""
    passed = True
    issues = []

    # Get all unique scene numbers
    scene_numbers = set(ev.scene_number for ev in scene_evidence)

    for character in characters.values():
        if character.is_dead():
            # Check if death scene number is valid
            if character.death_scene not in scene_numbers:
                issues.append(
                    f"{character.name} dies in scene {character.death_scene} but no evidence exists for that scene"
                )
                passed = False

            # Check if there's evidence marking them as dying in that scene
            death_evidence = [
                ev for ev in scene_evidence
                if ev.character_name == character.name and ev.dies_in_this_scene
            ]

            if not death_evidence:
                issues.append(
                    f"{character.name} is marked as dead but no scene evidence shows them dying"
                )
                passed = False
            elif death_evidence[0].scene_number != character.death_scene:
                issues.append(
                    f"{character.name} death scene mismatch: "
                    f"character.death_scene={character.death_scene} but "
                    f"evidence shows dying in scene {death_evidence[0].scene_number}"
                )
                passed = False

    if passed:
        dead_count = sum(1 for c in characters.values() if c.is_dead())
        return (True, f"All {dead_count} dead characters have valid death scenes.")

    return (False, "\n".join(issues))


def check_every_character_has_identifying_clues(
    characters: Dict[str, Character],
    scene_evidence: List[SceneEvidence]
) -> Tuple[bool, str]:
    """Check that every character has at least one identifying clue."""
    characters_without_clues = []

    for character_name in characters:
        # Get all evidence for this character
        char_evidence = [ev for ev in scene_evidence if ev.character_name == character_name]

        # Check if they have any identifying information
        has_clues = any(
            ev.uniform_visible or
            ev.holding_something_distinctive or
            ev.distinctive_features_visible or
            ev.body_position_relevant or
            ev.accent_audible or
            ev.name_mentioned_in_dialogue or
            ev.relationship_mentioned or
            ev.role_mentioned or
            ev.role_behaviour_visible or
            ev.spatial_relationship_visible or
            ev.environmental_context_relevant or
            ev.additional_visual_clues or
            ev.additional_dialogue_clues or
            ev.additional_contextual_clues
            for ev in char_evidence
        )

        if not has_clues:
            characters_without_clues.append(character_name)

    if characters_without_clues:
        details = (
            f"These characters have no identifying clues: "
            f"{', '.join(sorted(characters_without_clues))}"
        )
        return (False, details)

    return (True, f"All {len(characters)} characters have at least one identifying clue.")


def check_scenes_have_characters(
    scene_evidence: List[SceneEvidence]
) -> Tuple[bool, str]:
    """Check that each scene has at least one character."""
    scenes_by_number = {}

    for evidence in scene_evidence:
        if evidence.scene_number not in scenes_by_number:
            scenes_by_number[evidence.scene_number] = []
        scenes_by_number[evidence.scene_number].append(evidence.character_name)

    empty_scenes = [
        scene_num for scene_num, chars in scenes_by_number.items()
        if not chars
    ]

    if empty_scenes:
        return (False, f"These scenes have no characters: {', '.join(map(str, sorted(empty_scenes)))}")

    return (True, f"All {len(scenes_by_number)} scenes have at least one character.")


def check_dialogue_speakers_exist(
    characters: Dict[str, Character],
    dialogue: List[Dialogue]
) -> Tuple[bool, str]:
    """Check that all speakers in dialogue are valid characters."""
    invalid_speakers = set()
    empty_speaker_count = 0

    for line in dialogue:
        if not line.speaker.strip():
            empty_speaker_count += 1
        elif line.speaker not in characters:
            invalid_speakers.add(line.speaker)

    issues = []
    if empty_speaker_count > 0:
        issues.append(f"{empty_speaker_count} dialogue lines have empty/missing speakers")

    if invalid_speakers:
        issues.append(f"Unknown speakers: {', '.join(sorted(invalid_speakers))}")

    if issues:
        return (False, "\n".join(issues))

    unique_speakers = len(set(d.speaker for d in dialogue if d.speaker.strip()))
    return (True, f"All {unique_speakers} dialogue speakers are valid characters.")
