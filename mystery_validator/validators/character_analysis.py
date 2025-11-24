"""Character-focused analysis for Obra Dinn-style game balance.

Analyzes clue counts, scene appearances, and difficulty ratings for each character.
"""

from typing import Dict, List
from models import Character, SceneEvidence


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
