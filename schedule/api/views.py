from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from schedule.api.serializers import (
    RecurrenceRuleSerializer,
    ScheduleParticipantSerializer,
    ScheduleReminderSerializer,
    ScheduleSerializer,
)
from schedule.models import RecurrenceRule, Schedule, ScheduleParticipant, ScheduleReminder


def _parse_dt_or_none(value):
    if not value:
        return None
    return parse_datetime(value)


def _visible_schedules_for_user(user):
    if user.is_superuser:
        return Schedule.objects.all()
    return Schedule.objects.filter(Q(created_by=user) | Q(participants__user=user)).distinct()


def _add_months(dt, months):
    total_months = (dt.year * 12 + dt.month - 1) + months
    year = total_months // 12
    month = total_months % 12 + 1
    day = min(dt.day, 28)
    return dt.replace(year=year, month=month, day=day)


def _add_years(dt, years):
    try:
        return dt.replace(year=dt.year + years)
    except ValueError:
        return dt.replace(year=dt.year + years, month=2, day=28)


def _generate_occurrences(schedule, start_from=None, end_at=None, max_items=100):
    base_start = schedule.start_at
    duration = schedule.end_at - schedule.start_at
    rule = schedule.recurrence_rule

    if not rule:
        if start_from and base_start < start_from:
            return []
        if end_at and base_start > end_at:
            return []
        return [{'start_at': base_start, 'end_at': base_start + duration}]

    occurrences = []
    current = base_start
    iterations = 0

    weekdays_map = {
        'mon': 0,
        'tue': 1,
        'wed': 2,
        'thu': 3,
        'fri': 4,
        'sat': 5,
        'sun': 6,
    }
    allowed_weekdays = {
        weekdays_map[w.strip().lower()]
        for w in rule.by_weekday.split(',')
        if w.strip().lower() in weekdays_map
    }

    while iterations < max_items:
        iterations += 1

        if rule.until and current > rule.until:
            break
        if end_at and current > end_at:
            break

        if rule.frequency != RecurrenceRule.FREQUENCY_WEEKLY or not allowed_weekdays or current.weekday() in allowed_weekdays:
            if (not start_from or current >= start_from) and (not end_at or current <= end_at):
                occurrences.append({'start_at': current, 'end_at': current + duration})

            if rule.count and len(occurrences) >= rule.count:
                break

        if rule.frequency == RecurrenceRule.FREQUENCY_DAILY:
            current = current + timedelta(days=rule.interval)
        elif rule.frequency == RecurrenceRule.FREQUENCY_WEEKLY:
            current = current + timedelta(days=1)
        elif rule.frequency == RecurrenceRule.FREQUENCY_MONTHLY:
            current = _add_months(current, rule.interval)
        elif rule.frequency == RecurrenceRule.FREQUENCY_YEARLY:
            current = _add_years(current, rule.interval)
        else:
            break

    return occurrences


class RecurrenceRuleListCreateView(APIView):
    def get(self, request, queryset=None, **kwargs):
        rules = RecurrenceRule.objects.all()
        data = RecurrenceRuleSerializer(rules, many=True).data
        return Response(status=status.HTTP_200_OK, data=data)

    def post(self, request, queryset=None, **kwargs):
        serializer = RecurrenceRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class RecurrenceRuleDetailView(APIView):
    def get(self, request, pk, queryset=None, **kwargs):
        if not RecurrenceRule.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Recurrence rule not found.'})
        rule = RecurrenceRule.objects.get(id=pk)
        return Response(status=status.HTTP_200_OK, data=RecurrenceRuleSerializer(rule).data)

    def put(self, request, pk, queryset=None, **kwargs):
        if not RecurrenceRule.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Recurrence rule not found.'})
        rule = RecurrenceRule.objects.get(id=pk)
        serializer = RecurrenceRuleSerializer(rule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def delete(self, request, pk, queryset=None, **kwargs):
        if not RecurrenceRule.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Recurrence rule not found.'})
        RecurrenceRule.objects.get(id=pk).delete()
        return Response(status=status.HTTP_200_OK, data={'message': 'Recurrence rule deleted.'})


class ScheduleListCreateView(APIView):
    def get(self, request, queryset=None, **kwargs):
        schedules = _visible_schedules_for_user(request.user).select_related('recurrence_rule', 'content_type', 'created_by')

        content_type_id = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')
        if content_type_id:
            schedules = schedules.filter(content_type_id=content_type_id)
        if object_id:
            schedules = schedules.filter(object_id=object_id)

        data = ScheduleSerializer(schedules, many=True).data
        return Response(status=status.HTTP_200_OK, data=data)

    def post(self, request, queryset=None, **kwargs):
        payload = request.data.copy()
        if not payload.get('created_by'):
            payload['created_by'] = request.user.id

        serializer = ScheduleSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class ScheduleDetailView(APIView):
    def get(self, request, pk, queryset=None, **kwargs):
        schedules = _visible_schedules_for_user(request.user)
        if not schedules.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Schedule not found.'})
        schedule = schedules.get(id=pk)
        return Response(status=status.HTTP_200_OK, data=ScheduleSerializer(schedule).data)

    def put(self, request, pk, queryset=None, **kwargs):
        schedules = _visible_schedules_for_user(request.user)
        if not schedules.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Schedule not found.'})
        schedule = schedules.get(id=pk)
        serializer = ScheduleSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def delete(self, request, pk, queryset=None, **kwargs):
        schedules = _visible_schedules_for_user(request.user)
        if not schedules.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Schedule not found.'})
        schedules.get(id=pk).delete()
        return Response(status=status.HTTP_200_OK, data={'message': 'Schedule deleted.'})


class ScheduleRangeView(APIView):
    def get(self, request, queryset=None, **kwargs):
        start_raw = request.query_params.get('start')
        end_raw = request.query_params.get('end')

        start_dt = _parse_dt_or_none(start_raw)
        end_dt = _parse_dt_or_none(end_raw)
        if not start_dt or not end_dt:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'message': 'Query params start and end are required in ISO datetime format.'},
            )

        schedules = _visible_schedules_for_user(request.user).filter(start_at__lte=end_dt, end_at__gte=start_dt)
        data = ScheduleSerializer(schedules, many=True).data
        return Response(status=status.HTTP_200_OK, data=data)


class ScheduleTodayView(APIView):
    def get(self, request, queryset=None, **kwargs):
        now = timezone.localtime()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        schedules = _visible_schedules_for_user(request.user).filter(start_at__lt=day_end, end_at__gte=day_start)
        data = ScheduleSerializer(schedules, many=True).data
        return Response(status=status.HTTP_200_OK, data=data)


class ScheduleUpcomingView(APIView):
    def get(self, request, queryset=None, **kwargs):
        days = int(request.query_params.get('days', 7))
        now = timezone.now()
        upper = now + timedelta(days=max(days, 1))
        schedules = _visible_schedules_for_user(request.user).filter(start_at__gte=now, start_at__lte=upper)
        data = ScheduleSerializer(schedules, many=True).data
        return Response(status=status.HTTP_200_OK, data=data)


class ScheduleParticipantsView(APIView):
    def get(self, request, schedule_id, queryset=None, **kwargs):
        schedules = _visible_schedules_for_user(request.user)
        if not schedules.filter(id=schedule_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Schedule not found.'})
        participants = ScheduleParticipant.objects.filter(schedule_id=schedule_id).select_related('user', 'schedule')
        data = ScheduleParticipantSerializer(participants, many=True).data
        return Response(status=status.HTTP_200_OK, data=data)

    def post(self, request, schedule_id, queryset=None, **kwargs):
        schedules = _visible_schedules_for_user(request.user)
        if not schedules.filter(id=schedule_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Schedule not found.'})

        payload = request.data.copy()
        payload['schedule'] = schedule_id
        serializer = ScheduleParticipantSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class ScheduleParticipantDetailView(APIView):
    def get(self, request, pk, queryset=None, **kwargs):
        if not ScheduleParticipant.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Participant not found.'})
        participant = ScheduleParticipant.objects.select_related('schedule').get(id=pk)
        if not _visible_schedules_for_user(request.user).filter(id=participant.schedule_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Participant not found.'})
        return Response(status=status.HTTP_200_OK, data=ScheduleParticipantSerializer(participant).data)

    def put(self, request, pk, queryset=None, **kwargs):
        if not ScheduleParticipant.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Participant not found.'})
        participant = ScheduleParticipant.objects.select_related('schedule').get(id=pk)
        if not _visible_schedules_for_user(request.user).filter(id=participant.schedule_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Participant not found.'})
        serializer = ScheduleParticipantSerializer(participant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def delete(self, request, pk, queryset=None, **kwargs):
        if not ScheduleParticipant.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Participant not found.'})
        participant = ScheduleParticipant.objects.select_related('schedule').get(id=pk)
        if not _visible_schedules_for_user(request.user).filter(id=participant.schedule_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Participant not found.'})
        participant.delete()
        return Response(status=status.HTTP_200_OK, data={'message': 'Participant deleted.'})


class ScheduleRemindersView(APIView):
    def get(self, request, schedule_id, queryset=None, **kwargs):
        schedules = _visible_schedules_for_user(request.user)
        if not schedules.filter(id=schedule_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Schedule not found.'})
        reminders = ScheduleReminder.objects.filter(schedule_id=schedule_id).select_related('schedule', 'participant')
        data = ScheduleReminderSerializer(reminders, many=True).data
        return Response(status=status.HTTP_200_OK, data=data)

    def post(self, request, schedule_id, queryset=None, **kwargs):
        schedules = _visible_schedules_for_user(request.user)
        if not schedules.filter(id=schedule_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Schedule not found.'})

        payload = request.data.copy()
        payload['schedule'] = schedule_id
        serializer = ScheduleReminderSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class ScheduleReminderDetailView(APIView):
    def get(self, request, pk, queryset=None, **kwargs):
        if not ScheduleReminder.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Reminder not found.'})
        reminder = ScheduleReminder.objects.select_related('schedule').get(id=pk)
        if not _visible_schedules_for_user(request.user).filter(id=reminder.schedule_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Reminder not found.'})
        return Response(status=status.HTTP_200_OK, data=ScheduleReminderSerializer(reminder).data)

    def put(self, request, pk, queryset=None, **kwargs):
        if not ScheduleReminder.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Reminder not found.'})
        reminder = ScheduleReminder.objects.select_related('schedule').get(id=pk)
        if not _visible_schedules_for_user(request.user).filter(id=reminder.schedule_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Reminder not found.'})
        serializer = ScheduleReminderSerializer(reminder, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def delete(self, request, pk, queryset=None, **kwargs):
        if not ScheduleReminder.objects.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Reminder not found.'})
        reminder = ScheduleReminder.objects.select_related('schedule').get(id=pk)
        if not _visible_schedules_for_user(request.user).filter(id=reminder.schedule_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Reminder not found.'})
        reminder.delete()
        return Response(status=status.HTTP_200_OK, data={'message': 'Reminder deleted.'})


class ScheduleOccurrencesView(APIView):
    def get(self, request, pk, queryset=None, **kwargs):
        schedules = _visible_schedules_for_user(request.user)
        if not schedules.filter(id=pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Schedule not found.'})

        schedule = schedules.select_related('recurrence_rule').get(id=pk)
        start_from = _parse_dt_or_none(request.query_params.get('start'))
        end_at = _parse_dt_or_none(request.query_params.get('end'))
        count = int(request.query_params.get('count', 25))

        occurrences = _generate_occurrences(schedule, start_from=start_from, end_at=end_at, max_items=max(count, 1))
        return Response(status=status.HTTP_200_OK, data=occurrences)
