from django.db import models
from django.urls import reverse_lazy
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import assign_perm

from utils.models import UUIDBaseModel
from thread.models import Thread


class Forum(UUIDBaseModel):
    """
    A Forum groups Threads about the same topic
    """

    class Meta(UUIDBaseModel.Meta):
        unique_together = [["name", "team"], ["slug", "team"]]
        permissions = (("add_thread", "Add Thread in this Forum"),)

    team = models.ForeignKey(
        "team.Team",
        related_name="forums",
        on_delete=models.CASCADE,
        help_text="The Team to which this Forum belongs",
    )

    name = models.CharField(
        max_length=100,
        help_text="The name of this Forum, such as 'General Discussion' or 'Off-Topic'",
    )

    slug = models.SlugField(
        max_length=100, help_text="The slug for this Forum. Must be unique in the Team."
    )

    description = models.TextField(help_text="The description of this Forum")

    allow_new_threads = models.BooleanField(
        default=True,
        help_text="Uncheck to disallow creation of new Threads in this Forum.",
    )

    filterfield = "team"
    filtervalue = "team"
    breadcrumb_list_name = "Forums"

    @property
    def detail_url_kwargs(self):
        return {"team_slug": self.team.slug, "forum_slug": self.slug}

    object_url_namespace = "team:forum"

    def get_absolute_url(self):
        return reverse_lazy(
            self.object_url_namespace + ":detail", kwargs=self.detail_url_kwargs
        )

    def grant_permissions(self):
        """
        - All team members may view a Forum
        - Admins may update a Forum
        - Admins may delete a Forum
        - All team members may create new Threads in the Forum
        """
        assign_perm("forum.view_forum", self.team.group, self)
        assign_perm("forum.change_forum", self.team.admingroup, self)
        assign_perm("forum.delete_forum", self.team.admingroup, self)
        assign_perm("forum.add_thread", self.team.group, self)

    def save(self, **kwargs):
        """
        Save the Forum and grant permissions.
        """
        super().save(**kwargs)
        self.grant_permissions()

    @property
    def comments(self):
        """
        Return a queryset of all the Comments in all Threads in
        this Forum
        """
        from comment.models import Comment

        return Comment.objects.filter(
            # get all Comments which relate to a Thread object
            commented_object_ct=ContentType.objects.get(
                app_label="forum", model="thread"
            ),
            # where the Forum of the Thread is the current Forum
            commented_object_uuid__in=Thread.objects.filter(forum=self).values_list(
                "uuid", flat=True
            ),
        )

    @property
    def authors(self):
        """
        Return a queryset of all Actors who has written one or more
        Comments in a thread in this Forum
        """
        from actor.models import Actor

        return Actor.objects.filter(
            uuid__in=self.comments.values_list("actor__uuid", flat=True)
        )
