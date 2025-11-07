import json
from pathlib import Path
from typing import List, Dict


class FactLoader:
    IRREGULAR_PLURALS = {
        "mouse": "mice",
        "goose": "geese",
        "child": "children",
        "person": "people",
        "man": "men",
        "woman": "women",
        "tooth": "teeth",
        "foot": "feet",
        "ox": "oxen"
    }

    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)
        self.emoji_map = self._load_emoji_map()

    def get_available_fact_types(self) -> List[str]:
        fact_types = []
        for json_file in self.data_directory.glob("*.json"):
            if json_file.name != "emoji_list.json":
                fact_types.append(json_file.stem)
        return sorted(fact_types)

    def get_emoji_for_fact_type(self, fact_type: str) -> str:
        # Direct emoji mappings for common fact types (fallback/override)
        direct_mappings = {
            'apples': '🍎',
            'bananas': '🍌',
            'cheese': '🧀',
            'cats': '🐱',
            'dogs': '🐶'
        }

        # Check direct mapping first
        if fact_type in direct_mappings:
            return direct_mappings[fact_type]

        singular_forms = {
            'mice': 'mouse',
            'geese': 'goose',
            'children': 'child',
            'people': 'person',
            'men': 'man',
            'women': 'woman',
            'teeth': 'tooth',
            'feet': 'foot',
            'oxen': 'ox'
        }

        singular = singular_forms.get(fact_type)
        if not singular:
            if fact_type.endswith('ies'):
                singular = fact_type[:-3] + 'y'
            elif fact_type.endswith('ves'):
                if fact_type.endswith('aves'):
                    singular = fact_type[:-3] + 'e'
                else:
                    singular = fact_type[:-3] + 'f'
            elif fact_type.endswith('es'):
                singular = fact_type[:-2]
            elif fact_type.endswith('s'):
                singular = fact_type[:-1]
            else:
                singular = fact_type

        for emoji, name in self.emoji_map.items():
            if name == singular:
                return emoji

        print(f"Warning: No emoji found for fact_type='{fact_type}', singular='{singular}'")
        print(f"Available emoji mappings: {list(self.emoji_map.items())[:5]}...")
        return '❓'

    def _load_emoji_map(self) -> Dict[str, str]:
        emoji_list_path = self.data_directory / "emoji_list.json"

        if not emoji_list_path.exists():
            return {}

        with open(emoji_list_path) as file:
            data = json.load(file)

        emoji_map = {}
        for category in data.values():
            emoji_map.update(category)

        return emoji_map

    def get_theme_for_emoji(self, emoji: str) -> str:
        base_name = self.emoji_map.get(emoji, "")
        if not base_name:
            return ""

        if base_name in self.IRREGULAR_PLURALS:
            return self.IRREGULAR_PLURALS[base_name]
        elif base_name.endswith('s') or base_name.endswith('x') or base_name.endswith('ch') or base_name.endswith('sh'):
            return f"{base_name}es"
        elif base_name.endswith('y') and len(base_name) > 1 and base_name[-2] not in 'aeiou':
            return f"{base_name[:-1]}ies"
        elif base_name.endswith('f'):
            return f"{base_name[:-1]}ves"
        elif base_name.endswith('fe'):
            return f"{base_name[:-2]}ves"
        else:
            return f"{base_name}s"

    def load_facts_for_emoji(self, emoji: str) -> List[str]:
        theme_name = self.get_theme_for_emoji(emoji)
        if not theme_name:
            return []

        return self._load_theme(theme_name)

    def load_facts_for_fact_type(self, fact_type: str) -> List[str]:
        return self._load_theme(fact_type)

    def _load_theme(self, theme_name: str) -> List[str]:
        theme_path = self.data_directory / f"{theme_name}.json"

        if not theme_path.exists():
            return []

        with open(theme_path) as file:
            data = json.load(file)

        return data.get("facts", [])
