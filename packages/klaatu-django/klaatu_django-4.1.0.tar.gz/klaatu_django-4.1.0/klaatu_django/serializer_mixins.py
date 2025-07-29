import functools
from typing import Any

from rest_framework import serializers

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import override

from .serializer_fields import FileURLField

User = get_user_model()


class UserMixin:
    def get_user(self):
        context = getattr(self, 'context', {})
        assert 'request' in context, 'request must be included in serializer context'
        assert isinstance(context['request'].user, User), \
            f'context["request"].user must be a {User.__module__}.{User.__name__} object'
        return context['request'].user


class CreatedByMixin:
    """
    Sets `created_by` on a created object to the authenticated user. Of course
    only makes sense if there is such a field on the model.
    """
    def create(self, validated_data):
        validated_data = validated_data or {}
        context = getattr(self, 'context', {})
        try:
            user = context['request'].user
            if isinstance(user, User):
                validated_data.update(created_by=user)
        except (AttributeError, KeyError):
            pass
        return super().create(validated_data)  # type: ignore


def override_language(func):
    """
    Used by LanguageMixin below, but could of course be used for any
    serializer method that needs it.
    """
    @functools.wraps(func)
    def wrapper(serializer, *args, **kwargs):
        with override(serializer.context.get('language', settings.LANGUAGE_CODE)):
            return func(serializer, *args, **kwargs)
    return wrapper


class LanguageMixin:
    """
    Set self.context['language'] to a language code in order to present the
    response in that language.

    You probably want the corresponding view to inherit from
    `klaatu_django.view_mixins.LanguageMixin`.
    """
    context: dict[str, Any]

    @override_language
    def to_representation(self, instance):
        return super().to_representation(instance)  # type: ignore


class ImageSerializer(serializers.Serializer):
    """
    Not really a mixin, but placed here for silly circular import reasons.

    Requires the parent object to have a file field called 'image', and a
    char field called 'image_alt'.
    """
    url = FileURLField(source='image.url')
    alt = serializers.CharField(source='image_alt')

    def to_representation(self, instance):
        if not instance.image:
            return None
        return super().to_representation(instance)
