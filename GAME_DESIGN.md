# Game Design Document - Antarctic Mystery Validator

## Game Overview

This is an **Obra Dinn-style deduction game** set in Antarctic Station Alpha-7.

## Core Gameplay Goal

Players must solve the mystery by identifying:
1. **WHO is each character** - Match unnamed people to their identities
2. **HOW they died** - Determine the cause of death for each victim
3. **WHO killed them** - Identify the responsible party for each death

Just like in Return of the Obra Dinn, players piece together the full story through observation, deduction, and cross-referencing clues across multiple scenes.

## How It Works

### Scenes
- Players visit 50 different scenes
- Each scene shows characters in various situations
- Scenes may show deaths, conversations, or contextual moments

### Clues
Characters can be identified through various types of clues:

**Visual Clues:**
- Uniform (e.g., "wearing a scientist's coat")
- Distinctive items they're holding
- Physical features (scars, tattoos, etc.)
- Body position/posture

**Dialogue Clues:**
- Accent (hints at nationality)
- Name mentioned in conversation
- Additional dialogue context

**Contextual Clues:**
- Environmental context (e.g., "standing in the kitchen")
- Spatial relationships (e.g., "next to the station manager")
- Additional contextual information

**Relationship Clues:**
- Mentions of relationships (e.g., "talking to their spouse")

**Role Clues:**
- Role mentioned in dialogue
- Role-specific behavior visible

### The Challenge

A **single clue doesn't solve anything** - it's just one piece of the puzzle.

For example:
- "Wearing a scientist's jacket" → tells you they're a scientist, but not which one
- "Has a Russian accent" → tells you nationality, but not identity
- "Called 'Dr. Smith' by someone" → gives you a name, but you need more to confirm

Players must **combine multiple clues** to deduce:
- The character's full identity
- How they died (if dead)
- Who killed them (if murdered)

### Difficulty

Characters with **more clues** are easier to identify because players have more information to work with.

Characters with **fewer clues** are harder because players must make more difficult deductions with limited information.

## Validation Purpose

This validator ensures:
- The mystery is **solvable** - every character has enough clues
- The game is **balanced** - good mix of easy and hard identifications
- The logic is **consistent** - no timeline errors, ghosts, or impossible situations
- The difficulty is **appropriate** - not too easy (too many clues) or impossible (too few clues)
