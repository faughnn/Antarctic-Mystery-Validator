"""Timeline consistency validators for Obra Dinn-style game logic."""

from typing import Dict, List, Tuple
from models import Character, SceneEvidence


def check_timeline_consistency(
    characters: Dict[str, Character],
    scene_evidence: List[SceneEvidence]
) -> Tuple[bool, str]:
    """Check for timeline inconsistencies - characters appearing after death (ghosts).

    Validates that:
    1. Dead characters don't appear in scenes after their death
    2. Killers are present in the death scene
    """
    issues = []

    for character in characters.values():
        if not character.is_dead():
            continue

        death_scene = character.death_scene

        # Find all scenes this character appears in
        char_appearances = [
            ev for ev in scene_evidence
            if ev.character_name == character.name
        ]

        # Check for appearances after death
        for ev in char_appearances:
            if ev.scene_number > death_scene and not ev.dies_in_this_scene:
                issues.append(
                    f"GHOST: {character.name} appears in scene {ev.scene_number} "
                    f"but died in scene {death_scene}"
                )

        # Check if killer was present at death scene
        if character.killer and character.killer != "Accident":
            killer_at_death_scene = any(
                ev.character_name == character.killer and ev.scene_number == death_scene
                for ev in scene_evidence
            )

            if not killer_at_death_scene and character.killer in characters:
                issues.append(
                    f"TIMELINE ERROR: {character.killer} killed {character.name} in scene {death_scene} "
                    f"but killer was not present in that scene"
                )

    if issues:
        return (False, "\n".join(issues))

    dead_count = sum(1 for c in characters.values() if c.is_dead())
    return (True, f"Timeline consistent for all {dead_count} deaths - no ghosts detected.")
