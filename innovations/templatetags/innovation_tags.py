from django import template

register = template.Library()


@register.filter('has_status')
def has_status(innovation, status_name):
    status = innovation.status
    return True if status_name == status else False


@register.filter('remove_page_arg')
def remove_page_arg(path):
    url, args = path.split("?")
    args_list = args.split("&")
    new_args_list = [arg for arg in args_list if not arg.startswith("page=")]
    return "{}?{}".format(url, "&".join(new_args_list))
