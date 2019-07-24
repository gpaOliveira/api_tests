from tests.test_base import ApiTestBase
from framework.apis.pokemon.api_pokemon import ApiPokemon
from framework.pokemon.pokemon import Pokemon


class TestPokemonApi(ApiTestBase):

    def test_make_sure_pikachu_exists(self):
        """
        Given the Pokemon API
        When pikachu data is requested
        Then his type is electric
        And he appears on all games
        """
        api = ApiPokemon(self.environment.POKEMON_BASE)
        pokemon: Pokemon = api.get_pokemon("pikachu")

        self.add_output_message("Pokemon Name: {}".format(pokemon.name))
        self.add_output_message("Pokemon Games: {}".format(pokemon.games))
        self.add_output_message("Pokemon Type: {}".format(pokemon.type))

        if pokemon.name != "pikachu":
            self.add_fail_message("Pikachu not found - found {}".format(pokemon.name))
        if pokemon.games_count < 10:
            self.add_fail_message("Pokemon not in all games, only in {}: {}".format(pokemon.games_count, pokemon.games))
        if pokemon.type != "electric":
            self.add_fail_message("Pokemon not in all games")

        self.then_everything_should_be_fine()


