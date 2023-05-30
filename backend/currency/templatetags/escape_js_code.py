from django import template
import json

register = template.Library()


@register.filter
def escape_js_code(code):
    return json.dumps(str(code))
