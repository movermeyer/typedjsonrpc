import json
import pytest

from typedjsonrpc.registry import Registry


def test_register():
    registry = Registry()

    def foo(x):
        return x
    registry.register("bar", foo)
    assert "bar" in registry._name_to_method
    assert registry._name_to_method["bar"] == foo


def test_method():
    registry = Registry()

    @registry.method(returns=str, x=str)
    def foo(x):
        return x
    expected_name = "{}.{}".format(foo.__module__, foo.__name__)
    assert expected_name in registry._name_to_method
    assert registry._name_to_method[expected_name] == foo


def test_method_correct_argtypes():
    registry = Registry()

    @registry.method(returns=str, some_text=str, some_number=int)
    def foo(some_text, some_number):
        return some_text + str(some_number)
    assert foo("Hello", 5) == "Hello5"
    assert foo(some_text="Hello", some_number=5) == "Hello5"
    assert foo("Hello", some_number=5) == "Hello5"
    assert foo(some_number=5, some_text="Hello") == "Hello5"

    @registry.method(returns=str)
    def bar():
        return "Works"
    assert bar() == "Works"

    @registry.method(returns=str, some_text=str, some_number=int)
    def stuff(some_number, some_text):
        return str(some_number) + some_text
    assert stuff(42, "Answer") == "42Answer"


def test_method_args():
    registry = Registry()

    @registry.method(returns=str, some_text=str, some_number=int)
    def foo(some_text, some_number, *args):
        return some_text + str(some_number) + str(args)
    assert foo("Hi", 5, 6, "Test") == "Hi5(6, 'Test')"

    @registry.method(returns=str, some_text=str, some_number=int)
    def bar(some_text, some_number, *args, **kwargs):
        return some_text + str(some_number) + str(args) + str(kwargs)
    assert bar("Hi", 5, "foo", bla=6, stuff="Test") == "Hi5('foo',){'stuff': 'Test', 'bla': 6}"
    with pytest.raises(TypeError):
        bar("Hi", test=7)


def test_method_defaults():
    registry = Registry()

    @registry.method(returns=str, some_number=int, some_text=str)
    def foo(some_number, some_text="Test"):
        return some_text
    assert foo(5) == "Test"
    assert foo(5, "Hello") == "Hello"


def test_method_wrong_type_declarations():
    registry = Registry()

    with pytest.raises(Exception):
        @registry.method(returns=str, some_text=str, some_number=int)
        def foo(some_text, some_stuff):
            return some_text + some_stuff


def test_method_wrong_argument_order():
    registry = Registry()

    @registry.method(returns=str, some_text=str, some_number=int)
    def foo(some_text, some_number):
        return some_text + str(some_number)
    assert foo("Answer", 42) == "Answer42"
    with pytest.raises(TypeError):
        foo(42, "Answer")


def test_method_wrong_return_type():
    registry = Registry()

    @registry.method(returns=str, some_number=int)
    def foo(some_number):
        return some_number
    with pytest.raises(TypeError):
        foo(5)


def test_method_no_return_type():
    registry = Registry()

    with pytest.raises(Exception):
        @registry.method(some_number=int)
        def foo(some_number):
            return some_number


def test_method_return_type_none():
    registry = Registry()

    @registry.method(returns=None)
    def foo():
        pass
    foo()

    @registry.method(returns=type(None))
    def fun():
        pass
    fun()

    @registry.method(returns=type(None), some_text=str)
    def bar(some_text):
        return some_text
    with pytest.raises(TypeError):
        bar("Hello")

    @registry.method(returns=None, some_number=int)
    def stuff(some_number):
        return 2 * some_number
    with pytest.raises(TypeError):
        stuff(21)


def test_method_parameter_named_returns():
    registry = Registry()

    with pytest.raises(Exception):
        @registry.method(returns=str, some_number=int)
        def foo(some_number, returns):
            return str(some_number) + returns


def test_dispatch_keyword_args():
    registry = Registry()

    def add(x, y):
        return x + y
    registry.register("add", add)

    class FakeRequest(object):
        def get_data(self):
            return json.dumps({
                "jsonrpc": "2.0",
                "method": "add",
                "params": {
                    "x": 1,
                    "y": 2,
                },
                "id": "bogus",
            })
    fake_request = FakeRequest()
    response = registry.dispatch(fake_request)
    assert response == json.dumps({
        "jsonrpc": "2.0",
        "id": "bogus",
        "result": 3
    })


def test_dispatch_positional_args():
    registry = Registry()

    def add(x, y):
        return x + y
    registry.register("add", add)

    class FakeRequest(object):
        def get_data(self):
            return json.dumps({
                "jsonrpc": "2.0",
                "method": "add",
                "params": [1, 2],
                "id": "bogus",
            })
    fake_request = FakeRequest()
    response = registry.dispatch(fake_request)
    assert response == json.dumps({
        "jsonrpc": "2.0",
        "id": "bogus",
        "result": 3
    })


def test_dispatch_invalid_method():
    registry = Registry()

    class FakeRequest(object):
        def get_data(self):
            return json.dumps({
                "jsonrpc": "2.0",
                "method": "bogus",
                "params": [1, 2],
                "id": "bogus",
            })
    fake_request = FakeRequest()
    with pytest.raises(Exception):
        registry.dispatch(fake_request)