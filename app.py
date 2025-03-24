import os
import uuid
from flask import Flask, request, render_template, send_from_directory
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['GENERATED_FOLDER'] = 'static/generated'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = None
    if request.method == 'POST':
        nome = request.form.get('nome')
        cidade = request.form.get('cidade')
        pico = request.form.get('pico')
        categoria = request.form.get('categoria')
        cor = request.form.get('cor') or "#FFFFFF"
        imagem = request.files.get('imagem')

        if imagem and nome and cidade:
            temp_filename = f"{uuid.uuid4().hex}.png"
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            output_path = os.path.join(app.config['GENERATED_FOLDER'], temp_filename)
            imagem.save(input_path)

            overlay = Image.open("static/overlay.png").convert("RGBA")
            base = Image.open(input_path).convert("RGBA")
            base = base.resize(overlay.size)

            combined = Image.alpha_composite(base, overlay)

            draw = ImageDraw.Draw(combined)
            font = ImageFont.truetype("arial.ttf", 30)

            texto = f"Atleta: {nome}\nCidade: {cidade}\nPico: {pico}\nCategoria: {categoria}"
            draw.text((30, 390), texto, font=font, fill=cor)

            combined.save(output_path)
            image_url = output_path

    return render_template("index.html", image_url=image_url)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['GENERATED_FOLDER'], filename, as_attachment=True)
