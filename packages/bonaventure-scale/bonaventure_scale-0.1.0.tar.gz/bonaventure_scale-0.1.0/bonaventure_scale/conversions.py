"""
conversions.py
Bonaventure Scale Conversion Functions

This module provides conversion functions between Bonaventure Scale (°B),
Celsius (°C), Fahrenheit (°F), and Kelvin (K).
"""

def bonaventure_to_celsius(B):
    """Convert Bonaventure (°B) to Celsius (°C)."""
    return (100 / 198) * (B - 50)

def celsius_to_bonaventure(C):
    """Convert Celsius (°C) to Bonaventure (°B)."""
    return (198 / 100) * C + 50

def bonaventure_to_fahrenheit(B):
    """Convert Bonaventure (°B) to Fahrenheit (°F)."""
    return (180 / 198) * (B - 14.8)

def fahrenheit_to_bonaventure(F):
    """Convert Fahrenheit (°F) to Bonaventure (°B)."""
    return (198 / 180) * F + 14.8

def bonaventure_to_kelvin(B):
    """Convert Bonaventure (°B) to Kelvin (K)."""
    C = bonaventure_to_celsius(B)
    return C + 273.15

def kelvin_to_bonaventure(K):
    """Convert Kelvin (K) to Bonaventure (°B)."""
    C = K - 273.15
    return celsius_to_bonaventure(C)
