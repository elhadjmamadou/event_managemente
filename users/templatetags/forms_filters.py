from django.template import Library

register = Library()


def default_if_none(value):
    return value if value else ''

register.filter('default_if_none', default_if_none)
