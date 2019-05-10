import magic

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from guardian.mixins import PermissionListMixin, PermissionRequiredMixin

from review.mixins import ReviewSlugMixin
from utils.svgthumbnail import svgthumbnail
from .models import Attachment


class AttachmentListView(ReviewSlugMixin, PermissionListMixin, ListView):
    model = Attachment
    paginate_by = 100
    template_name = 'attachment_list.html'
    permission_required = 'attachment.view_attachment'

    def get_queryset(self):
        return super().get_queryset().filter(review=self.review)


class AttachmentView(ReviewSlugMixin, PermissionRequiredMixin, DetailView):
    """
    This view returns a http response with the file for an Attachment object,
    with the proper mimetype.
    TODO: Make the webserver serve the files
    """
    model = Attachment
    pk_url_kwarg = 'attachment_uuid'
    permission_required = 'attachment.view_attachment'

    def get(self, request, *args, **kwargs):
        # get attachment object
        attachment = self.get_object()

        # read file
        data = attachment.attachment.read()

        # find mimetype
        mimetype = magic.from_buffer(data, mime=True)

        if 'thumbnail' in request.GET:
            if mimetype[0:6] == "image/":
                # thumbnail requested but the file is an image, just
                # put the response together and return it!
                response = HttpResponse(content_type=mimetype)
                response.write(data)
            else:
                # thumbnail of non-image requested, return svg "icon"
                response = HttpResponse(content_type="image/svg+xml")
                response.write(svgthumbnail(mimetype))
        else:
            # no thumbnail requested, just return the file
            response = HttpResponse(content_type=mimetype)
            response.write(data)

        # all good
        return response


class AttachmentCreateView(ReviewSlugMixin, CreateView):
    model = Attachment
    template_name = 'attachment_form.html'
    fields = ['attachment', 'description']

    def setup(self, *args, **kwargs):
        """
        TODO: Figure out why PermissionRequiredMixin doesn't seem to work with CreateView
        """
        super().setup(*args, **kwargs)
        if not self.request.user.has_perms('attachment.add_attachment'):
            raise Http404

    def form_valid(self, form):
        attachment = form.save(commit=False)
        attachment.review=self.review
        attachment.save()

        messages.success(self.request, "Saved new attachment %s for review %s" % (
            attachment.pk,
            attachment.review,
        ))

        # redirect to the saved review
        return redirect(reverse(
            'team:category:item:review:attachment:list',
            kwargs={
                'team_slug': self.team.slug,
                'category_slug': self.category.slug,
                'item_slug': self.item.slug,
                'review_uuid': self.review.pk
            }
        ))


class AttachmentUpdateView(ReviewSlugMixin, PermissionRequiredMixin, UpdateView):
    model = Attachment
    template_name = 'attachment_form.html'
    fields = ['description']
    pk_url_kwarg = 'attachment_uuid'
    permission_required = 'attachment.change_attachment'

    def get_success_url(self):
        return(reverse('team:category:item:review:detail', kwargs={
            'team_slug': self.team.slug,
            'category_slug': self.category.slug,
            'item_slug': self.item.slug,
            'review_uuid': self.review.pk,
        }))


class AttachmentDeleteView(ReviewSlugMixin, PermissionRequiredMixin, DeleteView):
    model = Attachment
    template_name = 'attachment_delete.html'
    pk_url_kwarg = 'attachment_uuid'
    permission_required = 'attachment.delete_attachment'

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Attachment %s has been deleted" % self.get_object())
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return(reverse('team:category:item:review:detail', kwargs={
            'team_slug': self.team.slug,
            'category_slug': self.category.slug,
            'item_slug': self.item.slug,
            'review_uuid': self.review.pk,
        }))

