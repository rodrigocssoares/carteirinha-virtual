from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import base64
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def gerar_carteirinha(imagem, nome, cidade, pico, categoria, cor):
    user_image = imagem.convert("RGBA").resize((856, 540))
    overlay = Image.open("static/overlay.png").convert("RGBA").resize((856, 540))
    combined = Image.alpha_composite(user_image, overlay)
    draw = ImageDraw.Draw(combined)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
    except:
        font = ImageFont.load_default()

    linhas = [
        f"Atleta: {nome}",
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
        draw.text((30, y), linha, font=font, fill=cor)
        y += text_height + espaco

    return combined

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/preview", methods=["POST"])
def preview():
    nome = request.form.get("nome", "")
    cidade = request.form.get("cidade", "")
    pico = request.form.get("pico", "")
    categoria = request.form.get("categoria", "")
    cor = request.form.get("cor", "#ffffff")
    file = request.files.get("imagem")

    if not file:
        return render_template("index.html", erro="Envie uma imagem para continuar.")

    imagem = Image.open(file.stream)
    final = gerar_carteirinha(imagem, nome, cidade, pico, categoria, cor)

    buffer = BytesIO()
    final.save(buffer, format="PNG")
    imagem_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render_template("index.html", imagem_base64=imagem_base64)

@app.route("/gerar", methods=["POST"])
def gerar():
    nome = request.form.get("nome", "")
    cidade = request.form.get("cidade", "")
    pico = request.form.get("pico", "")
    categoria = request.form.get("categoria", "")
    cor = request.form.get("cor", "#ffffff")
    file = request.files.get("imagem")

    if not file:
        return render_template("index.html", erro="Envie uma imagem para continuar.")

    imagem = Image.open(file.stream)
    final = gerar_carteirinha(imagem, nome, cidade, pico, categoria, cor)

    filename = f"carteirinha_{uuid.uuid4().hex}.png"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    final.save(filepath)

    return send_file(filepath, as_attachment=True)


