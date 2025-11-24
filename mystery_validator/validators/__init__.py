"""Validators for Antarctic Mystery game data integrity and balance.

This package contains validators organized by category:
- basic: Core data integrity checks
- timeline: Timeline consistency and ghost detection
- character_analysis: Clue counting and difficulty analysis
- game_balance: Scene complexity, clue diversity, difficulty balance
"""

# Basic validators
from .basic import (
    check_everyone_appears,
    check_every_death_has_a_scene,
    check_every_character_has_identifying_clues,
    check_scenes_have_characters,
    check_dialogue_speakers_exist,
)

# Timeline validators
from .timeline import (
    check_timeline_consistency,
)

# Character analysis
from .character_analysis import (
    analyze_clues_per_character,
    analyze_character_appearances,
    analyze_character_difficulty,
)

# Game balance validators
from .game_balance import (
    check_difficulty_balance,
    analyze_scene_complexity,
    check_scene_complexity,
    check_clue_type_diversity,
    check_death_attribution_completeness,
)

__all__ = [
    # Basic
    'check_everyone_appears',
    'check_every_death_has_a_scene',
    'check_every_character_has_identifying_clues',
    'check_scenes_have_characters',
    'check_dialogue_speakers_exist',
    # Timeline
    'check_timeline_consistency',
    # Character analysis
    'analyze_clues_per_character',
    'analyze_character_appearances',
    'analyze_character_difficulty',
    # Game balance
    'check_difficulty_balance',
    'analyze_scene_complexity',
    'check_scene_complexity',
    'check_clue_type_diversity',
    'check_death_attribution_completeness',
]
