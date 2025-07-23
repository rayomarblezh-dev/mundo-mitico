import random
from PIL import Image, ImageDraw, ImageFont
import os

def generar_captcha_imagen():
    # Generar un código aleatorio de 6 dígitos
    codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    # Crear imagen
    width, height = 220, 80
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    # Cargar fuente (usar una fuente estándar del sistema)
    try:
        font = ImageFont.truetype('arial.ttf', 48)
    except:
        font = ImageFont.load_default()
    # Dibujar el texto en el centro
    text_width, text_height = draw.textsize(codigo, font=font)
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), codigo, font=font, fill=(0, 0, 0))
    # Guardar imagen
    images_dir = 'images'
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    path = os.path.join(images_dir, f'captcha_{codigo}.png')
    image.save(path)
    return path, codigo 