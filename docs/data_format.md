# Data Format Specifications

## characters.csv
Required columns:
- `id` - Unique identifier (lowercase, no spaces)
- `name` - Full character name
- `role` - Job title/role
- `death_scene` - Scene number where they died (empty if alive)
- `cause_of_death` - How they died (explosion, frozen, shot, etc.)
- `killer` - ID of who killed them (empty if accident/suicide)

## scenes.csv
Required columns:
- `id` - Scene number (1-6)
- `name` - Scene title
- `timeline_day` - Day number when scene occurs
- `characters_present` - JSON list of character IDs visible
- `characters_dead` - JSON list of character IDs dead in scene

## clues.csv
Required columns:
- `id` - Unique clue identifier
- `scene_id` - Which scene contains this clue
- `clue_type` - Type of clue (visual, dialogue, contextual, etc.)
- `subject_character` - Character ID this clue identifies
- `description` - Human-readable clue description
- `difficulty` - 1 (easy), 2 (medium), 3 (hard)
- `prerequisites` - JSON list of character IDs that must be known first