# Antarctic Mystery Validator

A validation system for the Antarctic Station Alpha-7 mystery game. Ensures the mystery is logically solvable, consistent, and properly balanced.

## Quick Start

### Run the Validator

```bash
# From project root
./test.sh

# Or directly
cd mystery_validator && python3 main.py
```

## Project Structure

```
Antarctic-Mystery-Validator/
├── mystery_validator/
│   ├── models.py           # Data classes (Character, SceneEvidence, Dialogue)
│   ├── loaders.py          # CSV loading functions
│   ├── validators.py       # Validation logic
│   ├── reports.py          # Report generation
│   ├── main.py             # Main entry point
│   └── data/exported/
│       ├── characters.csv       # 60 character records
│       ├── scene_evidence.csv   # 295 scene evidence records
│       └── dialogue.csv         # 275 dialogue lines
├── test.sh                 # Quick test runner
└── README.md              # This file
```

## Data Files

### characters.csv
- **60 characters** with their roles, nationalities, builds, and death information
- Columns: `characterName`, `role`, `nationality`, `build`, `causeOfDeath`, `responsibleParty`, `deathSceneNumber`

### scene_evidence.csv
- **295 evidence records** showing how characters can be identified in different scenes
- Tracks: visual clues, dialogue mentions, relationships, behavior, environmental context
- Character x Scene matrix with 23 columns of identification data

### dialogue.csv
- **275 dialogue lines** across all scenes
- Columns: `sceneNumber`, `lineNumber`, `speaker`, `text`, `displayTime`

## Current Validations

✅ **Everyone Appears** - Every character appears in at least one scene
✅ **Death Scenes Valid** - Dead characters have valid death scenes with evidence
✅ **Characters Have Identifying Clues** - Every character has at least one way to be identified
✅ **Scenes Have Characters** - No empty scenes
⚠️ **Dialogue Speakers Exist** - All dialogue speakers are valid characters (currently failing: 112 lines with empty speakers)

## Testing Remotely with Claude Code Web

Since you're using Claude Code Web, everything runs in the browser environment:

1. **Quick Test**: Just run `./test.sh`
2. **Direct Run**: `cd mystery_validator && python3 main.py`
3. **Check Specific Data**: Use Python interpreter to inspect data

### Example: Inspect Data

```bash
cd mystery_validator
python3 -c "
from loaders import load_characters
from pathlib import Path

characters = load_characters(Path('data/exported/characters.csv'))
print(f'Loaded {len(characters)} characters')

# Show first 5 dead characters
dead = [c for c in characters.values() if c.is_dead()][:5]
for c in dead:
    print(f'  {c.name}: {c.cause_of_death} in scene {c.death_scene}')
"
```

## Next Steps

### Potential Improvements

1. **Fix Data Issues**
   - Add speakers to the 112 dialogue lines with missing speakers

2. **Add More Validations**
   - Timeline consistency (characters don't appear after death)
   - Killer validation (killers are alive at time of murder)
   - Clue dependency analysis (no circular dependencies)
   - Difficulty scoring

3. **Enhanced Reporting**
   - HTML report generation
   - Visualization of scene timelines
   - Character appearance graphs
   - Dependency graphs using NetworkX

4. **Testing**
   - Unit tests for validators
   - Sample data for testing
   - Edge case coverage

## Development Notes

- **Python 3.11+** required
- Uses `dataclasses` for clean data modeling
- Type hints throughout
- Cross-platform file path handling with `pathlib`
- UTF-8 BOM handling for CSV files

## Exit Codes

- `0` - All validations passed
- `1` - One or more validations failed

## Questions?

Check the code - it's well-commented and structured for easy understanding!
