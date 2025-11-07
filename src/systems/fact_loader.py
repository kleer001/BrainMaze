import json
from pathlib import Path
from typing import List


class FactLoader:
    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)

    def get_available_fact_types(self) -> List[str]:
        fact_types = []
        for json_file in self.data_directory.glob("*.json"):
            if json_file.name != "emoji_list.json":
                fact_types.append(json_file.stem)
        return sorted(fact_types)

    def get_emoji_for_fact_type(self, fact_type: str) -> str:
        """Get emoji for a fact type. Fact type names should match emoji mappings exactly."""
        emoji_mappings = {
            'apples': '🍎',
            'bananas': '🍌',
            'bears': '🐻',
            'books': '📖',
            'cats': '🐱',
            'cheese': '🧀',
            'dogs': '🐶',
            'lightning': '⚡',
            'mice': '🐭',
            'pizza': '🍕',
            'rainbows': '🌈',
            'sharks': '🦈',
            'stars': '⭐'
        }

        if fact_type in emoji_mappings:
            return emoji_mappings[fact_type]

        print(f"Warning: No emoji found for fact_type='{fact_type}'")
        return '❓'

    def load_facts_for_fact_type(self, fact_type: str) -> List[str]:
        """Load all facts for a given fact type from its JSON file."""
        return self._load_theme(fact_type)

    def _load_theme(self, theme_name: str) -> List[str]:
        theme_path = self.data_directory / f"{theme_name}.json"

        if not theme_path.exists():
            return []

        with open(theme_path) as file:
            data = json.load(file)

        return data.get("facts", [])
