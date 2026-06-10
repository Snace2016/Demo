from django import template

register = template.Library()


@register.filter
def product_image_url(product):
    if product.image:
        return f'/media/{product.image}'
    return '/static/images/picture.png'
