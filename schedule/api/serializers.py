from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from schedule.models import RecurrenceRule, Schedule, ScheduleParticipant, ScheduleReminder


class RecurrenceRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurrenceRule
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        required=False,
        allow_null=True,
    )
    recurrence_rule = serializers.PrimaryKeyRelatedField(
        queryset=RecurrenceRule.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Schedule
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ScheduleParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleParticipant
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ScheduleReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleReminder
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
