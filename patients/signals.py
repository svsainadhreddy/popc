# patients/signals.py
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage

from .models import Patient

@receiver(pre_save, sender=Patient)
def delete_old_patient_photo_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_file = old.photo
    new_file = instance.photo

    if old_file and old_file.name and (not new_file or old_file.name != getattr(new_file, 'name', None)):
        try:
            if default_storage.exists(old_file.name):
                default_storage.delete(old_file.name)
        except Exception:
            pass

@receiver(post_delete, sender=Patient)
def delete_patient_photo_on_delete(sender, instance, **kwargs):
    file_field = instance.photo
    if file_field and file_field.name:
        try:
            if default_storage.exists(file_field.name):
                default_storage.delete(file_field.name)
        except Exception:
            pass
