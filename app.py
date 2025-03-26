from flask import Flask, request, render_template, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
OVERLAY_PATH = 'static/overlay.png'
CSV_PATH = 'data/ListaAtletas.csv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def carregar_dados_atleta(id_atleta):
    df = pd.read_csv(CSV_PATH)
    atleta = df[df['ID'] == int(id_atleta)]
    if not atleta.empty:
        return atleta.iloc[0]['Nome'], atleta.iloc[0]['Categoria']
    return None, None

def generate_card(img_path, nome, estado, cidade, categoria, cor_texto, result_filename):
    base = Image.open(img_path).convert("RGBA").resize((856, 540))
    overlay = Image.open(OVERLAY_PATH).convert("RGBA").resize((856, 540))
    base.paste(overlay, (0, 0), overlay)

    draw = ImageDraw.Draw(base)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, 28)
    except:
        font = ImageFont.load_default()

    linha1 = nome
    linha2 = f"{cidade} - {estado}"
    linha3 = f"Categoria: {categoria}"
    texto = f"{linha1}\n{linha2}\n{linha3}"

    bbox = draw.textbbox((0, 0), texto, font=font)
    text_height = bbox[3] - bbox[1]
    text_position = (40, base.height - text_height - 40)

    draw.multiline_text(text_position, texto, fill=cor_texto, font=font, spacing=4)

    result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
    base.save(result_path)
    return result_path

@app.route('/', methods=['GET', 'POST'])
def index():
    df = pd.read_csv(CSV_PATH).sort_values(by="Nome")
    imagem_gerada = None
    erro = ''
    nome = estado = cidade = categoria = cor = ''
    id_atleta = ''
    img_path = ''

    if request.method == 'POST':
        id_atleta = request.form.get('id_atleta', '')
        estado = request.form.get('estado', '')
        cidade = request.form.get('cidade', '')
        cor = request.form.get('cor', '#FFFFFF')
        acao = request.form.get('acao')

        nome, categoria = carregar_dados_atleta(id_atleta)
        if not nome:
            erro = "ID do atleta não encontrado."
            return render_template('index.html', erro=erro, id_atleta=id_atleta, atletas=df)

        img_path = request.form.get('imagem_path', '')

        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem and imagem.filename:
                filename = secure_filename(imagem.filename)
                img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagem.save(img_path)

        if not img_path or not os.path.exists(img_path):
            erro = "Imagem não encontrada."
            return render_template('index.html', erro=erro, id_atleta=id_atleta, atletas=df)

        result_filename = f"final_{secure_filename(nome)}.png"
        result_path = generate_card(img_path, nome, estado, cidade, categoria, cor, result_filename)

        if acao == 'visualizar':
            imagem_gerada = result_path
        elif acao == 'baixar':
            return send_file(result_path, as_attachment=True)

        return render_template("index.html", atletas=df, id_atleta=id_atleta, nome=nome, estado=estado,
                               cidade=cidade, categoria=categoria, cor=cor,
                               imagem_gerada=imagem_gerada, imagem_path=img_path)

    return render_template("index.html", atletas=df)

@app.route('/buscar_atleta', methods=['POST'])
def buscar_atleta():
    id_atleta = request.form.get('id_atleta')
    nome, categoria = carregar_dados_atleta(id_atleta)
    if nome:
        return jsonify({'nome': nome, 'categoria': categoria})
    return jsonify({'erro': 'ID não encontrado'}), 404

if __name__ == "__main__":
    app.run(debug=True)
