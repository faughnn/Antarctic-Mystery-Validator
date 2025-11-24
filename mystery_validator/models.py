from dataclasses import dataclass

@dataclass
class Character:
    id: str
    name: str
    role: str
    death_scene: str
    cause_of_death: str
    killer: str

    def is_dead(self):
        return self.death_scene is not None
    
    def get_description(self):
        return f"{self.name}, the {self.role} dies in scene {self.death_scene} by {self.cause_of_death}. The killer is {self.killer}."

@dataclass
class Clue:
    id: str
    discovery_scene_id: str
    fate_aspect: str
    clue_type: str
    target_character: str
    description: str
    difficulty: str
    prerequisites: str

@dataclass
class Scene:
    id: str
    name: str
    timeline_day: str
    order_shown_to_player: str
    characters_present: str
    characters_dead: str
    dialogue_speakers: str
    clues: str