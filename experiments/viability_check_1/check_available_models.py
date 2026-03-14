#!/usr/bin/env python3
"""Check available models for Groq and Google."""

import os

# Check Groq models
print("="*60)
print("GROQ MODELS")
print("="*60)
try:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    models = client.models.list()
    print("\nAvailable Groq models:")
    for model in models.data:
        print(f"  - {model.id}")
except Exception as e:
    print(f"Error: {e}")

# Check Google models
print("\n" + "="*60)
print("GOOGLE GEMINI MODELS")
print("="*60)
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    models = genai.list_models()
    print("\nAvailable Gemini models that support generateContent:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
except Exception as e:
    print(f"Error: {e}")
