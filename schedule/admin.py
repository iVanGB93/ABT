from django.contrib import admin

from schedule.models import RecurrenceRule, Schedule, ScheduleParticipant, ScheduleReminder


class ScheduleParticipantInline(admin.TabularInline):
	model = ScheduleParticipant
	extra = 1
	autocomplete_fields = ['user']


class ScheduleReminderInline(admin.TabularInline):
	model = ScheduleReminder
	extra = 1
	autocomplete_fields = ['participant']


@admin.register(RecurrenceRule)
class RecurrenceRuleAdmin(admin.ModelAdmin):
	list_display = ('id', 'frequency', 'interval', 'count', 'until', 'created_at')
	list_filter = ('frequency',)
	search_fields = ('frequency', 'by_weekday')
	readonly_fields = ('created_at', 'updated_at')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'title',
		'start_at',
		'end_at',
		'created_by',
		'is_cancelled',
		'content_type',
		'object_id',
	)
	list_filter = ('is_cancelled', 'all_day', 'content_type')
	search_fields = ('title', 'description', 'location')
	readonly_fields = ('created_at', 'updated_at')
	autocomplete_fields = ('created_by', 'recurrence_rule')
	inlines = [ScheduleParticipantInline, ScheduleReminderInline]


@admin.register(ScheduleParticipant)
class ScheduleParticipantAdmin(admin.ModelAdmin):
	list_display = ('id', 'schedule', 'user', 'role', 'acceptance_status', 'responded_at')
	list_filter = ('role', 'acceptance_status')
	search_fields = ('schedule__title', 'user__username', 'user__email')
	autocomplete_fields = ('schedule', 'user')
	readonly_fields = ('created_at', 'updated_at')


@admin.register(ScheduleReminder)
class ScheduleReminderAdmin(admin.ModelAdmin):
	list_display = ('id', 'schedule', 'participant', 'minutes_before', 'channel', 'is_sent', 'sent_at')
	list_filter = ('channel', 'is_sent')
	search_fields = ('schedule__title', 'participant__user__username', 'participant__user__email')
	autocomplete_fields = ('schedule', 'participant')
	readonly_fields = ('created_at', 'updated_at')
