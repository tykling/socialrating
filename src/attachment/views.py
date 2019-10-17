import magic

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from guardian.mixins import PermissionListMixin, PermissionRequiredMixin

from review.mixins import ReviewSlugMixin
from utils.svgthumbnail import svgthumbnail
from utils.mixins import PermissionRequiredOr403Mixin
from utils.mixins import BreadCrumbMixin as BCMixin

from .models import Attachment
from .mixins import AttachmentSlugMixin
from .utils import save_form_attachments


class AttachmentListView(ReviewSlugMixin, PermissionListMixin, BCMixin, ListView):
    """
    List all attachments belonging to a specific review
    """

    model = Attachment
    paginate_by = 100
    template_name = "attachment_list.html"
    permission_required = "attachment.view_attachment"

    def get_queryset(self):
        return super().get_queryset().filter(review=self.review)


class AttachmentCreateView(
    ReviewSlugMixin, PermissionRequiredOr403Mixin, BCMixin, CreateView
):
    """
    This view allows the user to add new attachments to an existing
    review.
    """

    model = Attachment
    template_name = "attachment_form.html"
    fields = ["attachment", "description"]
    permission_required = "review.add_attachment"

    def get_permission_object(self):
        """
        Only users with review.add_attachment permission for
        self.review are allowed to create new Attachments
        """
        return self.review

    def form_valid(self, form):
        attachment = form.save(commit=False)
        attachment.review = self.review
        attachment.mimetype = magic.from_buffer(attachment.attachment.read(), mime=True)
        attachment.size = attachment.attachment.size
        attachment.save()

        messages.success(self.request, "Saved new attachment")

        # redirect to the attachment list for the review
        return redirect(
            reverse(
                "team:category:item:review:attachment:list",
                kwargs={
                    "team_slug": self.team.slug,
                    "category_slug": self.category.slug,
                    "item_slug": self.item.slug,
                    "review_uuid": self.review.pk,
                },
            )
        )


class AttachmentDetailView(
    AttachmentSlugMixin, PermissionRequiredOr403Mixin, BCMixin, DetailView
):
    model = Attachment
    template_name = "attachment_detail.html"
    pk_url_kwarg = "attachment_uuid"
    permission_required = "attachment.view_attachment"


class AttachmentSettingsView(
    AttachmentSlugMixin, PermissionRequiredOr403Mixin, BCMixin, DetailView
):
    model = Attachment
    template_name = "attachment_settings.html"
    pk_url_kwarg = "attachment_uuid"
    permission_required = "attachment.change_attachment"


class AttachmentFileView(
    AttachmentSlugMixin, PermissionRequiredOr403Mixin, BCMixin, DetailView
):
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


class AttachmentUpdateView(
    AttachmentSlugMixin, PermissionRequiredOr403Mixin, BCMixin, UpdateView
):
    """
    View to update the description of an existing Attachment
    """

    model = Attachment
    template_name = "attachment_form.html"
    fields = ["description"]
    pk_url_kwarg = "attachment_uuid"
    permission_required = "attachment.change_attachment"

    def get_success_url(self):
        return reverse(
            "team:category:item:review:attachment:detail",
            kwargs={
                "team_slug": self.team.slug,
                "category_slug": self.category.slug,
                "item_slug": self.item.slug,
                "review_uuid": self.review.pk,
                "attachment_uuid": self.get_object().pk,
            },
        )


class AttachmentDeleteView(
    AttachmentSlugMixin, PermissionRequiredOr403Mixin, BCMixin, DeleteView
):
    model = Attachment
    template_name = "attachment_delete.html"
    pk_url_kwarg = "attachment_uuid"
    permission_required = "attachment.delete_attachment"

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Attachment %s has been deleted" % self.get_object())
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "team:category:item:review:detail",
            kwargs={
                "team_slug": self.team.slug,
                "category_slug": self.category.slug,
                "item_slug": self.item.slug,
                "review_uuid": self.review.pk,
            },
        )
