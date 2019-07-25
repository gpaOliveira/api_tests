import json


class Pokemon:
    def __init__(self, pokemon_raw):
        self._pokemon_raw = pokemon_raw
        self.name = pokemon_raw.get("name")
        games = [
            t.get("version", {}).get("name")
            for t in pokemon_raw.get("game_indices", {})
        ]
        self.games = ",".join(games)
        self.games_count = len(games)
        self.types = ",".join([
            t.get("type", {}).get("name")
            for t in pokemon_raw.get("types", {})
        ])

    def __str__(self):
        return "{}:\n{}".format(self.__class__.__name__, json.dumps(self.to_json(), indent=4))

    def to_json(self):
        return {
            "name": self.name,
            "games": self.games,
            "types": self.types
        }
