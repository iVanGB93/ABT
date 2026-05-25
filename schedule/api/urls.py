from django.urls import path

from schedule.api.views import (
    RecurrenceRuleDetailView,
    RecurrenceRuleListCreateView,
    ScheduleDetailView,
    ScheduleListCreateView,
    ScheduleOccurrencesView,
    ScheduleParticipantDetailView,
    ScheduleParticipantsView,
    ScheduleRangeView,
    ScheduleReminderDetailView,
    ScheduleRemindersView,
    ScheduleTodayView,
    ScheduleUpcomingView,
)

app_name = 'schedule-api'

urlpatterns = [
    path('recurrence-rules/', RecurrenceRuleListCreateView.as_view(), name='recurrence_rule_list_create'),
    path('recurrence-rules/<int:pk>/', RecurrenceRuleDetailView.as_view(), name='recurrence_rule_detail'),
    path('list/', ScheduleListCreateView.as_view(), name='schedule_list'),
    path('create/', ScheduleListCreateView.as_view(), name='schedule_create'),
    path('detail/<int:pk>/', ScheduleDetailView.as_view(), name='schedule_detail'),
    path('update/<int:pk>/', ScheduleDetailView.as_view(), name='schedule_update'),
    path('delete/<int:pk>/', ScheduleDetailView.as_view(), name='schedule_delete'),
    path('range/', ScheduleRangeView.as_view(), name='schedule_range'),
    path('today/', ScheduleTodayView.as_view(), name='schedule_today'),
    path('upcoming/', ScheduleUpcomingView.as_view(), name='schedule_upcoming'),
    path('occurrences/<int:pk>/', ScheduleOccurrencesView.as_view(), name='schedule_occurrences'),
    path('participants/<int:schedule_id>/', ScheduleParticipantsView.as_view(), name='participant_list_create'),
    path('participants/detail/<int:pk>/', ScheduleParticipantDetailView.as_view(), name='participant_detail'),
    path('participants/update/<int:pk>/', ScheduleParticipantDetailView.as_view(), name='participant_update'),
    path('participants/delete/<int:pk>/', ScheduleParticipantDetailView.as_view(), name='participant_delete'),
    path('reminders/<int:schedule_id>/', ScheduleRemindersView.as_view(), name='reminder_list_create'),
    path('reminders/detail/<int:pk>/', ScheduleReminderDetailView.as_view(), name='reminder_detail'),
    path('reminders/update/<int:pk>/', ScheduleReminderDetailView.as_view(), name='reminder_update'),
    path('reminders/delete/<int:pk>/', ScheduleReminderDetailView.as_view(), name='reminder_delete'),
]
