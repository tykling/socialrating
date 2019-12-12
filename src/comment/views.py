from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect

from utils.mixins import SRViewMixin, SRListViewMixin

from .models import Comment


class CommentListView(SRListViewMixin, ListView):
    model = Comment
    paginate_by = 100
    template_name = "comment_list.html"
    permission_required = "comment.view_comment"

    def get_queryset(self, **kwargs):
        """
        We have a GenericRelation called "comments"
        """
        comments = self.gfk_object.comments.filter(reply_to__isnull=True)
        self.checker.prefetch_perms(comments)
        return comments


class CommentCreateView(SRViewMixin, CreateView):
    model = Comment
    template_name = "comment_form.html"
    fields = ["subject", "body"]
    permission_required = "add_comment"

    def get_permission_object(self):
        """
        Only users with add_comment permission for the gfk object are
        allowed to create new Comments
        """
        return self.gfk_object

    def form_valid(self, form):
        """
        Set the comment object and actor and save
        """
        comment = form.save(commit=False)
        comment.actor = self.request.user.actor
        if hasattr(self, "comment"):
            comment.reply_to = self.comment
            comment.comment_object = self.comment.comment_object
        else:
            comment.comment_object = self.gfk_object
        comment.save()
        messages.success(self.request, "New comment created!")
        return redirect(comment.get_absolute_url())


class CommentDetailView(SRViewMixin, DetailView):
    model = Comment
    template_name = "comment_detail.html"
    pk_url_kwarg = "comment_uuid"
    permission_required = "comment.view_comment"


class CommentSettingsView(SRViewMixin, DetailView):
    model = Comment
    template_name = "comment_settings.html"
    pk_url_kwarg = "comment_uuid"
    permission_required = "comment.change_comment"


class CommentUpdateView(SRViewMixin, UpdateView):
    model = Comment
    template_name = "comment_form.html"
    fields = ["subject", "body"]
    pk_url_kwarg = "comment_uuid"
    permission_required = "comment.change_comment"

    def form_valid(self, form):
        comment = form.save()
        messages.success(self.request, "Comment updated!")
        return redirect(comment.get_absolute_url())


class CommentDeleteView(SRViewMixin, DeleteView):
    model = Comment
    template_name = "comment_delete.html"
    pk_url_kwarg = "comment_uuid"
    permission_required = "comment.delete_comment"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Comment has been deleted")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.get_object().comment_object.get_absolute_url()
