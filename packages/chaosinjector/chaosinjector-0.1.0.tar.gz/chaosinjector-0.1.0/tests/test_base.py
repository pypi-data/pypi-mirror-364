from unittest.mock import patch

import pytest

from src.chaosinjector import ChaosInjector


class TestClass:
    def method(self):
        return "real_method_result"

    def another_method(self):
        return "another_real"

    attr = "real_attr"


@pytest.fixture
def proxy():
    return ChaosInjector()


def test_probability_1_always_real(proxy):
    obj = TestClass()
    proxy.inject(obj, probability=1.0)

    assert obj.method() == "real_method_result"
    assert obj.attr == "real_attr"


def test_probability_0_always_noop(proxy):
    obj = TestClass()
    proxy.inject(obj, probability=0.0)

    assert obj.method() is None
    result = obj.method()
    assert result is None
    assert obj.attr is None


@patch("random.random")
def test_probability_0_5_mocked(mock_random, proxy):
    obj = TestClass()
    proxy.inject(obj, probability=0.5)

    mock_random.return_value = 0.4
    assert obj.method() == "real_method_result"

    mock_random.return_value = 0.6
    result = obj.method()
    assert result is None


def test_decider_always_true(proxy):
    obj = TestClass()
    proxy.inject(obj, decider=lambda name: True)

    assert obj.method() == "real_method_result"
    assert obj.attr == "real_attr"


def test_decider_always_false(proxy):
    obj = TestClass()
    proxy.inject(obj, decider=lambda name: False)

    result = obj.method()
    assert result is None
    assert obj.attr is None


def test_decider_conditional(proxy):
    obj = TestClass()
    proxy.inject(
        obj, decider=lambda name: name == "method"
    )

    assert obj.method() == "real_method_result"
    another_result = obj.another_method()
    assert another_result is None
    assert obj.attr is None


@patch("random.random")
def test_method_probs_specific(mock_random, proxy):
    obj = TestClass()
    proxy.inject(obj, method_probs={"method": 1.0, "another_method": 0.0})

    mock_random.return_value = 0.5
    assert obj.method() == "real_method_result"

    another_result = obj.another_method()
    assert another_result is None

    mock_random.return_value = 0.4
    assert obj.attr == "real_attr"

    mock_random.return_value = 0.6
    assert obj.attr is None


@patch("random.random")
def test_method_probs_with_fallback(mock_random, proxy):
    obj = TestClass()
    proxy.inject(obj, probability=0.3, method_probs={"method": 0.8})

    mock_random.return_value = 0.7
    assert obj.method() == "real_method_result"

    mock_random.return_value = 0.9
    result = obj.method()
    assert result is None

    mock_random.return_value = 0.2
    assert obj.another_method() == "another_real"

    mock_random.return_value = 0.4
    another_result = obj.another_method()
    assert another_result is None


def test_non_existing_attribute(proxy):
    obj = TestClass()
    proxy.inject(obj, probability=1.0)

    with pytest.raises(AttributeError):
        obj.non_existing

    proxy.inject(obj, probability=0.0)
    with pytest.raises(AttributeError):
        obj.non_existing


def test_multiple_adds(proxy):
    obj1 = TestClass()
    obj2 = TestClass()

    proxy.inject(obj1, probability=1.0)
    proxy.inject(obj2, probability=0.0)

    assert obj1.method() == "real_method_result"
    assert obj2.method() is None


def test_callable_vs_non_callable(proxy):
    class MixedClass:
        def func(self): return "func"

        prop = "prop"

    obj = MixedClass()
    proxy.inject(obj, probability=0.0)

    func_result = obj.func()
    assert func_result is None
    assert obj.prop is None


def test_decider_priority_over_probs(proxy):
    obj = TestClass()
    proxy.inject(
        obj,
        probability=0.5,
        decider=lambda name: name == "method",
        method_probs={"method": 0.0}
    )

    assert obj.method() == "real_method_result"
    another_result = obj.another_method()
    assert another_result is None


def test_invalid_probability(proxy):
    obj = TestClass()
    with pytest.raises(ValueError):
        proxy.inject(obj, probability=1.5)
