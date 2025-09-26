from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from datetime import datetime

from .models import DebateSession, DebateMessage, DebateEvaluation
from .ai_clients import AIClientManager


def home(request):
    """메인 페이지 - 토론 목록"""
    sessions = DebateSession.objects.all()[:10]
    return render(request, 'debate/home.html', {'sessions': sessions})


def create_session(request):
    """새 토론 세션 생성"""
    if request.method == 'POST':
        title = request.POST.get('title', '제목 없음')
        topic = request.POST.get('topic', '')
        ai1_prompt = request.POST.get('ai1_prompt', '긍정적인 관점에서 토론하세요.')
        ai2_prompt = request.POST.get('ai2_prompt', '부정적인 관점에서 토론하세요.')
        max_rounds = int(request.POST.get('max_rounds', 5))

        session = DebateSession.objects.create(
            title=title,
            topic=topic,
            ai1_system_prompt=ai1_prompt,
            ai2_system_prompt=ai2_prompt,
            max_rounds=max_rounds,
            user=request.user if request.user.is_authenticated else None
        )

        # 초기 사용자 메시지 저장
        DebateMessage.objects.create(
            session=session,
            speaker='user',
            content=topic,
            round_number=0
        )

        return redirect('debate:session_detail', session_id=session.id)

    return render(request, 'debate/create_session.html')


def session_detail(request, session_id):
    """토론 세션 상세 페이지"""
    session = get_object_or_404(DebateSession, id=session_id)
    messages = session.messages.all()
    return render(request, 'debate/session_detail.html', {
        'session': session,
        'messages': messages
    })


@require_http_methods(["POST"])
def start_debate(request, session_id):
    """토론 시작/진행"""
    session = get_object_or_404(DebateSession, id=session_id)

    if session.status == 'completed':
        return JsonResponse({'error': '이미 완료된 토론입니다.'}, status=400)

    # 토론 상태를 '진행중'으로 변경
    if session.status == 'created':
        session.status = 'in_progress'
        session.save()

    # 다음 발언자 결정
    last_message = session.messages.filter(speaker__in=['ai1', 'ai2']).last()
    if not last_message or last_message.speaker == 'ai2':
        next_speaker = 'ai1'
    else:
        next_speaker = 'ai2'

    # 최대 라운드 체크 (AI2가 발언을 완료한 후에만)
    if session.current_round >= session.max_rounds and next_speaker == 'ai1':
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save()
        return JsonResponse({'message': '토론이 완료되었습니다.', 'completed': True})

    try:
        # AI 클라이언트 매니저 생성
        ai_manager = AIClientManager()

        # 대화 히스토리 가져오기
        conversation_history = list(session.messages.all())

        # 시스템 프롬프트 선택
        system_prompt = (
            session.ai1_system_prompt if next_speaker == 'ai1'
            else session.ai2_system_prompt
        )

        # AI 응답 생성
        response_data = ai_manager.get_ai_response(
            next_speaker,
            system_prompt,
            conversation_history
        )
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'AI 응답 생성 중 오류가 발생했습니다: {str(e)}'
        }, status=500)

    if response_data['success']:
        # 라운드 증가 (AI1이 발언할 때만)
        if next_speaker == 'ai1':
            session.current_round += 1
            session.save()

        # 메시지 저장
        message = DebateMessage.objects.create(
            session=session,
            speaker=next_speaker,
            content=response_data['content'],
            round_number=session.current_round,
            response_time=response_data['response_time'],
            model_used=response_data.get('model_used', '')
        )

        return JsonResponse({
            'success': True,
            'message': {
                'id': str(message.id),
                'speaker': message.speaker,
                'content': message.content,
                'round_number': message.round_number,
                'created_at': message.created_at.isoformat()
            },
            'session': {
                'current_round': session.current_round,
                'max_rounds': session.max_rounds,
                'status': session.status
            }
        })

    else:
        return JsonResponse({
            'success': False,
            'error': response_data['error']
        }, status=500)


def session_list(request):
    """토론 세션 목록"""
    sessions = DebateSession.objects.all()
    return render(request, 'debate/session_list.html', {'sessions': sessions})


@require_http_methods(["POST"])
def evaluate_debate(request, session_id):
    """토론 평가"""
    session = get_object_or_404(DebateSession, id=session_id)

    try:
        data = json.loads(request.body)

        evaluation = DebateEvaluation.objects.create(
            session=session,
            ai1_score=data.get('ai1_score'),
            ai2_score=data.get('ai2_score'),
            ai1_comment=data.get('ai1_comment', ''),
            ai2_comment=data.get('ai2_comment', ''),
            overall_comment=data.get('overall_comment', ''),
            winner=data.get('winner'),
            evaluator=request.user if request.user.is_authenticated else None
        )

        return JsonResponse({
            'success': True,
            'evaluation_id': str(evaluation.id)
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
