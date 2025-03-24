from flask import Flask, request, render_template, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    card_url = None
    name = city = pico = categoria = color = ""
    filename = None

    if request.method == 'POST':
        name = request.form.get('name', '')
        city = request.form.get('city', '')
        pico = request.form.get('pico', '')
        categoria = request.form.get('categoria', '')
        color = request.form.get('color', '#ffffff')
        action = request.form.get('action')
        imagem_original = request.form.get('imagem_original')
        file = request.files.get('image')

        if file and file.filename != "":
            filename = f"{uuid.uuid4().hex}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
        elif imagem_original:
            filename = imagem_original
            filepath = os.path.join(UPLOAD_FOLDER, filename)
        else:
            return render_template(
                'index.html',
                name=name,
                city=city,
                pico=pico,
                categoria=categoria,
                color=color,
                card_url=None,
                imagem_original="",
                erro="Por favor, envie uma imagem."
            )

        user_image = Image.open(filepath).convert("RGBA").resize((856, 540))
        overlay = Image.open('static/overlay.png').convert("RGBA").resize((856, 540))
        combined = Image.alpha_composite(user_image, overlay)
        draw = ImageDraw.Draw(combined)

        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        except:
            font = ImageFont.load_default()

        linhas = [
            f"Atleta: {name}",
            f"Cidade: {city}",
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
            draw.text((30, y), linha, font=font, fill=color)
            y += text_height + espaco

        if action == "download":
            final_filename = f"final_{filename}"
            result_path = os.path.join(UPLOAD_FOLDER, final_filename)
            combined.save(result_path)
            return send_from_directory(UPLOAD_FOLDER, final_filename, as_attachment=True)
        else:
            preview_filename = f"preview_{filename}"
            result_path = os.path.join(UPLOAD_FOLDER, preview_filename)
            combined.save(result_path)
            card_url = f"/{UPLOAD_FOLDER}/{preview_filename}"

    return render_template(
        'index.html',
        name=name,
        city=city,
        pico=pico,
        categoria=categoria,
        color=color,
        imagem_original=filename,
        card_url=card_url
    )

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
