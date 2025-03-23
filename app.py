# Adiciona o texto
draw = ImageDraw.Draw(combined)

# Tenta usar uma fonte maior e em negrito (se disponível no Render)
try:
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
except:
    font = ImageFont.load_default()

# Texto combinado
texto = f"{nome} - {cidade}"

# Medir largura/altura do texto
text_width, text_height = draw.textsize(texto, font=font)

# Posição: parte de baixo da imagem com margem de 30px
x = 30  # ou centralizado: (combined.width - text_width) // 2
y = combined.height - text_height - 30

# Desenhar o texto
draw.text((x, y), texto, font=font, fill="white")
