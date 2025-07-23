import random
import qrcode
import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Genera 6 números aleatorios, crea un QR con esos números, guarda la imagen y retorna el path y los números

def generar_captcha_qr(directorio_salida='images'):
    # Generar 6 números aleatorios (0-9)
    numeros = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    # Crear el QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(numeros)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Asegurarse de que el directorio existe
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)

    # Guardar la imagen con un nombre único
    path_archivo = os.path.join(directorio_salida, f'captcha_{numeros}.png')
    img.save(path_archivo)

    return path_archivo, numeros

# Nueva función para generar el teclado inline de captcha

def generar_teclado_captcha():
    botones = []
    digitos = [str(i) for i in range(10)]
    idx = 0
    for _ in range(3):
        fila = []
        for _ in range(2):
            if idx < len(digitos):
                fila.append(InlineKeyboardButton(text=digitos[idx], callback_data=f"captcha_{digitos[idx]}"))
                idx += 1
        botones.append(fila)
    return InlineKeyboardMarkup(inline_keyboard=botones)