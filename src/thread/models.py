from django.db import models
from django.urls import reverse_lazy
from guardian.shortcuts import assign_perm

from utils.models import UUIDBaseModel


class Thread(UUIDBaseModel):
    """
    A forum thread. The actual comments in the thread are available via self.comments (from BaseModel).
    self.comments.filter(reply_to__isnull=True).get() should return the "root" comment which is the first
    post in the thread.
    """

    class Meta(UUIDBaseModel.Meta):
        unique_together = [["slug", "forum"]]
        permissions = (("add_comment", "Add Comment in this Thread"),)

    forum = models.ForeignKey(
        "forum.Forum",
        on_delete=models.CASCADE,
        related_name="threads",
        help_text="The Forum to which this Thread belongs",
    )

    actor = models.ForeignKey(
        "actor.Actor",
        on_delete=models.PROTECT,
        related_name="threads",
        help_text="The Actor who made this Thread.",
    )

    subject = models.CharField(max_length=100, help_text="The subject of this Thread.")

    slug = models.SlugField(
        max_length=50,
        help_text="The slug for this Thread. Must be unique in the Forum.",
    )

    locked = models.BooleanField(
        default=False,
        help_text="Check to lock this Thread to prevent new Comments from being posted to it.",
    )

    filterfield = "forum"
    filtervalue = "forum"
    breadcrumb_list_name = "Threads"
    slug_field = "subject"

    def __str__(self):
        return "Thread: %s" % self.subject

    @property
    def breadcrumb_detail_name(self):
        return self.subject[0:50]

    @property
    def detail_url_kwargs(self):
        return {
            "team_slug": self.team.slug,
            "forum_slug": self.forum.slug,
            "thread_slug": self.slug,
        }

    object_url_namespace = "team:forum:thread"

    def get_absolute_url(self):
        return reverse_lazy(
            self.object_url_namespace + ":detail", kwargs=self.detail_url_kwargs
        )

    def grant_permissions(self):
        """
        - All team members may view a Thread
        - Admins and OP may update a Thread
        - Admins and OP may delete a Thread
        - All team members may create new Comments in the Thread
        """
        assign_perm("thread.view_thread", self.team.group, self)
        assign_perm("thread.change_thread", self.team.admingroup, self)
        assign_perm("thread.change_thread", self.actor.user, self)
        assign_perm("thread.delete_thread", self.team.admingroup, self)
        assign_perm("thread.delete_thread", self.actor.user, self)
        assign_perm("thread.add_comment", self.team.group, self)

    def save(self, **kwargs):
        """
        Set slug, save the Thread, and grant permissions.
        """
        self.slug = self.get_slug(prefix=str(self.created.isoformat())[0:10] + "-")
        super().save(**kwargs)
        self.grant_permissions()

    @property
    def team(self):
        return self.forum.team
