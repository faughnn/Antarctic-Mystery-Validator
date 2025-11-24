"""Game balance validators for Obra Dinn-style deduction games.

Ensures the game has good difficulty distribution, scene complexity, clue variety, etc.
"""

from typing import Dict, List, Tuple
from collections import Counter
from models import Character, SceneEvidence


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


def analyze_scene_complexity(
    scene_evidence: List[SceneEvidence]
) -> Dict[int, Dict]:
    """Analyze complexity of each scene (how many characters appear).

    Returns dict with scene numbers as keys and complexity info as values:
    {
        scene_number: {
            'character_count': int,
            'characters': list of names,
            'complexity_rating': str ('SIMPLE', 'BALANCED', 'COMPLEX', 'OVERWHELMING')
        }
    }
    """
    scenes = {}

    for evidence in scene_evidence:
        scene_num = evidence.scene_number
        if scene_num not in scenes:
            scenes[scene_num] = set()
        scenes[scene_num].add(evidence.character_name)

    analysis = {}
    for scene_num, characters in scenes.items():
        char_count = len(characters)

        # Rate complexity (Obra Dinn sweet spot is 3-8 characters)
        if char_count <= 2:
            rating = "SIMPLE"
        elif char_count <= 6:
            rating = "BALANCED"
        elif char_count <= 10:
            rating = "COMPLEX"
        else:
            rating = "OVERWHELMING"

        analysis[scene_num] = {
            'character_count': char_count,
            'characters': sorted(characters),
            'complexity_rating': rating
        }

    return analysis


def check_scene_complexity(
    scene_complexity: Dict[int, Dict]
) -> Tuple[bool, str]:
    """Validate that scene complexity is reasonable.

    Warns about:
    - Scenes with too few characters (< 2) - limited cross-referencing
    - Scenes with too many characters (> 10) - overwhelming for players
    """
    issues = []
    warnings = []

    simple_scenes = []
    overwhelming_scenes = []

    for scene_num, info in scene_complexity.items():
        count = info['character_count']
        if count == 1:
            simple_scenes.append(scene_num)
        elif count > 10:
            overwhelming_scenes.append((scene_num, count))

    if overwhelming_scenes:
        overwhelming_list = ", ".join(f"Scene {num} ({count} chars)" for num, count in overwhelming_scenes)
        issues.append(f"Overwhelming scenes (>10 characters): {overwhelming_list}")

    if len(simple_scenes) > len(scene_complexity) * 0.3:
        warnings.append(
            f"{len(simple_scenes)} scenes have only 1 character ({len(simple_scenes)/len(scene_complexity)*100:.0f}%) - "
            f"limits cross-referencing opportunities"
        )

    # Summary
    complexity_counts = Counter(info['complexity_rating'] for info in scene_complexity.values())
    report_lines = [
        f"Scene complexity: SIMPLE={complexity_counts['SIMPLE']}, "
        f"BALANCED={complexity_counts['BALANCED']}, "
        f"COMPLEX={complexity_counts['COMPLEX']}, "
        f"OVERWHELMING={complexity_counts['OVERWHELMING']}"
    ]

    if issues:
        report_lines.extend(issues)
    if warnings:
        report_lines.extend(warnings)

    passed = len(issues) == 0
    return (passed, "\n".join(report_lines))


def check_clue_type_diversity(
    clue_analysis: Dict[str, Dict]
) -> Tuple[bool, str]:
    """Check that characters have diverse clue types (not all of one kind).

    Warns about characters that rely too heavily on a single clue type.
    E.g., "10 role clues, 0 visual, 0 dialogue" = unbalanced
    """
    issues = []
    warnings = []

    unbalanced_characters = []

    for character_name, data in clue_analysis.items():
        clue_types = data['clue_types']
        total = data['total_clues']

        if total == 0:
            continue

        # Check if one clue type dominates (>80% of total)
        max_type = max(clue_types.items(), key=lambda x: x[1])
        max_type_name, max_count = max_type

        if max_count > total * 0.8 and total >= 5:
            unbalanced_characters.append(
                f"{character_name}: {max_count}/{total} clues are {max_type_name}"
            )

    if unbalanced_characters:
        if len(unbalanced_characters) > 10:
            warnings.append(
                f"{len(unbalanced_characters)} characters rely heavily on one clue type - "
                f"reduces gameplay variety"
            )
        else:
            warnings.append(
                f"Characters with unbalanced clue types:\n    " +
                "\n    ".join(unbalanced_characters)
            )

    # Summary
    report_lines = []
    if not unbalanced_characters:
        report_lines.append(f"All characters have diverse clue types - good variety!")
    else:
        report_lines.append(f"{len(unbalanced_characters)} characters have unbalanced clue distributions")

    if warnings:
        report_lines.extend(warnings)

    passed = len(issues) == 0
    return (passed, "\n".join(report_lines))


def check_death_attribution_completeness(
    characters: Dict[str, Character]
) -> Tuple[bool, str]:
    """Check that all death information is complete.

    Every dead character should have:
    - Non-empty cause of death
    - Responsible party (killer name or "Accident")
    - Valid death scene number
    """
    issues = []

    missing_cause = []
    missing_killer = []
    missing_scene = []

    for character in characters.values():
        if character.is_dead():
            if not character.cause_of_death or not character.cause_of_death.strip():
                missing_cause.append(character.name)

            if not character.killer or not character.killer.strip():
                missing_killer.append(character.name)

            if character.death_scene is None:
                missing_scene.append(character.name)

    if missing_cause:
        issues.append(f"Missing cause of death: {', '.join(missing_cause)}")

    if missing_killer:
        issues.append(f"Missing responsible party: {', '.join(missing_killer)}")

    if missing_scene:
        issues.append(f"Missing death scene: {', '.join(missing_scene)}")

    if issues:
        return (False, "\n".join(issues))

    dead_count = sum(1 for c in characters.values() if c.is_dead())
    return (True, f"All {dead_count} deaths have complete attribution (cause, killer, scene).")
