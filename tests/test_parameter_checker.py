# coding: utf-8
#
# Copyright 2015 Palantir Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

import pytest

import typedjsonrpc.parameter_checker as parameter_checker
from typedjsonrpc.errors import InvalidParamsError


def test_list():
    def foo(a, b, c="baz"):
        pass

    with pytest.raises(InvalidParamsError):
        parameter_checker.validate_params_match(foo, ["foo"])
    parameter_checker.validate_params_match(foo, ["foo", "bar"])

    with pytest.raises(InvalidParamsError):
        parameter_checker.validate_params_match(foo, ["foo", "bar", "bop", 42])


def test_varargs():
    def foo(a, b="foo", *varargs):
        pass

    with pytest.raises(InvalidParamsError):
        parameter_checker.validate_params_match(foo, [])
    parameter_checker.validate_params_match(foo, ["foo", "bar"])
    parameter_checker.validate_params_match(foo, ["foo", "bar", 42])


def test_dict():
    def foo(a, b, c="baz"):
        pass

    with pytest.raises(InvalidParamsError):
        parameter_checker.validate_params_match(foo, {"a": "foo"})
    parameter_checker.validate_params_match(foo, {"a": "foo", "b": "bar"})

    with pytest.raises(InvalidParamsError):
        parameter_checker.validate_params_match(foo, {"a": "foo", "b": "bar", "c": "bop", "d": 42})

    with pytest.raises(InvalidParamsError):
        parameter_checker.validate_params_match(foo, {"a": "foo", "c": "bar"})


def test_kwargs():
    def foo(a, b, c="baz", **kwargs):
        pass

    with pytest.raises(InvalidParamsError):
        parameter_checker.validate_params_match(foo, {"a": "foo"})
    parameter_checker.validate_params_match(foo, {"a": "foo", "b": "bar"})

    parameter_checker.validate_params_match(foo, {"a": "foo", "b": "bar", "d": 42})

    with pytest.raises(InvalidParamsError):
        parameter_checker.validate_params_match(foo, {"a": "foo", "c": "bar"})


def test_no_defaults():
    def foo(a):
        pass
    with pytest.raises(InvalidParamsError):
        parameter_checker.validate_params_match(foo, [])
    parameter_checker.validate_params_match(foo, ["bar"])
    with pytest.raises(InvalidParamsError):
        parameter_checker.validate_params_match(foo, ["bar", "baz"])

    with pytest.raises(InvalidParamsError):
        parameter_checker.validate_params_match(foo, {})
    parameter_checker.validate_params_match(foo, {"a": "bar"})
    with pytest.raises(InvalidParamsError):
        parameter_checker.validate_params_match(foo, {"a": "bar", "b": "baz"})


class TestIsInstance(object):
    def test_strict_floats(self):
        assert parameter_checker._is_instance(1.0, float, strict_floats=True)
        assert not parameter_checker._is_instance(1, float, strict_floats=True)
        # This is a long in Python 2
        assert not parameter_checker._is_instance(1000000000000000000000, float, strict_floats=True)

    def test_non_strict_floats(self):
        assert parameter_checker._is_instance(1.0, float, strict_floats=False)
        assert parameter_checker._is_instance(1, float, strict_floats=False)
        # This is a long in Python 2
        assert parameter_checker._is_instance(1000000000000000000000, float, strict_floats=False)
