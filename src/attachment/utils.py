import magic

from django.contrib.contenttypes.models import ContentType

from .models import Attachment


def save_form_attachments(form, fieldname, gfk_object):
    """
    Loop over any uploaded files and create an Attachment object for each
    """
    files = form.files.getlist("attachments")
    for attachment in files:
        mimetype = magic.from_buffer(attachment.read(), mime=True)
        saved = Attachment.objects.create(
            actor=gfk_object.actor,
            content_type=ContentType.objects.get_for_model(gfk_object),
            object_id=gfk_object.pk,
            attachment=attachment,
            mimetype=mimetype,
            size=attachment.size,
        )
        print("saved attachment %s" % saved)
