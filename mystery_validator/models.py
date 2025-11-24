from dataclasses import dataclass
from typing import Optional

@dataclass
class Character:
    name: str
    role: str
    nationality: str
    build: str
    cause_of_death: Optional[str]
    killer: Optional[str]
    death_scene: Optional[int]

    def is_dead(self) -> bool:
        return self.death_scene is not None and self.death_scene > 0

    def get_description(self) -> str:
        status = f"dies in scene {self.death_scene} by {self.cause_of_death}" if self.is_dead() else "survives"
        return f"{self.name}, {self.role} ({self.nationality}, {self.build}) - {status}"


@dataclass
class SceneEvidence:
    character_name: str
    scene_number: int
    dies_in_this_scene: bool
    uniform_visible: bool
    holding_something_distinctive: bool
    held_item_description: Optional[str]
    distinctive_features_visible: bool
    distinctive_features_description: Optional[str]
    body_position_relevant: bool
    body_position_description: Optional[str]
    accent_audible: bool
    name_mentioned_in_dialogue: bool
    relationship_mentioned: bool
    relationship_description: Optional[str]
    role_mentioned: bool
    role_behaviour_visible: bool
    spatial_relationship_visible: bool
    spatial_relationship_description: Optional[str]
    environmental_context_relevant: bool
    environmental_context_description: Optional[str]
    additional_visual_clues: Optional[str]
    additional_dialogue_clues: Optional[str]
    additional_contextual_clues: Optional[str]


@dataclass
class Dialogue:
    scene_number: int
    line_number: int
    speaker: str
    text: str
    display_time: Optional[str]
