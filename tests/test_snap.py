from deforest_gee.snap import detectar_gpt

def test_detectar_gpt_no_falla():
    assert detectar_gpt() is None or isinstance(detectar_gpt(), str)
