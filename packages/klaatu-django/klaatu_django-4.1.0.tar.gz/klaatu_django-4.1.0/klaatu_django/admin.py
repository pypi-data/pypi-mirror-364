from typing import TYPE_CHECKING, Sequence

from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.utils import quote
from django.db.models import Model, QuerySet
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from .typing import AdminFieldsetsType, AdminFieldsType, FormType

if TYPE_CHECKING:
    from django.utils.functional import _StrPromise  # type: ignore


class BooleanListFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return [('1', 'Yes'), ('0', 'No')]

    def queryset(self, request, queryset):
        value = self.value()
        if value == '1':
            return queryset.filter(**{self.parameter_name: True})
        if value == '0':
            return queryset.filter(**{self.parameter_name: False})
        return queryset


class NoDeleteActionMixin:
    def get_actions(self, request):
        actions = super().get_actions(request)  # type: ignore
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class SetCreatedByAdmin(admin.ModelAdmin):
    # For use in admin pages for models with `created_by` fields
    def save_model(self, request, obj, form, change):
        if not change:
            try:
                obj.created_by = request.user
            except AttributeError:
                pass
        super().save_model(request, obj, form, change)


class SetCreatedByInlineAdmin(admin.ModelAdmin):
    # Set `created_by` on inline objects in admin
    def save_formset(self, request, form, formset, change):
        formset.save(commit=False)
        for obj in formset.new_objects:
            try:
                obj.created_by = request.user
            except AttributeError:
                pass
        super().save_formset(request, form, formset, change)


class TabularManyToManyInline(admin.TabularInline):
    template = "admin/edit_inline/tabular_manytomany.html"


class RelatedLinkMixin:
    admin_site: AdminSite

    def get_related_changeform_link(self, related_obj: Model | None, display_attr: str | None = None):
        """
        If `related_obj` is a model instance, and its model is registered with
        the AdminSite, return a link to the changeform for this instance.
        Otherwise, just return `related_obj` as-is.

        If `display_attr` is set, `related_obj` is displayed using this
        attribute on the model. Otherwise by the model's __str__().

        Usage:

        list_display = (..., "user_link", ...)

        @admin.display(description="user", ordering="user__username")
        def user_link(self, obj):
            return self.get_related_changeform_link(obj.user, "username")
        """
        if (
            isinstance(related_obj, Model) and
            self.admin_site.is_registered(related_obj._meta.model) and
            related_obj._meta.pk
        ):
            pk = getattr(related_obj, related_obj._meta.pk.attname)
            return format_html(
                '<a href="{}">{}</a>',
                reverse(
                    "admin:%s_%s_change" % (related_obj._meta.app_label, related_obj._meta.model_name),
                    args=(quote(pk),),
                    current_app=self.admin_site.name
                ),
                getattr(related_obj, display_attr) if display_attr else related_obj
            )
        return related_obj

    def get_related_changeform_link_list(
        self,
        related_queryset: QuerySet,
        display_attr: str | None = None,
        container_classes: str = "",
        item_classes: str = "",
    ):
        """
        Returns links to changeform for each item in `related_queryset`,
        each in their own <div class="related-changeform-link-list-item">. The
        whole list is enclosed in a <div class="related-changeform-link-list">.
        If queryset's model is not registered with the AdminSite, returns the
        same list but without links.

        If `display_attr` is set, items are displayed using this attribute
        on the model instances. Otherwise by the model's __str__().

        `container_classes` sets extra CSS classes on the containing <div>
        element, `item_classes` sets them on each item's <div>.

        Usage:

        list_display = (..., "user_link_list", ...)

        @admin.display(description="users", ordering="users__username")
        def user_link_list(self, obj):
            return self.get_related_changeform_link_list(
                obj.users.all(),
                "username"
            )
        """
        if self.admin_site.is_registered(related_queryset.model):
            opts = related_queryset.model._meta
            html = "".join([
                '<div class="related-changeform-link-list-item %s"><a href="%s">%s</a></div>' % (
                    item_classes,
                    reverse(
                        "admin:%s_%s_change" % (opts.app_label, opts.model_name),
                        args=(quote(getattr(obj, opts.pk.attname)),),
                        current_app=self.admin_site.name
                    ),
                    getattr(obj, display_attr) if display_attr else obj
                )
                for obj in related_queryset
            ])
        else:
            html = "".join([
                f'<div class="related-changeform-link-list-item {item_classes}">' +
                str(getattr(obj, display_attr)) if display_attr else str(obj) +
                "</div>"
                for obj in related_queryset
            ])

        return format_html(f'<div class="related-changeform-link-list {container_classes}">{html}</div>')

    def get_related_changelist_link(
        self,
        obj: Model | None,
        related_name: str,
        proxy_model: type[Model] | None = None,
        show_zero: bool = True,
        verbose_name: "_StrPromise | str | None" = None,
        verbose_name_plural: "_StrPromise | str | None" = None
    ):
        """
        `related_name` should be the name of a many-to-many or many-to-one
        (reverse foreign key relationship) field on `obj`. If the related
        model is registered with the AdminSite, return a link to that model's
        changelist, filtered for those instances that are related to `obj`.

        Set `proxy_model` if the link should go to the admin for a proxy
        model, rather than the concrete model indicated by the relation.

        Link text will be "[number of instances] [verbose_name[_plural]]",
        where `verbose_name[_plural]` is either set in the method arguments or
        collected from the related model's meta attributes. The usage of the
        "_plural" suffix is of course dependent upon the number of related
        objects found.

        Usage:

        list_display = (..., "user_list_link", ...)

        @admin.display(description="users")
        def user_list_link(self, obj):
            return self.get_related_changelist_link(obj, "users")
        """
        if obj is None or obj._meta.pk is None:
            return None

        related_field = obj._meta.get_field(related_name)

        if isinstance(related_field, ForeignObjectRel):
            if proxy_model and related_field.related_model and issubclass(proxy_model, related_field.related_model):
                related_model = proxy_model
            else:
                related_model = related_field.related_model

            if related_model and self.admin_site.is_registered(related_model):
                opts = related_model._meta
                verbose_name = verbose_name or related_model._meta.verbose_name
                verbose_name_plural = verbose_name_plural or related_model._meta.verbose_name_plural
                obj_count = getattr(obj, related_name).count()

                if not obj_count and not show_zero:
                    return ""

                return format_html(
                    '<a href="{}?{}__exact={}">{} {}</a>',
                    reverse(
                        "admin:%s_%s_changelist" % (opts.app_label, opts.model_name),
                        current_app=self.admin_site.name
                    ),
                    related_field.field.get_attname(),
                    getattr(obj, obj._meta.pk.attname),
                    obj_count,
                    verbose_name if obj_count == 1 else verbose_name_plural
                )

        return None


class ExtendedModelAdmin(RelatedLinkMixin, admin.ModelAdmin):
    """Meant to collect all kinds of useful extra functionality."""


class ExtendedTabularInline(RelatedLinkMixin, admin.TabularInline):
    pass


class ExtendedStackedInline(RelatedLinkMixin, admin.StackedInline):
    pass


class SeparateAddMixin(admin.ModelAdmin):
    """
    Use custom settings when a change form is used for adding a new object,
    rather than editing an existing one. Mirrors the `exclude`, `fields`,
    `fieldsets`, `form`, `inlines`, and `readonly_fields` properties. If a
    property is None, the regular one will be used instead.
    """
    add_exclude: Sequence[str] | None = None
    add_fields: AdminFieldsType | None = None
    add_fieldsets: AdminFieldsetsType | None = None
    add_form: FormType | None = None
    add_inlines: Sequence[type[InlineModelAdmin]] | None = None
    add_readonly_fields: Sequence[str] | None = None

    def get_add_exclude(self, request: HttpRequest) -> Sequence[str] | None:
        return self.add_exclude

    def get_add_fields(self, request: HttpRequest) -> AdminFieldsType | None:
        return self.add_fields

    def get_add_fieldsets(self, request: HttpRequest) -> AdminFieldsetsType | None:
        return self.add_fieldsets

    def get_add_inlines(self, request: HttpRequest) -> Sequence[type[InlineModelAdmin]] | None:
        return self.add_inlines

    def get_add_readonly_fields(self, request: HttpRequest) -> Sequence[str] | None:
        return self.add_readonly_fields

    def get_exclude(self, request, obj=None):
        if obj is None:
            add_exclude = self.get_add_exclude(request)
            if add_exclude is not None:
                return add_exclude
        return super().get_exclude(request, obj)

    def get_fields(self, request, obj=None):
        if obj is None:
            add_fields = self.get_add_fields(request)
            if add_fields is not None:
                return add_fields
        return super().get_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            add_fieldsets = self.get_add_fieldsets(request)
            if add_fieldsets is not None:
                return add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, change=False, **kwargs):
        defaults = {}
        if self.add_form is not None and not change:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, change=change, **defaults)

    def get_inlines(self, request, obj):
        if obj is None:
            add_inlines = self.get_add_inlines(request)
            if add_inlines is not None:
                return add_inlines
        return super().get_inlines(request, obj)  # type: ignore

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            add_readonly_fields = self.get_add_readonly_fields(request)
            if add_readonly_fields is not None:
                return add_readonly_fields
        return super().get_readonly_fields(request, obj)
