from django import template
from django.urls import URLResolver

register = template.Library()


@register.filter
def combine_url(url_resolvers: list[URLResolver]):
    return ' '.join([str(url_resolver.pattern) for url_resolver in url_resolvers])
