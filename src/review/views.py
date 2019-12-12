import logging

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django import forms
from django.shortcuts import redirect, reverse
from django.db import transaction
from django.contrib import messages

from context.models import Context
from attachment.utils import save_form_attachments
from vote.models import Vote
from utils.mixins import SRViewMixin, SRListViewMixin

from .models import Review

logger = logging.getLogger("socialrating.%s" % __name__)


class ReviewListView(SRListViewMixin, ListView):
    model = Review
    paginate_by = 100
    template_name = "review_list.html"
    permission_required = "review.view_review"


class ReviewCreateView(SRViewMixin, CreateView):
    model = Review
    template_name = "review_form.html"
    fields = ["headline", "body", "context"]
    permission_required = "item.add_review"

    def get_permission_object(self):
        """
        Only users with item.add_review permission for self.item are
        allowed to create new Reviews here
        """
        return self.item

    def get_context_data(self, **kwargs):
        """
        Add Item to the context
        """
        context = super().get_context_data(**kwargs)
        context["item"] = self.item
        return context

    def get_form(self, form_class=None):
        """
        Add ratings to the form and set initial Context QuerySet
        """
        form = super().get_form(form_class)
        for rating in self.item.category.ratings.all():
            choices = []
            for choice in range(1, rating.max_rating + 1):
                choices.append((choice, choice))
            form.fields["%s_vote" % rating.slug] = forms.TypedChoiceField(
                choices=choices,
                coerce=int,
                widget=forms.widgets.RadioSelect,
                required=False,
                label="%s: Please vote between 1-%s" % (rating.name, rating.max_rating),
            )
            form.fields["%s_comment" % rating.slug] = forms.CharField(
                label="%s: A short comment for the Vote above" % rating.name,
                required=False,
            )

        # set queryset for context, only show Contexts for this Team
        form.fields["context"].queryset = Context.objects.filter(team=self.team)
        if self.category.default_context:
            # no need for an empty item in the context picker when we have a default
            form.fields["context"].empty_label = None

        # add attachments field (support multiple files)
        form.fields["attachments"] = forms.FileField(
            widget=forms.ClearableFileInput(attrs={"multiple": True}),
            label="Attach files to the Review (descriptions can be added after upload)",
            required=False,
        )

        return form

    def get_initial(self):
        """
        Set initial Context if this category has a default_context
        """
        initial = super().get_initial()
        if self.category.default_context:
            initial["context"] = self.category.default_context
        return initial

    def form_valid(self, form):
        """
        First save the new Review, then save any Votes, Attachments and
        Tags.
        """
        # save everything in a single transaction so we save it all or nothing
        with transaction.atomic():
            review = form.save(commit=False)
            review.item = self.item
            review.actor = self.request.user.actor
            review.save()

            # loop over ratings available for this item,
            # saving a new Vote for each as needed
            for rating in self.item.category.ratings.all():
                votefield = "%s_vote" % rating.slug
                commentfield = "%s_comment" % rating.slug
                if votefield in form.fields and form.cleaned_data[votefield]:
                    # do we have a comment for this vote?
                    if commentfield in form.cleaned_data:
                        comment = form.cleaned_data[commentfield]
                    else:
                        comment = ""
                    # create the Vote object
                    Vote.objects.create(
                        review=review,
                        rating=rating,
                        vote=form.cleaned_data[votefield],
                        comment=comment,
                    )

            # save any attachments
            if form.is_multipart():
                save_form_attachments(
                    form=form, fieldname="attachments", gfk_object=review
                )

        # all done
        messages.success(
            self.request,
            "Saved review %s (%s votes, %s attachments)"
            % (review.pk, review.votes.count(), review.attachments.count()),
        )

        # redirect to the saved review
        return redirect(
            reverse(
                "team:category:item:review:detail",
                kwargs={
                    "team_slug": self.team.slug,
                    "category_slug": self.item.category.slug,
                    "item_slug": self.item.slug,
                    "review_uuid": review.pk,
                },
            )
        )


class ReviewDetailView(SRViewMixin, DetailView):
    model = Review
    template_name = "review_detail.html"
    pk_url_kwarg = "review_uuid"
    permission_required = "review.view_review"


class ReviewSettingsView(SRViewMixin, DetailView):
    model = Review
    template_name = "review_settings.html"
    pk_url_kwarg = "review_uuid"
    permission_required = "review.change_review"


class ReviewUpdateView(SRViewMixin, UpdateView):
    model = Review
    template_name = "review_form.html"
    pk_url_kwarg = "review_uuid"
    fields = ["headline", "body", "context"]
    permission_required = "review.change_review"

    def get_form(self, form_class=None):
        """
        - Add ratings to the form
        - Set initial Context QuerySet
        - Add attachments FileField to the form
        - TODO: Add tags field to the form
        """
        form = super().get_form(form_class)
        for rating in self.item.category.ratings.all():
            # make a list of choices
            choices = []
            for choice in range(1, rating.max_rating + 1):
                choices.append((choice, choice))

            try:
                vote = Vote.objects.get(review=self.get_object(), rating=rating)
            except Vote.DoesNotExist:
                vote = None

            # add the TypedChoiceField
            form.fields["%s_vote" % rating.slug] = forms.TypedChoiceField(
                choices=choices,
                coerce=int,
                widget=forms.widgets.RadioSelect,
                required=False,
                initial=vote.vote if vote else None,
                label="%s: Please vote between 1-%s" % (rating.name, rating.max_rating),
            )

            # add the comment CharField
            form.fields["%s_comment" % rating.slug] = forms.CharField(
                required=False,
                initial=vote.comment if vote else "",
                label="%s: A short comment for the Vote above" % rating.name,
            )

            # set the list of Contexts for this team
            form.fields["context"].queryset = Context.objects.filter(team=self.team)

        return form

    def get_context_data(self, **kwargs):
        """
        Add Item to the context
        """
        context = super().get_context_data(**kwargs)
        context["item"] = self.item
        return context

    def form_valid(self, form):
        """
        First save the Review,
        then save any Votes, Attachments and Tags.
        """
        if form.has_changed():
            review = form.save()

            # loop over ratings available for this item,
            # creating or updating a Vote for each as needed
            for rating in self.item.category.ratings.all():
                votefield = "%s_vote" % rating.slug
                commentfield = "%s_comment" % rating.slug
                if votefield in form.fields and form.cleaned_data[votefield]:
                    # does this vote already in database?
                    if Vote.objects.filter(
                        review=review,
                        rating=rating,
                        vote=form.cleaned_data[votefield],
                        comment=form.cleaned_data[commentfield]
                        if commentfield in form.cleaned_data
                        else "",
                    ).exists():
                        # this vote already exists in the database, no need to save it again
                        # TODO: when does this happen?
                        continue

                    # we either need to create a new Vote or update an existing
                    vote, created = Vote.objects.update_or_create(
                        review=review,
                        rating=rating,
                        defaults={
                            "vote": form.cleaned_data[votefield],
                            "comment": form.cleaned_data[commentfield]
                            if commentfield in form.cleaned_data
                            else "",
                        },
                    )

        # all done
        messages.success(
            self.request,
            "Updated review %s (%s votes, %s attachments)"
            % (review.pk, review.votes.count(), review.attachments.count()),
        )

        return redirect(
            reverse(
                "team:category:item:review:detail",
                kwargs={
                    "team_slug": self.team.slug,
                    "category_slug": self.item.category.slug,
                    "item_slug": self.item.slug,
                    "review_uuid": self.get_object().pk,
                },
            )
        )


class ReviewDeleteView(SRViewMixin, DeleteView):
    model = Review
    template_name = "review_delete.html"
    pk_url_kwarg = "review_uuid"
    permission_required = "review.delete_review"

    def delete(self, request, *args, **kwargs):
        messages.success(
            self.request,
            "Review has been deleted, along with all Votes, Attachments and Tags that related to it.",
        )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "team:category:item:review:list",
            kwargs={
                "team_slug": self.team.slug,
                "category_slug": self.category.slug,
                "item_slug": self.item.slug,
            },
        )
