from framework.apis.api_base import ApiBase
from framework.pokemon.pokemon import Pokemon


class ApiPokemon(ApiBase):
    def __init__(self, pokemon_base):
        super().__init__()
        self.pokemon_base = pokemon_base

    def get_pokemon(self, pokemon:str) -> Pokemon:
        pokemon_raw = self.request(
            name="get_pokemon",
            url=self.pokemon_base + "v2/pokemon/" + pokemon
        )
        return Pokemon(pokemon_raw)