from django import template

register = template.Library()

@register.filter
def truncate_chars(value, max_length):
    if len(value) > max_length:
        return value[:max_length] + '...'
    return value

from django import template
from ..models import Tienda

register = template.Library()

@register.filter
def get_tienda_nombre(tiendas, tienda_id):
    try:
        return tiendas.get(id_tienda=tienda_id).nombre
    except Tienda.DoesNotExist:
        return ''