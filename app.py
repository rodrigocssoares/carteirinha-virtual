
from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
OVERLAY_PATH = 'static/overlay.png'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def generate_card(img_path, nome, cidade, pico, categoria, cor_texto, result_filename):
    base = Image.open(img_path).convert("RGBA").resize((856, 540))
    overlay = Image.open(OVERLAY_PATH).convert("RGBA").resize((856, 540))
    base.paste(overlay, (0, 0), overlay)

    draw = ImageDraw.Draw(base)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, 22)
    except:
        font = ImageFont.load_default()

    texto = f"Atleta: {nome}\nCidade: {cidade}\nPico: {pico}\nCategoria: {categoria}"

    bbox = draw.textbbox((0, 0), texto, font=font)
    text_height = bbox[3] - bbox[1]
    text_position = (40, base.height - text_height - 40)

    draw.text(text_position, texto, fill=cor_texto, font=font)

    result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
    base.save(result_path)
    return result_path

@app.route('/', methods=['GET', 'POST'])
def index():
    imagem_gerada = None
    nome = cidade = pico = categoria = cor = ''
    result_path = img_path = ''
    if request.method == 'POST':
        nome = request.form.get('nome', '')
        cidade = request.form.get('cidade', '')
        pico = request.form.get('pico', '')
        categoria = request.form.get('categoria', '')
        cor = request.form.get('cor', '#FFFFFF')
        acao = request.form.get('acao')

        img_path = request.form.get("imagem_path", OVERLAY_PATH)
        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem and imagem.filename:
                filename = secure_filename(imagem.filename)
                img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagem.save(img_path)

        result_filename = f"final_{secure_filename(nome)}.png"
        result_path = generate_card(img_path, nome, cidade, pico, categoria, cor, result_filename)

        if acao == 'visualizar':
            imagem_gerada = result_path
        elif acao == 'baixar':
            return send_file(result_path, as_attachment=True)

    return render_template(
        "index.html",
        nome=nome,
        cidade=cidade,
        pico=pico,
        categoria=categoria,
        cor=cor,
        imagem_gerada=result_path,
        imagem_path=img_path
    )

if __name__ == "__main__":
    app.run(debug=True)
