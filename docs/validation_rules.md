# Validation Rules

## Timeline Rules
- A character cannot appear in a scene chronologically after their death
- Death scenes must exist (reference valid scene IDs)
- Killers must be alive when they kill someone

## Identification Rules  
- Every character must have at least one clue with no prerequisites
- Every character must be identifiable through some chain of clues
- No circular dependencies (A needs B, B needs A)

## Clue Distribution Rules
- Each scene should have at least 2 clues
- Each character should have multiple identification paths
- Easy clues (difficulty 1) should exist for at least 50% of characters

## Bottleneck Rules
- Warn if any character blocks 3+ other identifications
- Flag if more than 30% of characters depend on a single character