from flask import Flask, request, render_template, send_file, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def generate_card(img_path, nome, cidade, pico, categoria, cor_texto, result_filename):
    base = Image.open(img_path).convert("RGBA")
    draw = ImageDraw.Draw(base)

    font = ImageFont.load_default()

    texto = f"Atleta: {nome}\nCidade: {cidade}\nPico: {pico}\nCategoria: {categoria}"

    draw.text((20, base.height - 100), texto, fill=cor_texto, font=font)

    result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
    base.save(result_path)
    return result_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form.get('nome', '')
        cidade = request.form.get('cidade', '')
        pico = request.form.get('pico', '')
        categoria = request.form.get('categoria', '')
        cor_texto = request.form.get('cor', '#FFFFFF')
        acao = request.form.get('acao')

        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem and imagem.filename != '':
                filename = secure_filename(imagem.filename)
                img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagem.save(img_path)
                request.environ['img_path'] = img_path
            else:
                img_path = request.environ.get('img_path', '')
        else:
            img_path = request.environ.get('img_path', '')

        if img_path:
            result_filename = f"final_{secure_filename(nome)}.png"
            result_path = generate_card(img_path, nome, cidade, pico, categoria, cor_texto, result_filename)

            if acao == 'visualizar':
                return render_template('index.html', nome=nome, cidade=cidade, pico=pico, categoria=categoria, cor=cor_texto, imagem_gerada=result_path)
            elif acao == 'baixar':
                return send_file(result_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
