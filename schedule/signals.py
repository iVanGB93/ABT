from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from job.models import Job
from schedule.models import Schedule


@receiver(post_save, sender=Job)
def create_or_update_schedule_for_job(sender, instance, **kwargs):
    if not instance.scheduled_at:
        return

    content_type = ContentType.objects.get_for_model(Job)
    defaults = {
        'title': instance.description,
        'description': f'Job for {instance.client}',
        'start_at': instance.scheduled_at,
        'end_at': instance.scheduled_at + timedelta(hours=1),
        'all_day': False,
        'location': instance.address,
        'created_by': instance.provider,
        'is_cancelled': instance.status == 'cancelled',
    }

    Schedule.objects.update_or_create(
        content_type=content_type,
        object_id=instance.id,
        defaults=defaults,
    )
