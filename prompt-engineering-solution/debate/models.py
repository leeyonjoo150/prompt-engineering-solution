from django.db import models
from django.contrib.auth.models import User
import uuid


class DebateSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    topic = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # AI 설정
    ai1_system_prompt = models.TextField(default="긍정적인 관점에서 토론하세요.")
    ai2_system_prompt = models.TextField(default="부정적인 관점에서 토론하세요.")

    # 토론 상태
    STATUS_CHOICES = [
        ('created', '생성됨'),
        ('in_progress', '진행중'),
        ('completed', '완료됨'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')

    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # 토론 설정
    max_rounds = models.IntegerField(default=5)
    current_round = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.status}"


class DebateMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(DebateSession, on_delete=models.CASCADE, related_name='messages')

    SPEAKER_CHOICES = [
        ('user', 'User'),
        ('ai1', 'AI1 (긍정)'),
        ('ai2', 'AI2 (부정)'),
    ]
    speaker = models.CharField(max_length=10, choices=SPEAKER_CHOICES)

    content = models.TextField()
    round_number = models.IntegerField()

    # AI 응답 메타데이터
    response_time = models.FloatField(null=True, blank=True)
    model_used = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.session.title} - {self.speaker} (Round {self.round_number})"


class DebateEvaluation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(DebateSession, on_delete=models.CASCADE, related_name='evaluations')

    # 평가 점수 (1-10)
    ai1_score = models.IntegerField(choices=[(i, i) for i in range(1, 11)])
    ai2_score = models.IntegerField(choices=[(i, i) for i in range(1, 11)])

    # 평가 코멘트
    ai1_comment = models.TextField(blank=True)
    ai2_comment = models.TextField(blank=True)
    overall_comment = models.TextField(blank=True)

    # 승자 선정
    WINNER_CHOICES = [
        ('ai1', 'AI1 (긍정)'),
        ('ai2', 'AI2 (부정)'),
        ('draw', '무승부'),
    ]
    winner = models.CharField(max_length=10, choices=WINNER_CHOICES, null=True, blank=True)

    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session.title} - 평가 ({self.ai1_score} vs {self.ai2_score})"
