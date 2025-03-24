from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Rota principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Dados do formulário
        nome = request.form.get('nome')
        cidade = request.form.get('cidade')
        file = request.files.get('imagem')

        if file:
    # Salvar imagem enviada
    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Abrir imagem e overlay
    user_image = Image.open(filepath).convert("RGBA").resize((856, 540))
    overlay = Image.open('static/overlay.png').convert("RGBA").resize((856, 540))
    combined = Image.alpha_composite(user_image, overlay)
    draw = ImageDraw.Draw(combined)

    # Fonte
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
    except:
        font = ImageFont.load_default()

    # Coletar mais dados
    pico = request.form.get('pico')
    categoria = request.form.get('categoria')

    # Linhas de texto com legenda
    linhas = [
        f"Nome: {nome}",
        f"Cidade: {cidade}",
        f"Pico: {pico}",
        f"Categoria: {categoria}"
    ]

    # Posição inicial (parte inferior)
    margem = 30
    espaco = 8
    y = combined.height - margem - (len(linhas) * (font.size + espaco))

    for linha in linhas:
        bbox = draw.textbbox((0, 0), linha, font=font)
        x = 30
        draw.text((x, y), linha, font=font, fill="white")
        y += font.size + espaco

    # Salvar resultado
    result_path = os.path.join(UPLOAD_FOLDER, f"final_{filename}")
    combined.save(result_path)
    return send_file(result_path, as_attachment=True)


    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
