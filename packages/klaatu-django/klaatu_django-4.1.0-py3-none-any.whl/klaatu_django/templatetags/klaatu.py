import re
from datetime import date, datetime, timedelta
from typing import Any, Collection, Iterable
from urllib.parse import urljoin

from klaatu_python.utils import percent_rounded

from django import template
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import NaturalTimeFormatter
from django.http.request import HttpRequest, QueryDict
from django.template.base import token_kwargs
from django.template.context import Context
from django.template.defaultfilters import stringfilter
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince, timeuntil
from django.utils.translation import gettext_lazy, ngettext_lazy, override

from klaatu_django.utils import (
    _get_param_list,
    capitalize,
    natural_and_list,
    natural_or_list,
    relativedelta_rounded,
    render_modal,
    timedelta_formatter,
)

register = template.Library()


class EmailSection(template.Node):
    def __init__(self, nodelist: template.NodeList, **kwargs: template.base.FilterExpression):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context: template.Context) -> str:
        table_kwargs = {
            "role": "presentation",
            "class": "section",
            "cellspacing": "0",
            "cellpadding": "0",
        }
        table_args = ["%s=\"%s\"" % (k, v) for k, v in table_kwargs.items()]
        td_args = []
        for name, value in self.kwargs.items():
            td_args.append("%s=\"%s\"" % (name, value.resolve(context)))  # type: ignore
        return "<table %s><tr><td %s>%s</td></tr></table>" % (
            " ".join(table_args),
            " ".join(td_args),
            self.nodelist.render(context)
        )


class LinkNode(template.Node):
    def __init__(
        self,
        nodelist: template.NodeList,
        href: template.base.FilterExpression,
        **kwargs: template.base.FilterExpression,
    ):
        self.nodelist = nodelist
        self.href = href
        self.kwargs = kwargs

    def render(self, context: Context):
        href = self.href.resolve(context, ignore_failures=True)  # type: ignore
        kwargs = {
            key.replace("_", "-"): value.resolve(context, ignore_failures=True)  # type: ignore
            for key, value in self.kwargs.items()
        }
        root_url = getattr(settings, "ROOT_URL", "")
        if root_url and isinstance(href, str):
            is_external = bool(re.match("^https?://", href)) and not href.startswith(root_url)
        else:
            is_external = False
        if is_external:
            if "rel" in kwargs:
                if "external" not in kwargs["rel"].split(" "):
                    kwargs["rel"] += " external"
            else:
                kwargs["rel"] = "external"

        return format_html(
            '<a href="{}"{}{}>{}</a>',
            href,
            mark_safe(' target="_blank"') if is_external else " ",
            mark_safe("".join([f' {key}="{value}"' for key, value in kwargs.items()])),
            self.nodelist.render(context),
        )


class NaturalTimeShortFormatterMeta(type):
    def __new__(mcs, name, bases, dct):
        """
        The 'past' ones are identical to the originals, but I'm including them
        because the default Swedish translations are wrong.
        """
        klass = super().__new__(mcs, name, bases, dct)
        time_strings = getattr(klass, "time_strings", {})
        time_strings.update({
            'past-day': gettext_lazy('%(delta)s ago'),
            'past-hour': ngettext_lazy('an hour ago', '%(count)s hours ago', 'count'),
            'past-minute': ngettext_lazy('a minute ago', '%(count)s minutes ago', 'count'),
            'past-second': ngettext_lazy('a second ago', '%(count)s seconds ago', 'count'),
            'future-second': ngettext_lazy('in one second', 'in %(count)s seconds', 'count'),
            'future-minute': ngettext_lazy('in one minute', 'in %(count)s minutes', 'count'),
            'future-hour': ngettext_lazy('in one hour', 'in %(count)s hours', 'count'),
            'future-day': gettext_lazy('in %(delta)s'),
            "yesterday": gettext_lazy("yesterday"),
            "tomorrow": gettext_lazy("tomorrow"),
        })
        setattr(klass, "time_strings", time_strings)
        return klass


class NaturalTimeShortFormatter(NaturalTimeFormatter, metaclass=NaturalTimeShortFormatterMeta):
    """
    Ugly hack to only return the first part of the string when the timedelta
    >= 1 day (NaturalTimeFormatter returns "1 month, 3 days" etc, we only
    want "1 month" here).
    """
    @classmethod
    def string_for(cls, value):
        if not isinstance(value, date):
            return value
        if not isinstance(value, datetime):
            value = datetime.combine(value, datetime.min.time())

        # pylint:disable=no-member
        now = datetime.now(timezone.utc if timezone.is_aware(value) else None)
        # Make it as round as we want it:
        relative_delta = relativedelta_rounded(now, value)
        now = value + relative_delta

        if value < now:
            if abs(relative_delta.days) == 1:
                return cls.time_strings["yesterday"]
            delta = now - value
            if delta.days != 0:
                delta_str = timesince(value, now, time_strings=cls.past_substrings)
                return cls.time_strings["past-day"] % {
                    "delta": delta_str.split(", ")[0]
                }
        else:
            if abs(relative_delta.days) == 1:
                return cls.time_strings["tomorrow"]
            delta = value - now
            if delta.days != 0:
                delta_str = timeuntil(value, now, time_strings=cls.future_substrings)
                return cls.time_strings["future-day"] % {
                    "delta": delta_str.split(", ")[0]
                }
        return super().string_for(value)


### TAGS ##################################

@register.tag(name="link")
def do_link(parser: template.base.Parser, token: template.base.Token):
    """
    Outputs an <a> tag. The only purpose of this is to automatically inject
    `target="_blank"` and `rel="external"` if it's an external link, so
    there's a good argument for this being overkill. But I learned stuff from
    writing it, and that's never a waste.

    Has one required positional argument, which is the link URL. This can be a
    raw string or a template variable. Keyword arguments will be used as
    attributes on the <a> element, with underscores replaced by dashes in the
    keys.

    Usage:
    {% link "https://external-link.com" data_foo="bar" %}
    <p>This is my link</p>
    {% endlink %}

    Output:
    <a href="https://external-link.com" target="_blank" data-foo="bar">
        <p>This is my link</p>
    </a>
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError("'link' template tags must contain a URL.")
    href = parser.compile_filter(bits[1])
    kwargs = token_kwargs(bits[2:], parser)
    nodelist = parser.parse(("endlink",))
    parser.delete_first_token()
    return LinkNode(nodelist, href, **kwargs)


@register.inclusion_tag("klaatu/modals/dynamic.html")
def dynamic_modal(
    modal_id: str,
    url: str = "",
    classes: str = "",
    required_params: str = "",
    optional_params: str = "",
    large=False,
    scrollable=False,
    center=False,
    **kwargs,
):
    """
    Includes the Bootstrap modal "skeleton" from klaatu/modals/dynamic.html
    and renders it in a similar way to `modal()`, except it also sets
    `data-content-url` on the .modal element. On modal show event, the JS
    function loadDynamicContent() will load the contents from this URL into
    the modal.

    The template rendered by this URL will preferably extend
    klaatu/modals/dynamic_content.html.

    Any extra **kwargs, whose key begins with "data_", will be added to the
    .modal element as "data-" attributes.
    For example, `{% dynamic_modal ... data_foo_bar="42" %}` will result in a
    .modal element with `data-foo-bar="42"`.

    Extra kwargs whose keys do _not_ begin with "data_" will be ignored.
    """
    param_list = _get_param_list(required_params, optional_params)
    url = url.strip()
    if url and not url.startswith("/"):
        try:
            url = reverse(url)
        except Exception:
            pass

    return {
        "modal": {
            "id": modal_id.strip(),
            "url": url,
            "classes": classes.strip(),
            "required_params": required_params,
            "optional_params": optional_params,
            "all_params": param_list,
            "large": large,
            "scrollable": scrollable,
            "center": center,
            "data_attrs": {k.replace("_", "-"): v for k, v in kwargs.items() if k.startswith("data_")},
        },
    }


@register.tag(name="section")
def email_section(parser: template.base.Parser, token: template.base.Token):
    """
    Injects the tag's contents into a <table> with one row and one cell,
    roughly mimicking a <div>. This is because email clients are retarded and
    can't handle normal HTML.

    The <table> tag will have class="section"; it is up to the implementation
    to provide such a class. The element is probably best suited for
    graphically "top level" sections, and the class should therefore specify
    "max-width: 600px" or whichever container width you go for. Any kwargs
    will be used for attributes on the lone <td> tag.

    Example:

    {% section class="py-3" style="text-align: center" %}
        <p>Hey ho!</p>
    {% endsection %}

    ... will result in:

    <table class="section">
        <tr>
            <td class="py-3" style="text-align: center">
                <p>Hey ho!</p>
            </td>
        </tr>
    </table>
    """
    bits = token.split_contents()[1:]
    kwargs = {}
    for bit in bits:
        match = template.base.kwarg_re.match(bit)
        if match:
            name, value = match.groups()
            kwargs[name] = parser.compile_filter(value)
    nodelist = parser.parse(("endsection",))
    parser.delete_first_token()
    return EmailSection(nodelist, **kwargs)


@register.simple_tag
def join_query_params(request: HttpRequest, **kwargs) -> str:
    """
    Will coerce the new QueryDict to only contain one value for each key,
    with priority to those in kwargs.
    """
    params = {k: v for k, v in request.GET.dict().items() if not isinstance(v, list)}
    params.update(kwargs)
    querydict = QueryDict(mutable=True)
    querydict.update(params)
    return request.path_info + '?' + querydict.urlencode()


@register.simple_tag(takes_context=True)
def map_to_context(context: template.RequestContext, key: str):
    """
    Tries to get value from current context, both with key as-is and with
    dashes switched to underscores.
    """
    if key in context:
        return context[key]
    if "-" in key:
        return context.get(key.replace("-", "_"), "")
    return ""


@register.simple_tag(takes_context=True)
def modal(
    context: template.RequestContext,
    template_name: str,
    modal_id="",
    classes="",
    required_params="",
    optional_params="",
    footer=True,
    large=False,
    scrollable=False,
    center=False,
    **kwargs
) -> str:
    render_context: dict[str, Any] = {k: v for k, v in context.flatten().items() if isinstance(k, str)}
    render_context.update(kwargs)

    return render_modal(
        template_name=template_name,
        request=context.request,
        modal_id=modal_id,
        classes=classes,
        required_params=required_params,
        optional_params=optional_params,
        footer=footer,
        large=large,
        scrollable=scrollable,
        center=center,
        context=render_context,
    )


@register.inclusion_tag("klaatu/preloader.html")
def preloader(
    id: str | None = None,
    position="absolute",
    show=False,
    large=False,
    framed=True,
    backdrop=True,
    style="",
    **kwargs
):
    """
    Inserts a .preloader element, which will then be shown and hidden by JS.
    Extend klaatu/preloader.html to customize it.

    @param show Show preloader on load
    @param large If False, shrink font & image sizes to 75%; else 100%
    @param framed Whether to include a frame. This may or may not have any
           effect, depending on the HTML/CSS implementation.
    @param backdrop Whether to show the preloader against a backdrop of some
           kind. This may or may not have any effect, depending on the
           HTML/CSS implementation.
    """
    return {
        "preloader": {
            "id": id,
            "show": show,
            "large": large,
            "position": position,
            "framed": framed,
            "backdrop": backdrop,
            "style": style,
            **kwargs,
        }
    }


@register.simple_tag
def static_full_uri(value: str) -> str:
    root_url = getattr(settings, "ROOT_URL", "")
    return urljoin(root_url, static(value))


@register.simple_tag(name='urljoin')
def urljoin_tag(base, url) -> str:
    return urljoin(base, url)


### FILTERS ###############################

@register.filter(name="abs")
def abs_value(value) -> int | None:
    """
    Simply returns the absolute value of `value`, or None if it cannot be
    coerced to integer.
    """
    try:
        return abs(int(value))
    except TypeError:
        return None


@register.filter
def add_str(value, arg) -> str:
    return str(value) + str(arg)


@register.filter
def admin_boolean_icon(value: bool) -> str:
    """
    Taken from django.contrib.admin.templatetags.admin_list._boolean_icon(),
    which is probably considered "internal", so I copied its code instead.
    """
    icon_url = static('admin/img/icon-%s.svg' % {True: 'yes', False: 'no', None: 'unknown'}[value])
    return format_html('<img src="{}" alt="{}">', icon_url, value)


@register.filter(name="capitalize")
@stringfilter
def capitalize_string(value: str) -> str:
    return capitalize(value)


@register.filter
def delta_days(value) -> int | None:
    """
    Return number of days between now and `value`. Positive = future.
    `value` may be a date or datetime object, or a string which can be parsed
    with datetime.fromisoformat().
    """
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            pass
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return (value - timezone.localdate()).days
    return None


@register.filter
def distinct(seq: Collection) -> list:
    """Returns unique members of a collection."""
    return list(set(seq))


@register.filter
def divide_by(value, arg):
    try:
        return value / arg
    except Exception:
        return "-"


@register.filter
def emphasize(text: str, words: str | Iterable[str]):
    """
    Make all instances of `words` in `text` <strong>bold</strong>.
    Case insensitive.
    """
    if isinstance(words, str):
        words = words.split(" ")
    pattern = "|".join([w.lower() for w in words])
    return mark_safe(re.sub(f"({pattern})", r"<strong>\1</strong>", text, flags=re.IGNORECASE))


@register.filter
@stringfilter
def full_uri(value: str) -> str:
    root_url = getattr(settings, "ROOT_URL", "")
    return urljoin(root_url, value)


@register.filter
def in_language(value: str, language_code: str) -> str:
    with override(language_code):
        return str(value)


@register.filter
def modulo(value, arg):
    try:
        return int(value) % int(arg)
    except Exception:
        return None


@register.filter
def multiply(value, arg):
    try:
        return str(float(value) * float(arg))
    except Exception:
        return "-"


@register.filter(name="natural_and_list")
def natural_and_list_filter(value: Iterable) -> str:
    return natural_and_list(value)


@register.filter(name="natural_or_list")
def natural_or_list_filter(value: Iterable) -> str:
    return natural_or_list(value)


@register.filter
def naturaltime_short(value):
    return NaturalTimeShortFormatter.string_for(value)


@register.filter
def percent_of(part, whole) -> int:
    """Rounded percentage. Usage: `{{ part|percent_of:whole }}%`"""
    try:
        if not isinstance(part, (int, float)):
            part = int(part)
        if not isinstance(whole, (int, float)):
            whole = int(whole)
        return percent_rounded(part, whole)
    except ValueError:
        return 0


@register.filter
@stringfilter
def render(value: str) -> str:
    try:
        return template.Template(value).render(template.Context())
    except Exception:
        return value


@register.filter
def startswith(value: str, arg: str) -> bool:
    try:
        return value.startswith(arg)
    except Exception:
        return False


@register.filter
def subtract(value, arg):
    try:
        return value - arg
    except Exception:
        return "-"


@register.filter(name="timedelta")
def timedelta_filter(value: Any) -> str:
    if not isinstance(value, (timedelta, float, int)) or not value:
        return "-"
    return timedelta_formatter(value)


@register.filter
def timedelta_rounded(value: Any) -> str:
    if not isinstance(value, (timedelta, float, int)) or not value:
        return "-"
    return timedelta_formatter(value, rounded=True)


@register.filter
def timedelta_rounded_short(value: Any) -> str:
    if not isinstance(value, (timedelta, float, int)) or not value:
        return "-"
    return timedelta_formatter(value, rounded=True, short_format=True)


@register.filter
def timedelta_short(value: Any) -> str:
    if not isinstance(value, (timedelta, float, int)) or not value:
        return "-"
    return timedelta_formatter(value, short_format=True)


@register.filter
def timedelta_time(value: Any) -> str:
    """Returns value in HH:MM:SS format."""
    if not isinstance(value, (timedelta, float, int)):
        return "-"
    if isinstance(value, (int, float)):
        value = timedelta(seconds=value)
    hours = int(value.total_seconds() / 3600)
    minutes = int(value.total_seconds() % 3600 / 60)
    seconds = int(value.total_seconds() % 60)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)
