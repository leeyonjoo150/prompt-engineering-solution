import os
import openai
import requests
import time
from typing import Dict, Optional
from django.conf import settings
import httpx


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'OPENAI_API_KEY', None)
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        # OpenAI 1.0+ 방식 - 커스텀 http 클라이언트 사용
        try:
            http_client = httpx.Client()
            self.client = openai.OpenAI(api_key=self.api_key, http_client=http_client)
        except Exception as e:
            # 백업: 기본 방식 시도
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception:
                raise ValueError(f"Failed to initialize OpenAI client: {str(e)}")

    def generate_response(
        self,
        system_prompt: str,
        conversation_history: list,
        model: str = None
    ) -> Dict:
        """
        OpenAI API를 사용하여 응답 생성
        """
        start_time = time.time()

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # 대화 히스토리 추가
        for msg in conversation_history:
            if msg.speaker == 'user':
                messages.append({"role": "user", "content": msg.content})
            else:
                messages.append({"role": "assistant", "content": msg.content})

        try:
            # OpenAI 1.0+ 방식만 사용
            response = self.client.chat.completions.create(
                model=model or getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            end_time = time.time()

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model_used": model or getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
                "response_time": end_time - start_time,
                "usage": response.usage.model_dump() if hasattr(response.usage, 'model_dump') else None
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }


class OllamaClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')

    def generate_response(
        self,
        system_prompt: str,
        conversation_history: list,
        model: str = None
    ) -> Dict:
        """
        Ollama API를 사용하여 응답 생성
        """
        start_time = time.time()

        # 대화 히스토리를 하나의 프롬프트로 구성
        prompt = f"System: {system_prompt}\n\n"

        for msg in conversation_history:
            if msg.speaker == 'user':
                prompt += f"Human: {msg.content}\n"
            elif msg.speaker == 'ai1':
                prompt += f"AI1: {msg.content}\n"
            elif msg.speaker == 'ai2':
                prompt += f"AI2: {msg.content}\n"

        prompt += "Assistant: "

        try:
            # OpenAI 호환 API 형식 사용
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            for msg in conversation_history:
                if msg.speaker == 'user':
                    messages.append({"role": "user", "content": msg.content})
                elif msg.speaker in ['ai1', 'ai2']:
                    messages.append({"role": "assistant", "content": msg.content})

            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": model or getattr(settings, 'OLLAMA_MODEL', 'llama2'),
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                headers={
                    "Content-Type": "application/json"
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                end_time = time.time()

                # OpenAI 호환 API 응답 형식에서 content 추출
                content = ""
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]

                return {
                    "success": True,
                    "content": content,
                    "model_used": model or getattr(settings, 'OLLAMA_MODEL', 'llama2'),
                    "response_time": end_time - start_time
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": time.time() - start_time
                }

        except requests.ConnectionError:
            return {
                "success": False,
                "error": "Ollama 서버에 연결할 수 없습니다. Ollama가 실행되고 있는지 확인하세요.",
                "response_time": time.time() - start_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }


class AIClientManager:
    """AI 클라이언트들을 관리하는 클래스"""

    def __init__(self):
        self.openai_client = OpenAIClient()
        self.ollama_client = OllamaClient()

    def get_ai_response(
        self,
        ai_type: str,
        system_prompt: str,
        conversation_history: list
    ) -> Dict:
        """
        AI 타입에 따라 적절한 클라이언트를 사용하여 응답 생성
        """
        if ai_type == "ai1":  # OpenAI
            return self.openai_client.generate_response(
                system_prompt,
                conversation_history
            )
        elif ai_type == "ai2":  # Ollama
            return self.ollama_client.generate_response(
                system_prompt,
                conversation_history
            )
        else:
            return {
                "success": False,
                "error": f"Unknown AI type: {ai_type}"
            }