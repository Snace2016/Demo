import os
from io import BytesIO

from django.conf import settings
from PIL import Image


def process_product_image(uploaded_file):
    image = Image.open(uploaded_file)
    image = image.convert('RGB')
    image.thumbnail((300, 200), Image.Resampling.LANCZOS)

    canvas = Image.new('RGB', (300, 200), (255, 255, 255))
    offset_x = (300 - image.width) // 2
    offset_y = (200 - image.height) // 2
    canvas.paste(image, (offset_x, offset_y))

    filename = uploaded_file.name
    base, _ = os.path.splitext(filename)
    safe_name = ''.join(c if c.isalnum() or c in '-_' else '_' for c in base)
    result_name = f'{safe_name}.jpg'
    save_path = os.path.join(settings.MEDIA_ROOT, 'products', result_name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    canvas.save(save_path, 'JPEG', quality=85)
    return f'products/{result_name}'


def delete_product_image(image_path):
    if not image_path:
        return
    full_path = os.path.join(settings.MEDIA_ROOT, image_path)
    if os.path.isfile(full_path):
        os.remove(full_path)
