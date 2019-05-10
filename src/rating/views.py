from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, reverse
from django.contrib import messages

from category.mixins import CategorySlugMixin
from .models import Rating


class RatingListView(CategorySlugMixin, ListView):
    model = Rating
    paginate_by = 100
    template_name = 'rating_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(category=self.category)


class RatingCreateView(CategorySlugMixin, CreateView):
    model = Rating
    template_name = 'rating_form.html'
    fields = ['name', 'description', 'max_rating', 'icon']

    def form_valid(self, form):
        """
        Set the category
        """
        rating = form.save(commit=False)
        rating.category = self.category
        rating.save()
        messages.success(self.request, "New rating created!")
        return redirect(reverse('team:category:rating:list', kwargs={'team_slug': self.team.slug, 'category_slug': self.category.slug}))


class RatingDetailView(CategorySlugMixin, DetailView):
    model = Rating
    template_name = 'rating_detail.html'
    slug_url_kwarg = 'rating_slug'


class RatingUpdateView(CategorySlugMixin, UpdateView):
    model = Rating
    template_name = 'rating_form.html'
    slug_url_kwarg = 'rating_slug'
    fields = ['name', 'description', 'icon']


class RatingDeleteView(CategorySlugMixin, DeleteView):
    model = Rating
    template_name = 'review_delete.html'
    slug_url_kwarg = 'rating_slug'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Rating %s has been deleted, along with all Votes that related to it." % self.get_object())
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return(reverse('team:category:detail', kwargs={
            'camp_slug': self.camp.slug,
            'category_slug': self.category.slug,
        }))

