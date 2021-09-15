from vcftool.batch import chunked


def test_chunked_basic():
    iterable = [1, 2, 3, 4, 5, 6]
    assert list(chunked(iterable, 2)) == [(1, 2), (3, 4), (5, 6)]
    assert list(chunked(iterable, 3)) == [(1, 2, 3), (4, 5, 6)]
    assert list(chunked(iterable, 4)) == [(1, 2, 3, 4), (5, 6)]


def test_chunked_no_items():
    assert list(chunked([], 2)) == []


def test_chunked_0_size():
    assert list(chunked([1, 2], 0)) == []
