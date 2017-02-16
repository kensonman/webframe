from django import template
from django.core.urlresolvers import reverse, NoReverseMatch 
from django.template.defaultfilters import stringfilter

register=template.Library()

@register.filter
@stringfilter
def urlexists(url):
    '''
    Check the URL is registered in the urls.py.

    Usage: 
        <url-name>|urlexists  
    '''
    try:
        rst=reverse(url)
        return True
    except NoReverseMatch:
        return False
