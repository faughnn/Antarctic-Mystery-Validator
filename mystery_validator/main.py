#!/usr/bin/env python3
"""
Antarctic Mystery Validator - Main Entry Point

Loads mystery data and runs validation checks to ensure the mystery is solvable.
"""

from pathlib import Path
from loaders import load_characters, load_scene_evidence, load_dialogue
from reports import generate_simple_report
import validators


def main():
    """Main entry point for the mystery validator."""
    # Get the data directory path
    data_dir = Path(__file__).parent / "data" / "exported"

    # File paths
    characters_file = data_dir / "characters.csv"
    evidence_file = data_dir / "scene_evidence.csv"
    dialogue_file = data_dir / "dialogue.csv"

    print("=" * 80)
    print("Antarctic Mystery Validator")
    print("=" * 80)
    print()

    # Load data
    print("Loading data files...")
    try:
        characters = load_characters(characters_file)
        print(f"✓ Loaded {len(characters)} characters")

        scene_evidence = load_scene_evidence(evidence_file)
        print(f"✓ Loaded {len(scene_evidence)} scene evidence records")

        dialogue = load_dialogue(dialogue_file)
        print(f"✓ Loaded {len(dialogue)} dialogue lines")
        print()

    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return 1

    # Run analytical checks first
    print("Analyzing game balance...")
    print()

    clue_analysis = validators.analyze_clues_per_character(characters, scene_evidence)
    appearance_analysis = validators.analyze_character_appearances(characters, scene_evidence)
    difficulty_groups = validators.analyze_character_difficulty(characters, clue_analysis)

    # Run validations
    print("Running validation checks...")
    print()

    validation_results = {
        "Everyone Appears": validators.check_everyone_appears(
            characters, scene_evidence
        ),
        "Death Scenes Valid": validators.check_every_death_has_a_scene(
            characters, scene_evidence
        ),
        "Characters Have Identifying Clues": validators.check_every_character_has_identifying_clues(
            characters, scene_evidence
        ),
        "Scenes Have Characters": validators.check_scenes_have_characters(
            scene_evidence
        ),
        "Dialogue Speakers Exist": validators.check_dialogue_speakers_exist(
            characters, dialogue
        ),
        "Timeline Consistency (No Ghosts)": validators.check_timeline_consistency(
            characters, scene_evidence
        ),
        "Difficulty Balance": validators.check_difficulty_balance(
            difficulty_groups
        ),
    }

    # Generate reports
    generate_simple_report(validation_results)

    # Generate analytical report
    print()
    print("=" * 80)
    print("GAME BALANCE ANALYSIS")
    print("=" * 80)
    print()

    # Difficulty distribution summary
    print("📊 Difficulty Distribution:")
    for difficulty in ['EASY', 'MEDIUM', 'HARD', 'VERY HARD']:
        count = len(difficulty_groups[difficulty])
        percentage = (count / len(characters)) * 100
        print(f"   {difficulty:12} {count:3} characters ({percentage:5.1f}%)")
    print()

    # Character appearance summary
    appearances_list = sorted(appearance_analysis.items(), key=lambda x: x[1])
    print("📍 Scene Appearances:")
    print(f"   Min: {appearances_list[0][1]} scenes - {appearances_list[0][0]}")
    print(f"   Max: {appearances_list[-1][1]} scenes - {appearances_list[-1][0]}")
    avg_appearances = sum(appearance_analysis.values()) / len(appearance_analysis)
    print(f"   Avg: {avg_appearances:.1f} scenes per character")
    print()

    # Characters needing attention (very hard + few scenes)
    print("⚠️  Characters Needing Attention (VERY HARD):")
    very_hard_chars = difficulty_groups['VERY HARD']
    if very_hard_chars:
        for char_name in sorted(very_hard_chars):
            char_data = clue_analysis[char_name]
            scenes = appearance_analysis[char_name]
            print(f"   {char_name:30} {char_data['total_clues']:2} clues, {scenes:2} scenes")
    else:
        print("   None - all characters are solvable!")
    print()

    print("=" * 80)

    # Return exit code
    all_passed = all(passed for passed, _ in validation_results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
