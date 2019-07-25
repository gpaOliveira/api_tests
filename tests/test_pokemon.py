from tests.test_base import ApiTestBase
from framework.apis.pokemon.api_pokemon import ApiPokemon
from framework.pokemon.pokemon import Pokemon
from framework.comparisons.equal_deep import EqualDeep


class TestPokemonApi(ApiTestBase):

    def test_make_sure_pikachu_exists(self):
        """
        Given the Pokemon API
        When pikachu data is requested
        Then his type is electric
        And it appears on 20 games
        """
        api = ApiPokemon(self.environment.POKEMON_BASE)
        pokemon: Pokemon = api.get_pokemon("pikachu")
        self.flush_api_messages(api)

        self.add_output_message(str(pokemon))

        equals = EqualDeep()
        if not equals.run(target=pokemon, name="pikachu", types="electric", games_count=20):
            self.add_fail_messages(equals.error_messages)

        self.then_everything_should_be_fine()

    def test_make_sure_a_pokemon_abcdefg_does_not_exist(self):
        """
        Given the Pokemon API
        When abcdefg data is requested
        Then nothing appears
        """
        api = ApiPokemon(self.environment.POKEMON_BASE)
        pokemon: Pokemon = api.get_pokemon("abcdefg")

        self.add_output_message(str(pokemon))

        if pokemon is not None:
            self.add_fail_message("Pokemon should not have been found!")

        self.then_everything_should_be_fine()


