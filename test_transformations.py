import pytest
from transformations import *

@pytest.mark.parametrize("value,expected", [
    ('cat','cat'),
    ('dog','dog'),
    ('human','other'),
    ('CAT','cat'),
    (None,'other'),
    (123,'other')])
def test_type(value,expected):
    assert transform_type(value) == expected

@pytest.mark.parametrize("value,expected", [
    ('pug','pug'),
    ('GERMAN SHEPARD','german shepard'),
    (None,None),
    (123,'123')
])
def test_breed(value,expected):
    assert transform_breed(value) == expected

@pytest.mark.parametrize("value,expected", [
    ('paul','Paul'),
    ('Lizzi','Lizzi'),
    ('DONALD','Donald'),
    (None,None),
    (123,'123')])
def test_name(value,expected):
    assert transform_name(value) == expected
