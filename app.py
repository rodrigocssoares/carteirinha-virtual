from flask import Flask, request, render_template, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = None

    if request.method == 'POST':
        atleta = request.form.get('atleta')
        cidade = request.form.get('cidade')
        pico = request.form.get('pico')
        categoria = request.form.get('categoria')
        file = request.files.get('imagem')

        if file:
            filename = f"{uuid.uuid4().hex}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            user_image = Image.open(filepath).convert("RGBA").resize((856, 540))
            overlay = Image.open('static/overlay.png').convert("RGBA").resize((856, 540))
            combined = Image.alpha_composite(user_image, overlay)
            draw = ImageDraw.Draw(combined)

            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
            except:
                font = ImageFont.load_default()

            linhas = [
                f"Atleta: {atleta}",
                f"Cidade: {cidade}",
                f"Pico: {pico}",
                f"Categoria: {categoria}"
            ]

            margem = 30
            espaco = 8
            total_altura = sum([draw.textbbox((0, 0), linha, font=font)[3] for linha in linhas]) + (len(linhas) - 1) * espaco
            y = combined.height - total_altura - margem

            for linha in linhas:
                bbox = draw.textbbox((0, 0), linha, font=font)
                text_height = bbox[3] - bbox[1]
                draw.text((30, y), linha, font=font, fill="white")
                y += text_height + espaco

            final_filename = f"final_{filename}"
            result_path = os.path.join(UPLOAD_FOLDER, final_filename)
            combined.save(result_path)

            image_url = f"/{UPLOAD_FOLDER}/{final_filename}"

    return render_template('index.html', image_url=image_url)

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
