import magic

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages

from utils.svgthumbnail import svgthumbnail
from utils.mixins import SRViewMixin, SRListViewMixin

from .models import Attachment


class AttachmentListView(SRListViewMixin, ListView):
    """
    List all attachments belonging to a specific review
    """

    model = Attachment
    paginate_by = 100
    template_name = "attachment_list.html"
    permission_required = "attachment.view_attachment"

    def get_queryset(self, **kwargs):
        """
        We have a GenericRelation called "attachments"
        """
        print("inside attachmentlistview for object %s" % self.gfk_object)
        attachments = self.gfk_object.attachments.all()
        self.checker.prefetch_perms(attachments)
        return attachments


class AttachmentCreateView(SRViewMixin, CreateView):
    """
    This view allows the user to add new attachments to an existing item
    """

    model = Attachment
    template_name = "attachment_form.html"
    fields = ["attachment", "description"]
    permission_required = "add_attachment"

    def get_permission_object(self):
        """
        Only users with review.add_attachment permission for
        self.review are allowed to create new Attachments
        """
        return self.gfk_object

    def form_valid(self, form):
        attachment = form.save(commit=False)
        attachment.actor = self.request.user.actor
        attachment.mimetype = magic.from_buffer(attachment.attachment.read(), mime=True)
        attachment.size = attachment.attachment.size
        attachment.attachment_object = self.gfk_object
        attachment.save()

        messages.success(self.request, "Saved new attachment")

        # redirect to the attachment list for the item
        return redirect(self.gfk_object.get_absolute_url())


class AttachmentDetailView(SRViewMixin, DetailView):
    model = Attachment
    template_name = "attachment_detail.html"
    pk_url_kwarg = "attachment_uuid"
    permission_required = "attachment.view_attachment"


class AttachmentSettingsView(SRViewMixin, DetailView):
    model = Attachment
    template_name = "attachment_settings.html"
    pk_url_kwarg = "attachment_uuid"
    permission_required = "attachment.change_attachment"


class AttachmentFileView(SRViewMixin, DetailView):
    """
    This view returns a http response with the contents of the file
    and the proper mimetype.
    It can also return a thumbnail instead of the actual file.
    TODO: Make the webserver serve the files
    """

    model = Attachment
    pk_url_kwarg = "attachment_uuid"
    permission_required = "attachment.view_attachment"

    def get(self, request, *args, **kwargs):
        if "thumbnail" in request.GET and self.attachment.mimetype[0:6] != "image/":
            # thumbnail of non-image requested, return svg "icon"
            response = HttpResponse(content_type="image/svg+xml")
            response.write(svgthumbnail(self.attachment.mimetype))
        else:
            # no thumbnail requested, or mimetype is an image, just return the file
            response = HttpResponse(content_type=self.attachment.mimetype)
            response.write(self.attachment.attachment.read())

        # all good
        return response


class AttachmentUpdateView(SRViewMixin, UpdateView):
    """
    View to update the description of an existing Attachment
    """

    model = Attachment
    template_name = "attachment_form.html"
    fields = ["description"]
    pk_url_kwarg = "attachment_uuid"
    permission_required = "attachment.change_attachment"

    def get_success_url(self):
        return self.attachment.get_detail_url


class AttachmentDeleteView(SRViewMixin, DeleteView):
    model = Attachment
    template_name = "attachment_delete.html"
    pk_url_kwarg = "attachment_uuid"
    permission_required = "attachment.delete_attachment"

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Attachment %s has been deleted" % self.get_object())
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.attachment.attachment_object.get_absolute_url()
