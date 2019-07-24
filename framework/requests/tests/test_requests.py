from framework.requests.requests import Requests


def test_pikachu_is_there():
    r = Requests(url="https://pokeapi.co/api/v2/pokemon/pikachu")
    assert r.request() is True
    assert r.status_code == 200
    assert r.dict_data is not None
    assert r.filename is None
    r.save()
    assert r.filename is not None
    assert r.cached_filename is not None

    r_saved = Requests.load_from_file(r.cached_filename)
    assert r_saved._requested is True
    assert r.url == r_saved.url
    assert r.filename == r_saved.filename
    assert r.cached_filename == r_saved.cached_filename
    assert r.dict_data == r_saved.dict_data