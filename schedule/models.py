from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class RecurrenceRule(models.Model):
	FREQUENCY_DAILY = 'daily'
	FREQUENCY_WEEKLY = 'weekly'
	FREQUENCY_MONTHLY = 'monthly'
	FREQUENCY_YEARLY = 'yearly'

	FREQUENCY_CHOICES = [
		(FREQUENCY_DAILY, 'Daily'),
		(FREQUENCY_WEEKLY, 'Weekly'),
		(FREQUENCY_MONTHLY, 'Monthly'),
		(FREQUENCY_YEARLY, 'Yearly'),
	]

	frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
	interval = models.PositiveIntegerField(default=1)
	by_weekday = models.CharField(
		max_length=64,
		blank=True,
		default='',
		help_text='Comma-separated weekdays (mon,tue,wed,thu,fri,sat,sun) for weekly recurrences.',
	)
	count = models.PositiveIntegerField(null=True, blank=True)
	until = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'{self.frequency} every {self.interval}'


class Schedule(models.Model):
	title = models.CharField(max_length=150)
	description = models.TextField(blank=True, default='')
	start_at = models.DateTimeField()
	end_at = models.DateTimeField()
	all_day = models.BooleanField(default=False)
	location = models.CharField(max_length=255, blank=True, default='')

	recurrence_rule = models.ForeignKey(
		RecurrenceRule,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='schedules',
	)

	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
	object_id = models.PositiveBigIntegerField(null=True, blank=True)
	content_object = GenericForeignKey('content_type', 'object_id')

	created_by = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='created_schedules',
	)
	is_cancelled = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['start_at']

	def __str__(self):
		return self.title


class ScheduleParticipant(models.Model):
	ROLE_ORGANIZER = 'organizer'
	ROLE_ATTENDEE = 'attendee'

	ACCEPTANCE_PENDING = 'pending'
	ACCEPTANCE_ACCEPTED = 'accepted'
	ACCEPTANCE_DECLINED = 'declined'
	ACCEPTANCE_TENTATIVE = 'tentative'

	ROLE_CHOICES = [
		(ROLE_ORGANIZER, 'Organizer'),
		(ROLE_ATTENDEE, 'Attendee'),
	]
	ACCEPTANCE_CHOICES = [
		(ACCEPTANCE_PENDING, 'Pending'),
		(ACCEPTANCE_ACCEPTED, 'Accepted'),
		(ACCEPTANCE_DECLINED, 'Declined'),
		(ACCEPTANCE_TENTATIVE, 'Tentative'),
	]

	schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='participants')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule_participations')
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ATTENDEE)
	acceptance_status = models.CharField(max_length=20, choices=ACCEPTANCE_CHOICES, default=ACCEPTANCE_PENDING)
	responded_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['schedule', 'user']
		constraints = [
			models.UniqueConstraint(fields=['schedule', 'user'], name='unique_schedule_participant')
		]

	def __str__(self):
		return f'{self.user} in {self.schedule}'


class ScheduleReminder(models.Model):
	CHANNEL_EMAIL = 'email'
	CHANNEL_PUSH = 'push'

	CHANNEL_CHOICES = [
		(CHANNEL_EMAIL, 'Email'),
		(CHANNEL_PUSH, 'Push'),
	]

	schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='reminders')
	participant = models.ForeignKey(
		ScheduleParticipant,
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='reminders',
		help_text='Optional participant-specific reminder. If empty, reminder applies to all participants.',
	)
	minutes_before = models.PositiveIntegerField(default=30)
	channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default=CHANNEL_EMAIL)
	is_sent = models.BooleanField(default=False)
	sent_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['schedule', 'minutes_before']

	def __str__(self):
		return f'{self.channel} reminder for {self.schedule} ({self.minutes_before} min)'
