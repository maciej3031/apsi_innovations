from django import template

register = template.Library()


@register.filter('has_status')
def has_status(innovation, status_name):
    status = innovation.status
    return True if status_name == status else False
