from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from utils.mixins import SRViewMixin, SRListViewMixin

from .models import Event


class EventListView(SRListViewMixin, ListView):
    model = Event
    paginate_by = 100
    template_name = "event_list.html"
    permission_required = "event.view_event"


class EventDetailView(SRViewMixin, DetailView):
    model = Event
    template_name = "event_detail.html"
    slug_url_kwarg = "event_slug"
    permission_required = "event.view_event"
