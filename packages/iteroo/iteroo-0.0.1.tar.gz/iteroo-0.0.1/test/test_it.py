from iteroo import it
import iteroo


def test_range():
    assert it.range(5).sum() == sum(range(5))


def test_t():
    a = iteroo.it.it([[1, 1], [2, 2], [3, 3]])
    b = a.inmap([lambda x: x + 1, lambda x: x + 2, lambda x: x + 3]).collect()

    print(b)
    assert b


def test_alltrue():
    assert not it.it([False, True, True]).alltrue()
    assert it.it([True, True, True]).alltrue()

    assert it.it([True, "Some", 1, "False"]).alltrue()

    assert not it.it([True, "Some", 0, "False"]).alltrue()


# todo dedup
def test_allfalse():
    assert not it.it([False, True, True]).allfalse()
    assert it.it([False, False, False]).allfalse()

    assert it.it([False, 0, None]).allfalse()
    assert not it.it([False, 0, None, "False"]).allfalse()


def test_equal():
    a = it.it([0, 1, 2, 3])
    b = it.range(4)
    assert a.equal(b).alltrue()

    assert a.collect() == b.collect()


def test_flatten():
    a = iteroo.it.it([[1, 3, 4], [1, 5, 6]])
    assert a.flatten().collect() == [1, 3, 4, 1, 5, 6]


def test_flatten_2deep():
    a = iteroo.it.it([[1, 3, [4, 9]], [1, 5, 6]])
    assert a.flatten().collect() == [1, 3, [4, 9], 1, 5, 6]


def test_sum():
    a = [1, 2, 3, 4, 5, 6]
    assert iteroo.it.it(a).sum() == sum(a)
    assert sum(iteroo.it.it(a)) == sum(a)


def test_count():
    a = it.it([1, 2, 3, 4, 5, 6])
    assert a.count() == 6


def test_diff():
    a = it.it([1, 2, 4, 7, 11, 15])
    assert a.diff().allequal([1, 2, 3, 4])


def test_take_every_nth():
    a = it.range(1, 10)
    assert a.take_every_nth(1).collect() == a.collect()
    assert a.take_every_nth(2).collect() == [2, 4, 6, 8]
    assert a.take_every_nth(3).collect() == [3, 6, 9]
    assert a.take_every_nth(4).collect() == [4, 8]
    assert a.take_every_nth(5).collect() == [5]


def test_count_gen():
    a = it.count(start=1, step=2)
    assert a.takewhile(lambda x: x <= 5).collect() == [1, 3, 5]


def test_cycle():
    a = it.count(start=1, step=2).take_n(2)
    assert a.collect() == [1, 3]
    b = it.count(start=1, step=2).take_n(2)
    assert b.cycle().take_n(6).collect() == [1, 3, 1, 3, 1, 3]


def test_take_n():
    # assert a.select(5).collect() == [1, 3, 5, 76, 9]
    a = it.count(start=1, step=2)
    assert a.take_n(4).collect() == [1, 3, 5, 7]


def test_repeat():
    from iteroo.it import repeat
    assert repeat(1, 3).collect() == [1, 1, 1]


def test_zip():
    a = it.it([1, 2, 3])
    b = it.it([4, 5, 6])
    assert a.zip(b).collect() == [(1, 4), (2, 5), (3, 6)]


def test_select():
    a = it.it([1, 2, 3, 4])
    mask = [1, 0, 1, 0]
    assert a.select(mask).collect() == [1, 3]


def test_dropwhile():
    a = it.it([1, 2, 3, 4, 1, 2])
    assert a.dropwhile(lambda x: x < 3).collect() == [3, 4, 1, 2]


def test_max():
    a = it.it([1, 5, 3, 2])
    assert a.max() == 5


def test_filter():
    a = it.it([1, 2, 3, 4, 5])
    assert a.filter(lambda x: x % 2 == 0).collect() == [2, 4]
