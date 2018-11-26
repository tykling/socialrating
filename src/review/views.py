from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from item.mixins import ItemViewMixin
from .models import Review


class ReviewListView(ItemViewMixin, ListView):
    model = Review
    paginate_by = 100
    template_name = 'review_list.html'

    def get_queryset(self):
        return super().get_queryset().filter(item=self.item)


class ReviewCreateView(ItemViewMixin, CreateView):
    model = Review
    template_name = 'review_form.html'


class ReviewDetailView(ItemViewMixin, DetailView):
    model = Review
    template_name = 'review_detail.html'
    pk_url_kwarg = 'review_uuid'


class ReviewUpdateView(ItemViewMixin, UpdateView):
    model = Review
    template_name = 'review_form.html'
    pk_url_kwarg = 'review_uuid'


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

