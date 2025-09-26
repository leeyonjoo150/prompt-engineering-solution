# AI 토론 시스템

두 AI가 서로 다른 관점에서 토론하는 웹 애플리케이션입니다.

## 주요 기능

- **AI vs AI 토론**: OpenAI와 Ollama API를 사용하여 두 AI가 토론
- **실시간 진행**: 실시간으로 토론 과정을 관찰
- **토론 평가**: 완료된 토론에 대해 점수 및 코멘트 평가
- **히스토리 관리**: 이전 토론 내용 저장 및 조회

## 설치 및 실행

### 1. 환경 설정

```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 마이그레이션

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. 관리자 계정 생성 (선택사항)

```bash
python manage.py createsuperuser
```

### 4. 개발 서버 실행

```bash
python manage.py runserver
```

브라우저에서 `http://127.0.0.1:8000`으로 접속하세요.

## API 설정

### OpenAI API

환경변수 또는 Django settings에 API 키를 설정하세요:

```python
OPENAI_API_KEY = 'your-openai-api-key'
```

### Ollama API

로컬에 Ollama가 설치되어 있어야 합니다:

```bash
# Ollama 설치 후
ollama serve
ollama pull llama2
```

기본 설정: `http://localhost:11434`

## 사용 방법

1. **새 토론 시작**: 홈페이지에서 "새로운 토론 시작하기" 클릭
2. **토론 설정**: 제목, 주제, AI 프롬프트, 라운드 수 설정
3. **토론 진행**: "토론 시작" 버튼으로 AI 응답 생성
4. **자동 진행**: "자동 진행" 버튼으로 전체 토론 자동 진행
5. **토론 평가**: 완료 후 각 AI의 성과 평가

## 프로젝트 구조

```
ai_debate/
├── debate/
│   ├── models.py          # 데이터베이스 모델
│   ├── views.py           # 뷰 함수
│   ├── ai_clients.py      # AI API 클라이언트
│   ├── templates/         # HTML 템플릿
│   └── admin.py           # 관리자 페이지
├── ai_debate/
│   ├── settings.py        # Django 설정
│   └── urls.py           # URL 라우팅
└── requirements.txt       # 패키지 의존성
```

## AI 설정

### AI1 (긍정)
- **색상**: 파란색 계열
- **역할**: 주제에 대해 긍정적/찬성 관점
- **API**: OpenAI GPT-3.5-turbo

### AI2 (부정)
- **색상**: 빨간색 계열
- **역할**: 주제에 대해 부정적/반대 관점
- **API**: Ollama (로컬 LLM)

## 개발자 정보

이 프로젝트는 Django 5.2.6과 Bootstrap 5.3을 사용하여 개발되었습니다.

## 라이선스

MIT License