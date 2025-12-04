# accounts/signals.py
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from django.utils.module_loading import import_string

from .models import Doctor

@receiver(pre_save, sender=Doctor)
def delete_old_doctor_profile_image_on_change(sender, instance, **kwargs):
    """
    Delete old profile_image from storage when a new image file is uploaded
    or when profile_image is cleared.
    """
    if not instance.pk:
        return  # new instance, nothing to delete

    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_file = old.profile_image
    new_file = instance.profile_image

    # If old file exists and is different from new, delete it
    if old_file and old_file.name and (not new_file or old_file.name != getattr(new_file, 'name', None)):
        try:
            if default_storage.exists(old_file.name):
                default_storage.delete(old_file.name)
        except Exception:
            # log in production; swallow here to avoid breaking the request
            pass

@receiver(post_delete, sender=Doctor)
def delete_doctor_profile_image_on_delete(sender, instance, **kwargs):
    """
    Delete profile_image from storage when Doctor instance is deleted.
    """
    file_field = instance.profile_image
    if file_field and file_field.name:
        try:
            if default_storage.exists(file_field.name):
                default_storage.delete(file_field.name)
        except Exception:
            pass
