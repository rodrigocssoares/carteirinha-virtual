from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cidade = request.form.get('cidade')
        pico = request.form.get('pico')
        categoria = request.form.get('categoria')
        file = request.files.get('imagem')

        if file:
            # Salvar imagem original enviada
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

            # Linhas com legenda
            linhas = [
                f"Nome: {nome}",
                f"Cidade: {cidade}",
                f"Pico: {pico}",
                f"Categoria: {categoria}"
            ]

            # Calcular posição inicial (de baixo para cima)
            margem = 30
            espaco = 8
            total_altura = sum([draw.textbbox((0, 0), linha, font=font)[3] for linha in linhas]) + (len(linhas) - 1) * espaco
            y = combined.height - total_altura - margem

            for linha in linhas:
                bbox = draw.textbbox((0, 0), linha, font=font)
                text_height = bbox[3] - bbox[1]
                draw.text((30, y), linha, font=font, fill="white")
                y += text_height + espaco

            # Salvar imagem final
            result_path = os.path.join(UPLOAD_FOLDER, f"final_{filename}")
            combined.save(result_path)

            return send_file(result_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
