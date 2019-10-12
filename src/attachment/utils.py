import magic


def save_form_attachments(form, fieldname, review):
    """
    Loop over any uploaded files and create an Attachment object for each
    """
    files = form.files.getlist("attachments")
    for attachment in files:
        mimetype = magic.from_buffer(attachment.read(), mime=True)
        saved = Attachment.objects.create(
            review=review,
            attachment=attachment,
            mimetype=mimetype,
            size=attachment.size,
        )
        print("saved attachment %s" % saved)
