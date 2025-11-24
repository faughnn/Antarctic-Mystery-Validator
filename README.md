# Antarctic Mystery Validator

[![Mystery Validator](https://github.com/faughnn/Antarctic-Mystery-Validator/actions/workflows/validate.yml/badge.svg)](https://github.com/faughnn/Antarctic-Mystery-Validator/actions/workflows/validate.yml)

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

## Remote Testing & Viewing Results

### 🤖 Automated Testing (GitHub Actions)

Every push automatically runs the validator. View results in multiple ways:

1. **Status Badge** (top of this README)
   - 🟢 Green = All tests passing
   - 🔴 Red = Some tests failing

2. **GitHub Actions Tab**
   - Go to: https://github.com/faughnn/Antarctic-Mystery-Validator/actions
   - Click on any workflow run
   - See full Python output in the "Run Mystery Validator" step
   - View the **Summary** tab for formatted results

3. **Download Full Logs**
   - On any workflow run page
   - Click "Artifacts" section
   - Download `validation-results` (text file with complete output)

4. **Manual Trigger**
   - Go to Actions tab → "Mystery Validator" workflow
   - Click "Run workflow" button
   - Select branch and run on demand

### 💻 Local Testing (Claude Code Web)

When working in Claude Code Web:

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

## What You'll See in GitHub Actions

When you visit the Actions tab, you'll see:

```
🧊 Antarctic Mystery Validator
================================================================================

Loading data files...
✓ Loaded 60 characters
✓ Loaded 295 scene evidence records
✓ Loaded 275 dialogue lines

Running validation checks...

================================================================================
VALIDATION RESULTS
================================================================================

✓ PASS - Everyone Appears
      All 60 characters appear in at least one scene.

✓ PASS - Death Scenes Valid
      All 60 dead characters have valid death scenes.

[... more results ...]
```

**The workflow will:**
- ✅ Pass (green checkmark) if all validations pass
- ❌ Fail (red X) if any validation fails
- 📊 Show summary on the workflow summary page
- 💾 Save full output as downloadable artifact

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
