import logging

import django.views.generic
from django.shortcuts import get_object_or_404, reverse
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from guardian.core import ObjectPermissionChecker
from guardian.mixins import PermissionRequiredMixin

from team.models import Team
from category.models import Category
from context.models import Context
from forum.models import Forum
from thread.models import Thread
from fact.models import Fact
from rating.models import Rating
from item.models import Item
from review.models import Review
from vote.models import Vote
from comment.models import Comment
from event.models import Event
from attachment.models import Attachment

logger = logging.getLogger("socialrating.%s" % __name__)


class SlugObjectsMixin:
    """
    A mixin to get objects from url slugs.
    Also adds breadcrumbs based on the objects we have and the view we are in.
    """

    def setup(self, *args, **kwargs):
        # super setup() so we have self.request available
        super().setup(*args, **kwargs)

        # add a checker we can use to cache permissions for objects
        self.checker = ObjectPermissionChecker(self.request.user)

        # start out with an almost empty context_data dict
        self.context_data = {"checker": self.checker}

        # do we have a team?
        if "team_slug" in kwargs:
            self.team = get_object_or_404(Team, slug=kwargs["team_slug"])
            self.checker.prefetch_perms([self.team])
            if not self.checker.has_perm("team.view_team", self.team):
                raise PermissionDenied
            self.url_namespace_prefixes = ["team"]
            self.add_breadcrumbs(self.team)
            self.url_kwargs = {"team_slug": self.team.slug}
            self.object_kwargs = {"team": self.team}
            self.context_data["team"] = self.team
            self.context_data["team_perms"] = self.checker.get_perms(self.team)
            self.gfk_object = self.team

            # do we have a context?
            if "context_slug" in kwargs:
                self.context = get_object_or_404(
                    Context, team=self.team, slug=self.kwargs["context_slug"]
                )
                self.checker.prefetch_perms([self.context])
                if not self.checker.has_perm("context.view_context", self.context):
                    raise PermissionDenied
                self.url_namespace_prefixes.append("context")
                self.add_breadcrumbs(self.context)
                self.url_kwargs["context_slug"] = self.context.slug
                self.context_data["context"] = self.context
                self.context_data["context_perms"] = self.checker.get_perms(
                    self.context
                )
                self.gfk_object = self.context

            # do we have a category?
            if "category_slug" in kwargs:
                self.category = get_object_or_404(
                    Category, team=self.team, slug=self.kwargs["category_slug"]
                )
                self.checker.prefetch_perms([self.category])
                if not self.checker.has_perm("category.view_category", self.category):
                    raise PermissionDenied
                self.url_namespace_prefixes.append("category")
                self.add_breadcrumbs(self.category)
                self.url_kwargs["category_slug"] = self.category.slug
                self.context_data["category"] = self.category
                self.context_data["category_perms"] = self.checker.get_perms(
                    self.category
                )
                self.gfk_object = self.category

                # do we have a fact?
                if "fact_slug" in kwargs:
                    self.fact = get_object_or_404(
                        Fact, category=self.category, slug=self.kwargs["fact_slug"]
                    )
                    self.checker.prefetch_perms([self.fact])
                    if not self.checker.has_perm("fact.view_fact", self.fact):
                        raise PermissionDenied
                    self.url_namespace_prefixes.append("fact")
                    self.add_breadcrumbs(self.fact)
                    self.context_data["fact"] = self.fact
                    self.context_data["fact_perms"] = self.checker.get_perms(self.fact)
                    self.gfk_object = self.fact

                # do we have a rating?
                elif "rating_slug" in kwargs:
                    self.rating = get_object_or_404(
                        Rating, category=self.category, slug=self.kwargs["rating_slug"]
                    )
                    self.checker.prefetch_perms([self.rating])
                    if not self.checker.has_perm("rating.view_rating", self.rating):
                        raise PermissionDenied
                    self.url_namespace_prefixes.append("rating")
                    self.add_breadcrumbs(self.rating)
                    self.context_data["rating"] = self.rating
                    self.context_data["rating_perms"] = self.checker.get_perms(
                        self.rating
                    )
                    self.gfk_object = self.rating

                # do we have an item?
                elif "item_slug" in kwargs:
                    self.item = get_object_or_404(
                        Item, category=self.category, slug=self.kwargs["item_slug"]
                    )
                    self.checker.prefetch_perms([self.item])
                    if not self.checker.has_perm("item.view_item", self.item):
                        raise PermissionDenied
                    self.url_namespace_prefixes.append("item")
                    self.add_breadcrumbs(self.item)
                    self.url_kwargs["item_slug"] = self.item.slug
                    self.context_data["item"] = self.item
                    self.context_data["item_perms"] = self.checker.get_perms(self.item)
                    self.gfk_object = self.item

                    # do we have a review?
                    if "review_uuid" in kwargs:
                        self.review = get_object_or_404(
                            Review, item=self.item, uuid=self.kwargs["review_uuid"]
                        )
                        self.checker.prefetch_perms([self.review])
                        if not self.checker.has_perm("review.view_review", self.review):
                            raise PermissionDenied
                        self.url_namespace_prefixes.append("review")
                        self.add_breadcrumbs(self.review)
                        self.url_kwargs["review_uuid"] = self.review.uuid
                        self.context_data["review"] = self.review
                        self.context_data["review_perms"] = self.checker.get_perms(
                            self.review
                        )
                        self.gfk_object = self.review

                        # do we have a vote?
                        if "vote_uuid" in kwargs:
                            # get the vote
                            self.vote = get_object_or_404(
                                Vote, review=self.review, uuid=self.kwargs["vote_uuid"]
                            )
                            self.checker.prefetch_perms([self.vote])
                            if not self.checker.has_perm("vote.view_vote", self.vote):
                                raise PermissionDenied
                            self.url_namespace_prefixes.append("vote")
                            self.add_breadcrumbs(self.vote)
                            self.url_kwargs["vote_uuid"] = self.vote.uuid
                            self.context_data["vote"] = self.vote
                            self.context_data["vote_perms"] = self.checker.get_perms(
                                self.vote
                            )
                            self.gfk_object = self.vote

            # do we have a forum?
            if "forum_slug" in kwargs:
                self.forum = get_object_or_404(
                    Forum, team=self.team, slug=self.kwargs["forum_slug"]
                )
                self.checker.prefetch_perms([self.forum])
                if not self.checker.has_perm("forum.view_forum", self.forum):
                    raise PermissionDenied
                self.url_namespace_prefixes.append("forum")
                self.add_breadcrumbs(self.forum)
                self.url_kwargs["forum_slug"] = self.forum.slug
                self.context_data["forum"] = self.forum
                self.context_data["forum_perms"] = self.checker.get_perms(self.forum)
                self.gfk_object = self.forum

                # do we have a thread?
                if "thread_slug" in kwargs:
                    self.thread = get_object_or_404(
                        Thread, forum=self.forum, slug=self.kwargs["thread_slug"]
                    )
                    self.checker.prefetch_perms([self.thread])
                    if not self.checker.has_perm("thread.view_thread", self.thread):
                        raise PermissionDenied
                    self.url_namespace_prefixes.append("thread")
                    self.add_breadcrumbs(self.thread)
                    self.url_kwargs["thread_slug"] = self.thread.slug
                    self.context_data["thread"] = self.thread
                    self.context_data["thread_perms"] = self.checker.get_perms(
                        self.thread
                    )
                    self.gfk_object = self.thread

        # do we have a comment? (GFK object outside normal hierachy)
        if "comment_uuid" in kwargs:
            self.comment = get_object_or_404(
                Comment,
                uuid=self.kwargs["comment_uuid"],
                object_id=self.gfk_object.pk,
                content_type=ContentType.objects.get_for_model(self.gfk_object),
            )
            self.checker.prefetch_perms([self.comment])
            if not self.checker.has_perm("comment.view_comment", self.comment):
                raise PermissionDenied
            self.url_namespace_prefixes.append("comment")
            self.add_breadcrumbs(self.comment)
            self.url_kwargs["comment_uuid"] = self.comment.uuid
            self.context_data["comment"] = self.comment
            self.context_data["comment_perms"] = self.checker.get_perms(self.comment)
            self.gfk_object = self.comment

        # do we have an attachment? (GFK object outside normal hierachy)
        if "attachment_uuid" in kwargs:
            self.attachment = get_object_or_404(
                Attachment,
                uuid=self.kwargs["attachment_uuid"],
                object_id=self.gfk_object.pk,
                content_type=ContentType.objects.get_for_model(self.gfk_object),
            )
            self.checker.prefetch_perms([self.attachment])
            if not self.checker.has_perm("attachment.view_attachment", self.attachment):
                raise PermissionDenied
            self.url_namespace_prefixes.append("attachment")
            self.add_breadcrumbs(self.attachment)
            self.url_kwargs["attachment_uuid"] = self.attachment.uuid
            self.context_data["attachment"] = self.attachment
            self.context_data["attachment_perms"] = self.checker.get_perms(
                self.attachment
            )
            self.gfk_object = self.attachment

        # do we have an event? (GFK object outside normal hierachy)
        if "event_uuid" in kwargs:
            self.event = get_object_or_404(
                Event,
                uuid=self.kwargs["event_uuid"],
                object_id=self.gfk_object.pk,
                content_type=ContentType.objects.get_for_model(self.gfk_object),
            )
            self.checker.prefetch_perms([self.event])
            if not self.checker.has_perm("event.view_event", self.event):
                raise PermissionDenied
            self.url_namespace_prefixes.append("event")
            self.add_breadcrumbs(self.event)
            self.url_kwargs["event_uuid"] = self.event.uuid
            self.context_data["event"] = self.event
            self.context_data["event_perms"] = self.checker.get_perms(self.event)

        # finally add any missing action breadcrumbs,
        # but if this is a CreateView add a link to the ListView first
        if self.request.resolver_match.url_name == "create":
            self.add_listview_breadcrumb()
        # add action breadcrumb
        self.add_action_breadcrumb()

    def get_context_data(self, **kwargs):
        """
        Add Team and related objects and permissions to context
        """
        context = super().get_context_data(**kwargs)
        context.update(self.context_data)
        return context


class PermissionRequiredOr403Mixin(PermissionRequiredMixin):
    """
    A subclass of PermissionRequireMixin with the properties we want
    to use in SocialRating views
    """

    accept_global_perms = False
    return_403 = True


class BreadCrumbMixin:
    """
    BreadCrumbMixin contains all the properties, methods and logic we use for adding breadcrumbs
    """

    def __init__(self):
        # start with an empty list of crumbs
        self.breadcrumbs = []
        self.url_namespace_prefixes = []
        self.url_kwargs = {}

    def add_breadcrumbs(self, obj):
        """
        This is the primary breadcrumb adding method. We call it with an object like
        a team or an item, and breadcrumbs for that objects listview and detailview
        will be added.
        """
        # logger.debug(
        #    "inside add_breadcrumbs() with obj %s and prefixes %s and kwargs %s"
        #    % (obj, self.url_namespace_prefixes, self.url_kwargs)
        # )

        # logger.debug("adding breadcrumb for listview for obj %s" % obj)
        self.breadcrumbs.append(
            (
                obj.__class__.breadcrumb_list_name,
                reverse(
                    ":".join(self.url_namespace_prefixes + ["list"]),
                    kwargs=self.url_kwargs,
                ),
            )
        )

        # logger.debug("adding breadcrumb for detailview for obj %s" % obj)
        self.breadcrumbs.append((obj.breadcrumb_detail_name, obj.get_absolute_url()))

    @property
    def breadcrumb_title(self):
        """
        This property returns a default breadcrumb title for generic action views.
        ListView and DetailView will get the name from the model.
        """
        if isinstance(self, django.views.generic.list.ListView):
            # ListViews uses the breadcrumb list name from the model
            return self.model.breadcrumb_list_name
        elif isinstance(self, django.views.generic.edit.CreateView):
            # return a default string for all CreateViews
            return "Create"
        elif isinstance(self, django.views.generic.edit.UpdateView):
            # return a default string for all UpdateViews
            return "Update"
        elif isinstance(self, django.views.generic.edit.DeleteView):
            # return a default string for all DeleteViews
            return "Delete"
        else:
            # DetailViews use the breadcrumb title from a model property
            return

    def add_listview_breadcrumb(self):
        """
        Return a breadcrumb for the view named "list" in the same
        namespace as the current resolver match, with the same kwargs.
        Used to get a link to the matching ListView for a CreateView
        """
        self.breadcrumbs.append(
            (
                self.model.breadcrumb_list_name,
                reverse(
                    viewname=":".join(
                        self.request.resolver_match.namespaces + ["list"]
                    ),
                    kwargs=self.request.resolver_match.kwargs,
                ),
            )
        )

    def add_action_breadcrumb(self):
        """
        Return a breadcrumb for the current views action, like "Create" or "Delete"
        Override the defaults set in BreadCrumbMixin by setting breadcrumb_title on the view.
        """
        # first include a breadcrumb for settings view so we get
        # "Settings / Update" rather than just "Update"
        if "settings_view" in self.kwargs:
            # logger.debug("adding settings breadcrumb")
            self.breadcrumbs.append(
                (
                    "Settings",
                    reverse(
                        viewname=":".join(
                            self.request.resolver_match.namespaces + ["settings"]
                        ),
                        kwargs=self.request.resolver_match.kwargs,
                    ),
                )
            )

        # Then include the actual "action" breadcrumb, like Create, Update, Delete...
        if hasattr(self, "breadcrumb_title") and self.breadcrumb_title:
            self.breadcrumbs.append((self.breadcrumb_title, self.request.path))


class FilterQSMixin:
    """
    Filter queryset by this views models filterfield and filtervalue property.
    The filterfield holds the name of the field we want to filter by on the model,
    and filtervalue holds the name of the property on the view which holds the value
    we want to filter by.
    Example: the Item model has filterfield "category" and filtervalue "category" so
    we filter the queryset with {"category": self.category}

    Also filter for context if we have one.

    Finally check permissions for all objects and remove the ones with no permission from
    the queryset before returning.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        kwargs = {}

        # generic filtering for FK relationships?
        if hasattr(self.model, "filterfield") and hasattr(self.model, "filtervalue"):
            kwargs.update(
                {self.model.filterfield: getattr(self, self.model.filtervalue)}
            )

        # filter if we have anything to filter on
        if kwargs:
            queryset = queryset.filter(**kwargs)

        # filter for context(s)?
        contexts = self.request.GET.getlist("context")
        self.context_data["filtercontexts"] = contexts

        if hasattr(queryset.model, "context") and contexts:
            contextfilter = Q(context__isnull=True)
            for contextslug in contexts:
                contextfilter.add(Q(context__slug=contextslug), Q.OR)
            print("filter for contexts is %s" % contextfilter)
            queryset = queryset.filter(contextfilter)
        else:
            print("not filtering for any contexts")

        # prefetch permissions for the full queryset
        self.checker.prefetch_perms(queryset)
        view_perm = (
            f"{queryset.model._meta.model_name}.view_{queryset.model._meta.model_name}"
        )
        removelist = []
        for obj in queryset:
            if not self.checker.has_perm(view_perm, obj):
                removelist.append(obj.pk)

        # remove any objects the user doesn't have permission to see
        return queryset.exclude(pk__in=removelist)


class SRViewMixin(
    # first get objects from URL slugs
    SlugObjectsMixin,
    # include few adjustments for guardian
    PermissionRequiredOr403Mixin,
    # all the breadcrumb stuff
    BreadCrumbMixin,
    # filter querysets based on the "parent" objects for the view
    FilterQSMixin,
):
    """
    A convenience mixin which includes all the mixins we want to use in all SocialRating views.
    The leftmost mixin/first arg runs first.
    """

    pass


class SRListViewMixin(
    # first get objects from URL slugs
    SlugObjectsMixin,
    # all the breadcrumb stuff
    BreadCrumbMixin,
    # filter querysets based on the "parent" objects for the view
    FilterQSMixin,
):
    """
    A convenience mixin for ListViews which includes all the mixins we want to use
    The leftmost mixin/first arg runs first.
    """

    pass
