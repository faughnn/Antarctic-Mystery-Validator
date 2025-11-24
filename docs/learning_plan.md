# Python Mystery Validator - Step-by-Step Learning Plan

## Overview
Build a mystery validation framework for your Antarctic Station Alpha-7 game, learning Python along the way. Each phase builds on the previous one, introducing new Python concepts gradually.

---

## Phase 1: Python Basics & Data Loading (Week 1-2)

### Goal
Load your mystery data from CSV files and display it.

### Python Concepts to Learn
- Variables and basic data types (strings, integers, lists, dictionaries)
- Reading files
- CSV module
- Loops (for, while)
- Print formatting

### Project Tasks
1. **Create your project structure:**
   ```
   mystery_validator/
   ├── data/
   │   ├── characters.csv
   │   ├── scenes.csv
   │   └── clues.csv
   └── main.py
   ```

2. **Write a simple CSV reader:**
   ```python
   import csv
   
   # Read and print characters
   with open('data/characters.csv', 'r') as file:
       reader = csv.DictReader(file)
       for row in reader:
           print(f"Character: {row['name']} - {row['role']}")
   ```

3. **Store data in dictionaries:**
   ```python
   characters = {}
   # Load characters into dictionary with ID as key
   ```

4. **Practice exercises:**
   - Count how many characters died
   - List all unique death causes
   - Find which scene has the most deaths

### Success Criteria
- [x] Can load all 3 CSV files
- [x] Can print a summary of the data
- [x] Understand dictionaries and lists

---

## Phase 2: Basic Data Structures with Classes (Week 3-4)

### Goal
Replace dictionaries with proper classes for better organization.

### Python Concepts to Learn
- Classes and objects
- `__init__` method
- Instance variables
- Methods
- `@dataclass` decorator (simpler syntax)

### Project Tasks
1. **Create your first class:**
   ```python
   class Character:
       def __init__(self, id, name, role):
           self.id = id
           self.name = name
           self.role = role
           self.death_scene = None
           self.cause_of_death = None
           self.killer = None
       
       def is_dead(self):
           return self.death_scene is not None
   ```

2. **Learn about dataclasses (easier syntax):**
   ```python
   from dataclasses import dataclass
   
   @dataclass
   class Scene:
       id: int
       name: str
       timeline_day: int
       characters_present: list
       characters_dead: list
   ```

3. **Create the file structure:**
   ```
   mystery_validator/
   ├── models.py      # Character, Scene, Clue classes
   ├── loaders.py     # Functions to load CSVs
   └── main.py        # Main program
   ```

4. **Practice exercises:**
   - [x] Add a method to Character that returns a description string
   - [ ] Create a method that checks if a character was present in a scene
   - [ ] Write a `__str__` method for pretty printing

### Success Criteria
- [x] All data stored as objects instead of dictionaries (Characters complete, Scenes/Clues created)
- [x] Can create and use class methods
- [x] Understand difference between class and instance

---

## Phase 3: Simple Validations (Week 5-6)

### Goal
Implement basic validation checks without complex logic.

### Python Concepts to Learn
- Functions with return values
- Type hints
- List comprehensions
- Boolean logic
- Error messages and string formatting

### Project Tasks
1. **Create validators.py with simple checks:**
   ```python
   def check_everyone_appears(characters, scenes):
       """Check that every character appears in at least one scene"""
       appearing_characters = set()
       for scene in scenes.values():
           appearing_characters.update(scene.characters_present)
       
       missing = []
       for char_id in characters.keys():
           if char_id not in appearing_characters:
               missing.append(char_id)
       
       return len(missing) == 0, missing
   ```

2. **Implement these validations:**
   - [x] Every character appears in at least one scene
   - [x] Every death has a scene number
   - [x] No duplicate character IDs
   - [x] Death scenes actually exist
   - [x] Every scene has at least one character

3. **Create a simple report:**
   ```python
   def generate_simple_report(validation_results):
       print("VALIDATION REPORT")
       print("=" * 50)
       for check_name, (passed, details) in validation_results.items():
           status = "✓" if passed else "✗"
           print(f"{status} {check_name}")
           if not passed:
               print(f"   Issues: {details}")
   ```

### Success Criteria
- [x] At least 5 working validation functions (completed: everyone appears, death scenes exist, no duplicates)
- [x] Clean, readable validation report
- [x] Understand function return values and tuples

---

## Phase 4: Timeline and Death Logic (Week 7-8)

### Goal
Implement complex timeline validation and death consistency checks.

### Python Concepts to Learn
- [ ] Nested loops
- [ ] Complex conditionals
- [ ] Set operations
- [ ] Sorting and filtering
- [ ] Exception handling (try/except)

### Project Tasks
1. **Timeline consistency checker:**
   ```python
   def validate_timeline_consistency(characters, scenes):
       """Ensure characters don't appear after death"""
       errors = []
       
       for scene in scenes.values():
           for char_id in scene.characters_present:
               character = characters.get(char_id)
               if character and character.death_scene:
                   death_scene = scenes.get(character.death_scene)
                   if death_scene.timeline_day < scene.timeline_day:
                       errors.append(f"{character.name} appears after death")
       
       return len(errors) == 0, errors
   ```

2. **Death attribution validator:**
   - [ ] Check every murder has a valid killer
   - [ ] Verify killer was alive at the time
   - [ ] Ensure death causes match scene descriptions

3. **Create organized validator classes:**
   ```python
   class TimelineValidator:
       def __init__(self, characters, scenes):
           self.characters = characters
           self.scenes = scenes
       
       def validate(self):
           # All timeline checks
           pass
   ```

### Success Criteria
- [ ] Timeline validation working correctly
- [ ] Death logic fully validated
- [ ] Code organized into logical validator classes

---

## Phase 5: Clue Coverage Analysis (Week 9-10)

### Goal
Ensure every character can be identified through clues.

### Python Concepts to Learn
- [ ] Enums
- [ ] JSON parsing
- [ ] Nested data structures
- [ ] Recursive thinking (but not recursive functions yet)
- [ ] Collections module (Counter, defaultdict)

### Project Tasks
1. **Create enums.py:**
   ```python
   from enum import Enum
   
   class ClueType(Enum):
       VISUAL = "visual"
       DIALOGUE = "dialogue"
       CONTEXTUAL = "contextual"
       ELIMINATION = "elimination"
   ```

2. **Implement clue analysis:**
   - [ ] Count clues per character
   - [ ] Check every character has at least one "easy" clue
   - [ ] Identify characters with no clues
   - [ ] Analyze clue distribution by type

3. **Create difficulty scoring:**
   ```python
   def calculate_identification_difficulty(character_id, clues):
       character_clues = [c for c in clues if c.subject_character == character_id]
       if not character_clues:
           return float('inf')  # Impossible
       
       easiest = min(c.difficulty for c in character_clues)
       return easiest
   ```

### Success Criteria
- [ ] Can identify which characters lack clues
- [ ] Difficulty scoring system works
- [ ] Clue distribution report generated

---

## Phase 6: Dependency Graph - Basic (Week 11-12)

### Goal
Detect circular dependencies without using graph libraries.

### Python Concepts to Learn
- [ ] Building directed graphs with dictionaries
- [ ] Basic graph traversal
- [ ] Finding cycles manually
- [ ] Debugging complex logic

### Project Tasks
1. **Build a dependency map:**
   ```python
   def build_dependency_map(clues):
       """Map which characters depend on others being identified first"""
       dependencies = {}
       for clue in clues:
           if clue.prerequisites:
               if clue.subject_character not in dependencies:
                   dependencies[clue.subject_character] = set()
               dependencies[clue.subject_character].update(clue.prerequisites)
       return dependencies
   ```

2. **Simple cycle detection:**
   ```python
   def has_circular_dependency(char_a, char_b, dependencies):
       """Check if A depends on B and B depends on A"""
       a_needs_b = char_b in dependencies.get(char_a, set())
       b_needs_a = char_a in dependencies.get(char_b, set())
       return a_needs_b and b_needs_a
   ```

3. **Identify bottleneck characters:**
   - [ ] Count how many characters depend on each character
   - [ ] Flag characters that block 3+ others

### Success Criteria
- [ ] Can detect simple circular dependencies
- [ ] Can identify bottleneck characters
- [ ] Understand graph representation with dictionaries

---

## Phase 7: Advanced Dependencies with NetworkX (Week 13-14)

### Goal
Use NetworkX library for sophisticated dependency analysis.

### Python Concepts to Learn
- [ ] Installing and using external libraries (pip)
- [ ] NetworkX basics
- [ ] Graph algorithms
- [ ] Library documentation reading

### Project Tasks
1. **Install NetworkX:**
   ```bash
   pip install networkx
   ```

2. **Rebuild with NetworkX:**
   ```python
   import networkx as nx
   
   def build_dependency_graph(clues):
       G = nx.DiGraph()
       for clue in clues:
           for prereq in clue.prerequisites:
               G.add_edge(prereq, clue.subject_character)
       return G
   ```

3. **Advanced analysis:**
   - [ ] Find all cycles: `nx.simple_cycles(G)`
   - [ ] Find shortest paths between characters
   - [ ] Identify strongly connected components

### Success Criteria
- [ ] NetworkX integrated successfully
- [ ] Can find all circular dependencies
- [ ] Can visualize the dependency graph

---

## Phase 8: Solving Simulation (Week 15-16)

### Goal
Simulate a player solving the mystery step-by-step.

### Python Concepts to Learn
- [ ] State machines
- [ ] Simulation logic
- [ ] Complex algorithms
- [ ] Debugging strategies

### Project Tasks
1. **Create solver state:**
   ```python
   @dataclass
   class SolverState:
       identified_characters: set
       available_clues: list
       used_clues: set
       current_iteration: int
   ```

2. **Implement solving algorithm:**
   ```python
   def simulate_solving(characters, clues):
       state = SolverState(set(), clues, set(), 0)
       steps = []
       
       while len(state.identified_characters) < len(characters):
           # Find usable clues
           # Pick easiest clue
           # Apply clue
           # Record step
           pass
       
       return steps
   ```

3. **Generate solving path report:**
   - [ ] Show order characters get identified
   - [ ] Identify where players might get stuck
   - [ ] Calculate minimum steps to solve

### Success Criteria
- [ ] Simulation completes successfully
- [ ] Can identify unsolvable mysteries
- [ ] Clear step-by-step solving report

---

## Phase 9: Report Generation & Visualization (Week 17-18)

### Goal
Create professional, readable output reports.

### Python Concepts to Learn
- [ ] String formatting and templates
- [ ] File writing
- [ ] Optional: HTML generation
- [ ] Optional: Matplotlib for graphs

### Project Tasks
1. **Create reports.py:**
   ```python
   class ReportGenerator:
       def __init__(self, results):
           self.results = results
       
       def generate_text_report(self):
           # Plain text report
           pass
       
       def generate_html_report(self):
           # HTML formatted report
           pass
       
       def save_to_file(self, filename):
           # Save report to file
           pass
   ```

2. **Add visualizations (optional):**
   ```python
   import matplotlib.pyplot as plt
   
   def plot_difficulty_distribution(difficulty_scores):
       # Create bar chart of character difficulties
       pass
   ```

3. **Summary statistics:**
   - [ ] Overall solvability score
   - [ ] Difficulty curve analysis
   - [ ] Completeness percentage

### Success Criteria
- [ ] Professional-looking reports
- [ ] Multiple output formats
- [ ] Clear, actionable recommendations

---

## Phase 10: Polish & Error Handling (Week 19-20)

### Goal
Make the tool robust and user-friendly.

### Python Concepts to Learn
- [ ] Exception handling
- [ ] Logging
- [ ] Command-line arguments
- [ ] Configuration files
- [ ] Unit testing basics

### Project Tasks
1. **Add error handling:**
   ```python
   try:
       characters = load_characters(filename)
   except FileNotFoundError:
       print(f"Error: Could not find {filename}")
       return
   except csv.Error as e:
       print(f"Error reading CSV: {e}")
       return
   ```

2. **Add command-line interface:**
   ```python
   import argparse
   
   parser = argparse.ArgumentParser(description='Validate mystery game logic')
   parser.add_argument('--characters', required=True, help='Path to characters CSV')
   parser.add_argument('--scenes', required=True, help='Path to scenes CSV')
   parser.add_argument('--clues', required=True, help='Path to clues CSV')
   ```

3. **Write basic tests:**
   ```python
   def test_circular_dependency_detection():
       # Test that circular dependencies are caught
       pass
   ```

### Success Criteria
- [ ] Graceful error handling
- [ ] User-friendly command-line interface
- [ ] At least 10 unit tests
- [ ] Configuration file support

---

## Bonus Challenges

Once you've completed all phases, try these:

1. [ ] **Add a GUI**: Use Tkinter or PyQt to create a graphical interface
2. [ ] **Web version**: Use Flask to create a web-based validator
3. [ ] **Auto-fix suggestions**: Suggest how to fix validation errors
4. [ ] **Difficulty balancer**: Automatically suggest clue additions to balance difficulty
5. [ ] **Multiple mystery support**: Validate multiple mysteries in batch
6. **Export to game format**: Generate JSON/XML for your game engine

---

## Resources for Learning

### Python Basics
- Python.org official tutorial
- "Automate the Boring Stuff with Python" (free online)
- Python Tutor (visualize code execution)

### Specific Topics
- Real Python (excellent articles on every topic)
- GeeksforGeeks (good for algorithms)
- Stack Overflow (when you're stuck)

### For Your Mystery Project
- NetworkX documentation (for graph work)
- Pandas documentation (for CSV handling)
- Python CSV module docs

---

## Tips for Success

1. **Commit working code**: Use git, commit after each working phase
2. **Test with small data first**: Use 3 characters before testing with all 9
3. **Print everything**: Add print statements to understand what's happening
4. **Keep a learning journal**: Note what confused you and how you solved it
5. **Don't skip phases**: Each builds important knowledge for the next
6. **Ask for help**: When stuck for >30 minutes, take a break or ask for help
7. **Refactor regularly**: Once it works, make it cleaner
8. **Celebrate milestones**: Each phase completed is an achievement!

---

## Expected Timeline

- **Total time**: 20 weeks at casual pace (few hours per week)
- **Accelerated**: 8-10 weeks if studying intensively
- **With experience**: 4-6 weeks if you know some Python

Remember: The goal is learning, not speed. Take time to understand each concept thoroughly.