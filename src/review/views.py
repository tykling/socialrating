from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django import forms
from django.shortcuts import redirect, reverse

from item.mixins import ItemViewMixin
from rating.models import Vote
from team.mixins import TeamViewMixin
from context.models import Context

from .models import Review


class ReviewListView(ItemViewMixin, ListView):
    model = Review
    paginate_by = 100
    template_name = 'review_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(item=self.item)


class ReviewCreateView(TeamViewMixin, ItemViewMixin, CreateView):
    model = Review
    template_name = 'review_form.html'
    fields = ['headline', 'body', 'context']

    def get_context_data(self):
        """
        Add Item to the context
        """
        context = super().get_context_data()
        context['item'] = self.item
        return context

    def get_form(self, form_class=None):
        """
        Add ratings to the form and set initial Context
        QuerySet
        """
        form = super().get_form(form_class)
        for rating in self.item.category.ratings.all():
            choices = []
            for choice in range(1, rating.max_rating+1):
                choices.append((choice, choice))
            form.fields["%s_vote" % rating.slug] = forms.TypedChoiceField(
                choices=choices,
                coerce=int,
                widget=forms.widgets.RadioSelect,
                required=False,
                label='%s: Please vote between 1-%s' % (rating.name, rating.max_rating),
            )
            form.fields["%s_comment" % rating.slug] = forms.CharField(
                label='%s: A short comment for the Vote above' % rating.name,
                required=False,
            )
            form.fields['context'].queryset = Context.objects.filter(team=self.team)
        return form

    def form_valid(self, form):
        """
        First save the new Review,
        then save any Votes, Attachments and Tags.
        """
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
                Vote.objects.create(
                    review=review,
                    rating=rating,
                    vote=form.cleaned_data[votefield],
                    comment=form.cleaned_data[commentfield] if commentfield in form.cleaned_data else '',
                )

        return redirect(reverse(
            'team:category:item:review:detail',
            kwargs={
                'team_slug': self.team.slug,
                'category_slug': self.item.category.slug,
                'item_slug': self.item.slug,
                'review_uuid': review.pk
            }
        ))


class ReviewDetailView(ItemViewMixin, DetailView):
    model = Review
    template_name = 'review_detail.html'
    pk_url_kwarg = 'review_uuid'


class ReviewUpdateView(ItemViewMixin, UpdateView):
    model = Review
    template_name = 'review_form.html'
    pk_url_kwarg = 'review_uuid'
    fields = ['headline', 'body', 'context']


class ReviewDeleteView(ItemViewMixin, DeleteView):
    model = Review
    template_name = 'review_delete.html'
    pk_url_kwarg = 'review_uuid'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Review %s has been deleted, along with all Votes that related to it." % self.get_object())
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return(reverse('team:category:item:detail', kwargs={
            'camp_slug': self.camp.slug,
            'category_slug': self.category.slug,
            'item_slug': self.item.slug,
        }))

