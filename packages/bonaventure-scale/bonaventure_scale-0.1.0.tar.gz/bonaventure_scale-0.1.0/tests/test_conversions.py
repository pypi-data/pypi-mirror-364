import pytest
from bonaventure_scale import (
    bonaventure_to_celsius,
    celsius_to_bonaventure,
    bonaventure_to_fahrenheit,
    fahrenheit_to_bonaventure,
    bonaventure_to_kelvin,
    kelvin_to_bonaventure
)

def test_bonaventure_to_celsius():
    assert round(bonaventure_to_celsius(90), 2) == 20.20

def test_celsius_to_bonaventure():
    assert round(celsius_to_bonaventure(20.2020), 1) == 90.0

def test_bonaventure_to_fahrenheit():
    assert round(bonaventure_to_fahrenheit(90), 2) == 68.36

def test_fahrenheit_to_bonaventure():
    assert round(fahrenheit_to_bonaventure(68.36), 1) == 90.0

def test_bonaventure_to_kelvin():
    assert round(bonaventure_to_kelvin(90), 2) == 293.35

def test_kelvin_to_bonaventure():
    assert round(kelvin_to_bonaventure(293.35), 1) == 90.0
