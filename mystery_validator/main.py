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
    }

    # Generate report
    generate_simple_report(validation_results)

    # Return exit code
    all_passed = all(passed for passed, _ in validation_results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
