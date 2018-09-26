from django import template

register = template.Library()


@register.filter
def blank_name(name):
    if name and not name.strip():
        return "None"
    return name
