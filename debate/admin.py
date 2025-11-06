from django.contrib import admin
from .models import DebateSession, DebateMessage, DebateEvaluation


@admin.register(DebateSession)
class DebateSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'current_round', 'max_rounds', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'topic']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(DebateMessage)
class DebateMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'speaker', 'round_number', 'created_at']
    list_filter = ['speaker', 'round_number', 'created_at']
    search_fields = ['content', 'session__title']
    readonly_fields = ['id', 'created_at']


@admin.register(DebateEvaluation)
class DebateEvaluationAdmin(admin.ModelAdmin):
    list_display = ['session', 'ai1_score', 'ai2_score', 'winner', 'created_at']
    list_filter = ['winner', 'ai1_score', 'ai2_score', 'created_at']
    search_fields = ['session__title', 'overall_comment']
    readonly_fields = ['id', 'created_at']
