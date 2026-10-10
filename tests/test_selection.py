import pytest
from deforest_gee.selection import parsear_seleccion


def test_lista_y_rango():
    assert parsear_seleccion("1,3-5", 6) == [0, 2, 3, 4]


def test_todos():
    assert parsear_seleccion("todos", 3) == [0, 1, 2]


def test_fuera_de_rango():
    with pytest.raises(ValueError):
        parsear_seleccion("4", 3)
