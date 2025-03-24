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
        file = request.files.get('imagem')

        if file:
            # Salvar a imagem original enviada pelo usuário
            filename = f"{uuid.uuid4().hex}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Abrir e preparar a imagem
            user_image = Image.open(filepath).convert("RGBA")
            user_image = user_image.resize((856, 540))

            # Abrir e redimensionar o overlay
            overlay = Image.open('static/overlay.png').convert("RGBA")
            overlay = overlay.resize((856, 540))

            # Combinar imagens
            combined = Image.alpha_composite(user_image, overlay)

            # Preparar desenho
            draw = ImageDraw.Draw(combined)

            # Tentar usar fonte negrito, senão padrão
            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
            except:
                font = ImageFont.load_default()

            # Texto a desenhar
            texto = f"{nome} - {cidade}"

            # Medir largura e altura com textbbox (Pillow 8.0+)
            bbox = draw.textbbox((0, 0), texto, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Posição: parte inferior com margem
            x = 30
            y = combined.height - text_height - 30

            draw.text((x, y), texto, font=font, fill="white")

            # Salvar imagem final
            result_path = os.path.join(UPLOAD_FOLDER, f"final_{filename}")
            combined.save(result_path)

            return send_file(result_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

