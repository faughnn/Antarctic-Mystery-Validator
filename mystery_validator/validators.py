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


# ============================================================================
# ANALYTICAL VALIDATORS (Obra Dinn-style game balance)
# ============================================================================

def analyze_clues_per_character(
    characters: Dict[str, Character],
    scene_evidence: List[SceneEvidence]
) -> Dict[str, Dict]:
    """Analyze how many identifying clues each character has.

    Uses percentile-based difficulty distribution for even buckets (~20% in each).

    Returns dict with character names as keys and analysis as values:
    {
        'character_name': {
            'total_clues': int,
            'clue_types': {
                'visual': int,
                'dialogue': int,
                'contextual': int,
                ...
            },
            'scenes_with_clues': int,
            'difficulty': str
        }
    }
    """
    analysis = {}
    all_clue_counts = []

    # First pass: count clues for each character
    for character_name in characters:
        char_evidence = [ev for ev in scene_evidence if ev.character_name == character_name]

        visual_clues = 0
        dialogue_clues = 0
        contextual_clues = 0
        relationship_clues = 0
        role_clues = 0
        scenes_with_clues = set()

        for ev in char_evidence:
            has_clue_in_scene = False

            # Visual clues
            if ev.uniform_visible:
                visual_clues += 1
                has_clue_in_scene = True
            if ev.holding_something_distinctive:
                visual_clues += 1
                has_clue_in_scene = True
            if ev.distinctive_features_visible:
                visual_clues += 1
                has_clue_in_scene = True
            if ev.body_position_relevant:
                visual_clues += 1
                has_clue_in_scene = True
            if ev.additional_visual_clues:
                visual_clues += 1
                has_clue_in_scene = True

            # Dialogue clues
            if ev.accent_audible:
                dialogue_clues += 1
                has_clue_in_scene = True
            if ev.name_mentioned_in_dialogue:
                dialogue_clues += 1
                has_clue_in_scene = True
            if ev.additional_dialogue_clues:
                dialogue_clues += 1
                has_clue_in_scene = True

            # Contextual clues
            if ev.environmental_context_relevant:
                contextual_clues += 1
                has_clue_in_scene = True
            if ev.spatial_relationship_visible:
                contextual_clues += 1
                has_clue_in_scene = True
            if ev.additional_contextual_clues:
                contextual_clues += 1
                has_clue_in_scene = True

            # Relationship clues
            if ev.relationship_mentioned:
                relationship_clues += 1
                has_clue_in_scene = True

            # Role clues
            if ev.role_mentioned:
                role_clues += 1
                has_clue_in_scene = True
            if ev.role_behaviour_visible:
                role_clues += 1
                has_clue_in_scene = True

            if has_clue_in_scene:
                scenes_with_clues.add(ev.scene_number)

        total_clues = visual_clues + dialogue_clues + contextual_clues + relationship_clues + role_clues

        analysis[character_name] = {
            'total_clues': total_clues,
            'clue_types': {
                'visual': visual_clues,
                'dialogue': dialogue_clues,
                'contextual': contextual_clues,
                'relationship': relationship_clues,
                'role': role_clues
            },
            'scenes_with_clues': len(scenes_with_clues),
            'difficulty': None  # Will be calculated in second pass
        }

        all_clue_counts.append(total_clues)

    # Calculate difficulty thresholds based on percentiles
    thresholds = _calculate_difficulty_thresholds(all_clue_counts)

    # Second pass: assign difficulty ratings
    for character_name in analysis:
        clue_count = analysis[character_name]['total_clues']
        analysis[character_name]['difficulty'] = _calculate_difficulty(clue_count, thresholds)

    return analysis


def _calculate_difficulty_thresholds(all_clue_counts: list[int]) -> dict:
    """Calculate difficulty thresholds based on quintiles for even distribution.

    Divides characters into 5 equal groups based on clue counts:
    - VERY HARD: Bottom 20% (fewest clues)
    - HARD: 20-40%
    - MEDIUM: 40-60%
    - EASY: 60-80%
    - VERY EASY: Top 20% (most clues)

    If characters have the same clue count, they go in the lower (harder) bucket.

    Returns dict with minimum clue count thresholds for each difficulty level.
    """
    sorted_counts = sorted(all_clue_counts)
    n = len(sorted_counts)

    # Calculate exact indices for quintile boundaries
    # For 60 characters: indices 12, 24, 36, 48 mark the boundaries
    # Each character at index i where indices[i] represents their clue count

    # We want to split into 5 groups as evenly as possible
    # Index 12 is the start of the 2nd quintile (HARD), etc.
    quintile_size = n // 5  # For 60 chars, this is 12

    # Boundary indices (start of each quintile after the first)
    idx_20 = quintile_size          # Index 12 for n=60
    idx_40 = quintile_size * 2      # Index 24 for n=60
    idx_60 = quintile_size * 3      # Index 36 for n=60
    idx_80 = quintile_size * 4      # Index 48 for n=60

    # Ensure indices are within bounds
    idx_20 = min(idx_20, n - 1)
    idx_40 = min(idx_40, n - 1)
    idx_60 = min(idx_60, n - 1)
    idx_80 = min(idx_80, n - 1)

    return {
        'hard_min': sorted_counts[idx_20],        # Need >= this for HARD
        'medium_min': sorted_counts[idx_40],      # Need >= this for MEDIUM
        'easy_min': sorted_counts[idx_60],        # Need >= this for EASY
        'very_easy_min': sorted_counts[idx_80],   # Need >= this for VERY EASY
    }


def _calculate_difficulty(clue_count: int, thresholds: dict) -> str:
    """Calculate character difficulty rating based on percentile thresholds.

    More clues = easier to identify (more information to work with)
    Fewer clues = harder to identify (must deduce with limited information)

    Uses percentile-based distribution for even buckets (~20% in each difficulty).
    Characters with same clue count go in the lower (harder) bucket.
    """
    # Check from easiest to hardest
    if clue_count >= thresholds['very_easy_min']:
        return "VERY EASY"
    elif clue_count >= thresholds['easy_min']:
        return "EASY"
    elif clue_count >= thresholds['medium_min']:
        return "MEDIUM"
    elif clue_count >= thresholds['hard_min']:
        return "HARD"
    else:
        return "VERY HARD"


def analyze_character_appearances(
    characters: Dict[str, Character],
    scene_evidence: List[SceneEvidence]
) -> Dict[str, int]:
    """Count how many scenes each character appears in.

    Returns dict with character names as keys and scene count as values.
    """
    appearances = {name: 0 for name in characters}

    for character_name in characters:
        char_scenes = set(
            ev.scene_number for ev in scene_evidence
            if ev.character_name == character_name
        )
        appearances[character_name] = len(char_scenes)

    return appearances


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


def analyze_character_difficulty(
    characters: Dict[str, Character],
    clue_analysis: Dict[str, Dict]
) -> Dict[str, List[str]]:
    """Group characters by difficulty rating.

    Returns dict with difficulty levels as keys and lists of character names as values.
    """
    by_difficulty = {
        'VERY EASY': [],
        'EASY': [],
        'MEDIUM': [],
        'HARD': [],
        'VERY HARD': []
    }

    for character_name, analysis in clue_analysis.items():
        difficulty = analysis['difficulty']
        by_difficulty[difficulty].append(character_name)

    return by_difficulty


def check_difficulty_balance(
    difficulty_groups: Dict[str, List[str]]
) -> Tuple[bool, str]:
    """Validate that difficulty distribution is reasonable.

    Game Goal: Players must identify WHO each character is, HOW they died, and WHO killed them.
    This requires deduction across multiple clues - single clues don't solve the puzzle.

    A balanced Obra Dinn-style game should have:
    - Some easy/very easy characters (entry points for players to get started)
    - Majority medium difficulty (bulk of the challenge)
    - Some hard characters (challenging deductions)
    - Very few "very hard" characters (edge cases, should be rare)
    """
    total = sum(len(chars) for chars in difficulty_groups.values())
    very_easy_count = len(difficulty_groups['VERY EASY'])
    easy_count = len(difficulty_groups['EASY'])
    medium_count = len(difficulty_groups['MEDIUM'])
    hard_count = len(difficulty_groups['HARD'])
    very_hard_count = len(difficulty_groups['VERY HARD'])

    issues = []
    warnings = []

    # Check for critical issues
    entry_points = very_easy_count + easy_count
    if entry_points == 0:
        issues.append("No EASY or VERY EASY characters - players will struggle to get started")

    if very_hard_count > total * 0.15:
        issues.append(
            f"{very_hard_count} VERY HARD characters ({very_hard_count/total*100:.0f}%) - "
            f"too many near-impossible characters"
        )

    # Check for warnings
    if entry_points < 5:
        warnings.append(
            f"Only {entry_points} easy entry points (VERY EASY + EASY) - "
            f"consider adding more for player onboarding"
        )

    if medium_count < total * 0.2:
        warnings.append(
            f"Only {medium_count} MEDIUM characters ({medium_count/total*100:.0f}%) - "
            f"consider adding more mid-difficulty challenges"
        )

    # Build report
    report_lines = [
        f"Difficulty distribution: VERY EASY={very_easy_count}, EASY={easy_count}, "
        f"MEDIUM={medium_count}, HARD={hard_count}, VERY HARD={very_hard_count}"
    ]

    if issues:
        report_lines.extend(issues)
    if warnings:
        report_lines.extend(warnings)

    passed = len(issues) == 0
    return (passed, "\n".join(report_lines))
