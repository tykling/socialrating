import logging

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

from utils.mixins import SRViewMixin, SRListViewMixin

from .models import Vote

logger = logging.getLogger("socialrating.%s" % __name__)


class VoteListView(SRListViewMixin, ListView):
    """
    List all votes belonging to a specific review
    """

    model = Vote
    paginate_by = 100
    template_name = "vote_list.html"
    permission_required = "vote.view_vote"


class VoteCreateView(SRViewMixin, CreateView):
    """
    This view allows the user to add new votes to an existing review.
    """

    model = Vote
    template_name = "vote_form.html"
    fields = ["rating", "vote", "comment"]
    permission_required = "review.add_vote"

    def get_form(self):
        """
        Filter Rating select to only show ratings which don't already have a Vote
        in this Review
        """
        form = super().get_form()
        form.fields["rating"].queryset = self.review.ratings_missing_votes()
        form.fields["rating"].empty_label = None
        return form

    def get_permission_object(self):
        """
        Only users with review.add_vote permission for
        self.review are allowed to create new Votes
        """
        return self.review

    def form_valid(self, form):
        vote = form.save(commit=False)
        vote.review = self.review
        vote.save()

        messages.success(self.request, "Saved new vote")

        # redirect to the vote list for the review
        return redirect(
            reverse(
                "team:category:item:review:vote:list",
                kwargs={
                    "team_slug": self.team.slug,
                    "category_slug": self.category.slug,
                    "item_slug": self.item.slug,
                    "review_uuid": self.review.pk,
                },
            )
        )


class VoteDetailView(SRViewMixin, DetailView):
    model = Vote
    template_name = "vote_detail.html"
    pk_url_kwarg = "vote_uuid"
    permission_required = "vote.view_vote"


class VoteSettingsView(SRViewMixin, DetailView):
    model = Vote
    template_name = "vote_settings.html"
    pk_url_kwarg = "vote_uuid"
    permission_required = "vote.change_vote"


class VoteUpdateView(SRViewMixin, UpdateView):
    model = Vote
    template_name = "vote_form.html"
    fields = ["vote", "comment"]
    pk_url_kwarg = "vote_uuid"
    permission_required = "vote.change_vote"

    def get_success_url(self):
        return reverse(
            "team:category:item:review:vote:detail",
            kwargs={
                "team_slug": self.team.slug,
                "category_slug": self.category.slug,
                "item_slug": self.item.slug,
                "review_uuid": self.review.pk,
                "vote_uuid": self.get_object().pk,
            },
        )


class VoteDeleteView(SRViewMixin, DeleteView):
    model = Vote
    template_name = "vote_delete.html"
    pk_url_kwarg = "vote_uuid"
    permission_required = "vote.delete_vote"

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Vote %s has been deleted" % self.get_object())
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
