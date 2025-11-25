from django import template

register = template.Library()


@register.filter
def has_group(user, group_name):
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()


@register.filter
def attr(obj, name):
    """Return attribute or callables result by name from an object in templates.

    Usage: {{ obj|attr:'field_name' }}
    """
    if obj is None:
        return ''
    try:
        value = getattr(obj, name)
    except Exception:
        return ''
    if callable(value):
        try:
            return value()
        except Exception:
            return ''
    return value
