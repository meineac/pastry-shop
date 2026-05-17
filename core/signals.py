from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from .models import Tag

from cms.models import News, Vacancy, QaA, Review

# Senders for m2m_changed are the hidden auto-generated through models
M2M_SENDERS = [
    News.tags.through,
    Vacancy.tags.through,
    QaA.tags.through,
    Review.tags.through,
]

@receiver(m2m_changed, sender=M2M_SENDERS[0])
@receiver(m2m_changed, sender=M2M_SENDERS[1])
@receiver(m2m_changed, sender=M2M_SENDERS[2])
@receiver(m2m_changed, sender=M2M_SENDERS[3])
def cleanup_orphaned_tags_m2m(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action in ('post_remove', 'post_clear'):
        tags_to_check = Tag.objects.all() if action == 'post_clear' else Tag.objects.filter(pk__in=pk_set)
        for tag in tags_to_check:
            # Check if this tag is still related to any objects across the project
            # This is a generic approach since related names exist for tags across multiple models.
            is_orphaned = True
            for related_object in tag._meta.related_objects:
                accessor_name = related_object.get_accessor_name()
                related_manager = getattr(tag, accessor_name, None)
                if related_manager and related_manager.exists():
                    is_orphaned = False
                    break

            if is_orphaned:
                tag.delete()


DELETE_SENDERS = [News, Vacancy, QaA, Review]

@receiver(pre_delete, sender=DELETE_SENDERS[0])
@receiver(pre_delete, sender=DELETE_SENDERS[1])
@receiver(pre_delete, sender=DELETE_SENDERS[2])
@receiver(pre_delete, sender=DELETE_SENDERS[3])
def cleanup_orphaned_tags_on_delete(sender, instance, **kwargs):
    # Try to find many-to-many fields that point to Tag
    for field in instance._meta.many_to_many:
        if field.related_model == Tag:
            tags = getattr(instance, field.name).all()
            for tag in tags:
                # We need to manually check if this is the ONLY instance using this tag
                is_orphaned = True
                for related_object in tag._meta.related_objects:
                    accessor_name = related_object.get_accessor_name()
                    related_manager = getattr(tag, accessor_name, None)
                    if related_manager:
                        # Exclude the current instance that is about to be deleted
                        if related_manager.exclude(pk=instance.pk).exists():
                            is_orphaned = False
                            break
                if is_orphaned:
                    tag.delete()
