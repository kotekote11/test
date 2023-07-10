from PIL import Image, ImageDraw

# Создаем изображение размером 800x600 пикселей
image = Image.new('RGB', (800, 600), (135, 206, 250))  # Используем цвет неба

draw = ImageDraw.Draw(image)

# Рисуем линию для песчаного берега
draw.line([(0, 400), (800, 400)], fill=(238, 232, 170), width=200)

# Рисуем волны на море
wave_color = (70, 130, 180)  # Используем цвет воды
amplitude = 40  # Высота волн
frequency = 20  # Частота волн

for y in range(410, 600, 10):
    draw.line([(0, y), (800, y)], fill=wave_color, width=2)
    draw.line([(0, y + amplitude), (800, y + amplitude)], fill=wave_color, width=2)

    amplitude *= -1  # Чтобы волны менялись

# Сохраняем изображение
image.save("sea.png")