from flask import Flask, session, request, redirect, Response
from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
import base64
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Necessário para usar sessões

def generate_captcha(length=6):
    """
    Gera uma imagem CAPTCHA com o número especificado de caracteres.
    
    Args:
        length (int): Número de caracteres no CAPTCHA
    
    Returns:
        tuple: (image_base64, captcha_text)
    """
    # Criar imagem com fundo branco
    width, height = 30 * length + 40, 80
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Gerar texto aleatório para o CAPTCHA
    characters = string.ascii_letters + string.digits
    captcha_text = ''.join(random.choice(characters) for _ in range(length))
    
    # Tentar carregar uma fonte, com fallback para a fonte padrão do PIL
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()
    
    # Desenhar texto
    draw.text((20, 20), captcha_text, font=font, fill=(0, 0, 128))
    
    # Adicionar ruído (linhas e pontos)
    for _ in range(8):
        # Linhas aleatórias
        line_color = (
            random.randint(0, 180),
            random.randint(0, 180),
            random.randint(0, 180)
        )
        draw.line(
            [
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height))
            ],
            fill=line_color,
            width=2
        )
    
    # Adicionar pontos de ruído
    for _ in range(width * height // 50):
        dot_color = (
            random.randint(0, 200),
            random.randint(0, 200),
            random.randint(0, 200)
        )
        draw.point(
            (random.randint(0, width), random.randint(0, height)),
            fill=dot_color
        )
    
    # Converter imagem para base64 para exibir no HTML
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_str, captcha_text

def validate_captcha(user_input, correct_text):
    """
    Valida a resposta do usuário ao CAPTCHA.
    
    Args:
        user_input (str): Texto inserido pelo usuário
        correct_text (str): Texto correto do CAPTCHA
    
    Returns:
        bool: True se a validação for bem-sucedida, False caso contrário
    """
    if not user_input or not correct_text:
        return False
    return user_input.lower() == correct_text.lower()  # Não case sensitive

# HTML templates hard-coded
HTML_START = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask CAPTCHA Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        form { margin-top: 20px; }
        label { display: block; margin-bottom: 5px; }
        input[type="text"] { padding: 8px; width: 100%; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #45a049; }
        .captcha-img { margin: 15px 0; }
        .success { color: green; font-weight: bold; }
        .error { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Flask CAPTCHA Demo</h1>
"""

HTML_END = """
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    
    if request.method == 'POST':
        user_input = request.form.get('captcha', '')
        captcha_text = session.get('captcha_text', '')
        
        # Verificar se o CAPTCHA está correto
        if validate_captcha(user_input, captcha_text):
            message = '<p class="success">CAPTCHA correto! Formulário enviado com sucesso.</p>'
        else:
            message = '<p class="error">CAPTCHA incorreto. Tente novamente.</p>'
    
    # Gerar novo CAPTCHA (tanto para GET quanto para POST)
    captcha_length = request.args.get('length', 6, type=int)  # Permitir configurar o tamanho via query param
    captcha_img, captcha_text = generate_captcha(captcha_length)
    
    # Armazenar texto do CAPTCHA na sessão
    session['captcha_text'] = captcha_text
    
    # Criar HTML com o CAPTCHA embutido
    form_html = f"""
        {message}
        <form method="post">
            <p>Digite os caracteres que você vê na imagem abaixo:</p>
            <div class="captcha-img">
                <img src="data:image/png;base64,{captcha_img}" alt="CAPTCHA">
            </div>
            <label for="captcha">Texto do CAPTCHA:</label>
            <input type="text" id="captcha" name="captcha" required>
            <button type="submit">Verificar</button>
        </form>
        <p><small>Dica: Para alterar o número de caracteres, use ?length=X na URL</small></p>
    """
    
    # Combinar o HTML
    return HTML_START + form_html + HTML_END

@app.route('/api/captcha')
def get_captcha():
    """
    API endpoint para obter um novo CAPTCHA.
    Retorna JSON com a imagem base64 e um token para validação.
    """
    captcha_length = request.args.get('length', 6, type=int)
    captcha_img, captcha_text = generate_captcha(captcha_length)
    
    # Armazenar na sessão
    token = os.urandom(8).hex()
    session[f'captcha_{token}'] = captcha_text
    
    return {
        'image': captcha_img,
        'token': token
    }

@app.route('/api/verify', methods=['POST'])
def verify_captcha():
    """
    API endpoint para verificar um CAPTCHA.
    """
    data = request.get_json()
    if not data:
        return {'success': False, 'error': 'Dados JSON ausentes'}, 400
    
    token = data.get('token')
    user_input = data.get('captcha')
    
    if not token or not user_input:
        return {'success': False, 'error': 'Token ou texto CAPTCHA ausente'}, 400
    
    # Obter texto CAPTCHA correto da sessão
    session_key = f'captcha_{token}'
    correct_text = session.get(session_key)
    
    if not correct_text:
        return {'success': False, 'error': 'Token inválido ou expirado'}, 400
    
    # Limpar o token da sessão (uso único)
    session.pop(session_key, None)
    
    # Verificar CAPTCHA
    is_valid = validate_captcha(user_input, correct_text)
    
    return {'success': is_valid}

# Função auxiliar para usar em outros projetos Flask
def init_captcha(app):
    """
    Inicializa o CAPTCHA em outro aplicativo Flask.
    
    Args:
        app: A aplicação Flask
    
    Example:
        from flask import Flask, request, render_template_string
        app = Flask(__name__)
        app.secret_key = 'seu-segredo'
        
        from app import init_captcha, generate_captcha, validate_captcha
        init_captcha(app)
        
        @app.route('/meu-formulario')
        def meu_formulario():
            captcha_img, _ = generate_captcha(4)  # 4 caracteres
            # Renderizar template com captcha_img
    """
    # Certificar-se de que a aplicação tem uma chave secreta para sessões
    if not app.secret_key:
        app.secret_key = os.urandom(24)
    
    # Adicionar as rotas API
    app.add_url_rule('/api/captcha', 'get_captcha', get_captcha)
    app.add_url_rule('/api/verify', 'verify_captcha', verify_captcha, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)