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
            # Salva imagem original
            filename = f"{uuid.uuid4().hex}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Abre a imagem carregada pelo usuário
            user_image = Image.open(filepath).convert("RGBA")

            # Redimensionar para padrão cartão de crédito (85.6 x 53.98 mm, proporção 856 x 540 px)
            user_image = user_image.resize((856, 540))

            # Abre a imagem overlay transparente
            overlay = Image.open('static/overlay.png').convert("RGBA").resize((856, 540))

            # Combina as imagens
            combined = Image.alpha_composite(user_image, overlay)

            # Adiciona o texto
            draw = ImageDraw.Draw(combined)
            font = ImageFont.load_default()

            # Exemplo de posicionamento do texto
            draw.text((30, 450), f"Nome: {nome}", font=font, fill="white")
            draw.text((30, 490), f"Cidade: {cidade}", font=font, fill="white")

            # Salva o resultado final
            result_path = os.path.join(UPLOAD_FOLDER, f"final_{filename}")
            combined.save(result_path)

            return send_file(result_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
