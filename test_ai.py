#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Django 설정
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_debate.settings')
django.setup()

from debate.ai_clients import AIClientManager

def test_ai_clients():
    print("AI client test started...")

    try:
        # AI 매니저 생성
        ai_manager = AIClientManager()
        print("AI manager created successfully")

        # OpenAI 테스트
        print("\nTesting OpenAI client...")
        response = ai_manager.get_ai_response(
            "ai1",
            "Say hello briefly.",
            []
        )
        print("OpenAI response:", response)

        # Ollama 테스트
        print("\nTesting Ollama client...")
        response = ai_manager.get_ai_response(
            "ai2",
            "Say hello briefly.",
            []
        )
        print("Ollama response:", response)

    except Exception as e:
        print("Error occurred:", str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_clients()