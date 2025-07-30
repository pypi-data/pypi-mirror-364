from memetextgen import to_meme_case

def test_output_length():
    assert len(to_meme_case("test")) == 4

def test_type():
    assert isinstance(to_meme_case("test"), str)
