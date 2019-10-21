import os


def get_attachment_path(instance, filename):
    """
    Return full path to use for saving the file
    """
    return os.path.join("attachments", str(instance.uuid), filename)
