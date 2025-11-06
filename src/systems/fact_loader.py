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

    def _load_theme(self, theme_name: str) -> List[str]:
        theme_path = self.data_directory / f"{theme_name}.json"

        if not theme_path.exists():
            return []

        with open(theme_path) as file:
            data = json.load(file)

        return data.get("facts", [])
