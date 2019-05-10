import eav

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy
from guardian.shortcuts import get_perms, assign_perm

from team.models import TeamRelatedModel

class Category(TeamRelatedModel):
    """
    A category defines a type of thing/place/event. A Category belongs to a Team.
    Team owners can create, modify, and delete categories.
    """
    class Meta:
        ordering = ['weight', 'name']
        unique_together = [['name', 'team'], ['slug', 'team']]

    team = models.ForeignKey(
        'team.Team',
        related_name='categories',
        on_delete=models.PROTECT,
        help_text='The Team to which this Category belongs',
    )

    name = models.CharField(
        max_length=100,
        help_text='The name of this Category. Must be unique within the Team.',
    )

    slug = models.SlugField(
        help_text='The slug for this Category. Must be unique within the Team.',
    )

    description = models.TextField(
        help_text='The description of this category. Markdown is supported.',
    )

    weight = models.IntegerField(
        default=10,
        help_text='Change the weight of a Category to change sorting. Heavier Categories sink to the bottom. Categories with the same weight are sorted by name.',
    )

    default_context = models.ForeignKey(
        'context.Context',
        on_delete=models.PROTECT,
        help_text='The default Context for new Reviews for Items in this Category. Leave blank to have no default.',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('team:category:detail', kwargs={
            'team_slug': self.team.slug,
            'category_slug': self.slug
        })

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super().save(**kwargs)

        # fix category.view_category permission if needed 
        if not 'category.view_category' in get_perms(self.team.group, self):
            assign_perm('category.view_category', self.team.group, self)

        # fix category.add_category permission if needed 
        if not 'category.add_category' in get_perms(self.team.admingroup, self):
            assign_perm('category.add_category', self.team.admingroup)

        # fix category.change_category permission if needed 
        if not 'category.change_category' in get_perms(self.team.admingroup, self):
            assign_perm('category.change_category', self.team.admingroup, self)

        # fix category.delete_category permission if needed 
        if not 'category.delete_category' in get_perms(self.team.admingroup, self):
            assign_perm('category.delete_category', self.team.admingroup, self)


    def create_fact_slug(self, fact_name):
        """
        Use the EavSlugField.create_slug_from_name to convert the name (including
        category id to make them unique) to a format which can be used as a Django field name
        """
        return eav.fields.EavSlugField.create_slug_from_name("category%s_%s" % (self.pk, fact_name))

    @property
    def facts(self):
        """
        We use the term "fact" as another word for EAV attributes.
        """
        return self.eav.get_all_attributes()

# register models with eav
eav.register(Category)

