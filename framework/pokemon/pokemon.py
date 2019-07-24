

class Pokemon:
    def __init__(self, pokemon_raw):
        self.pokemon_raw = pokemon_raw
        self.name = pokemon_raw.get("name")
        games = [
            t.get("version", {}).get("name")
            for t in pokemon_raw.get("game_indices", {})
        ]
        self.games = ",".join(games)
        self.games_count = len(games)
        self.type = ",".join([
            t.get("type", {}).get("name")
            for t in pokemon_raw.get("types", {})
        ])