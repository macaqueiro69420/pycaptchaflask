# PyCaptchaFlask

Uma aplicação Flask simples com funcionalidade de CAPTCHA em um único arquivo (`app.py`), fácil de incorporar em outros projetos Flask.

## Funcionalidades

- Geração de imagens CAPTCHA com número configurável de caracteres
- Verificação não sensível a maiúsculas/minúsculas
- HTML hard-coded (sem templates separados)
- API endpoints para integração com outras aplicações
- Função auxiliar para incorporação em outros projetos Flask

## Requisitos

- Python 3.8+
- Flask
- Pillow (PIL)

## Instalação

1. Clone o repositório:
```
git clone https://github.com/macaqueiro69420/pycaptchaflask.git
cd pycaptchaflask
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Execute a aplicação:
```
python app.py
```

## Uso

### Executar o demo

Após iniciar o aplicativo:

1. Acesse `http://127.0.0.1:5000/` em seu navegador
2. Você verá um formulário com uma imagem CAPTCHA
3. Digite os caracteres exibidos e clique em "Verificar"
4. O resultado da verificação será exibido na página

Para alterar o número de caracteres no CAPTCHA, use o parâmetro `length` na URL:
```
http://127.0.0.1:5000/?length=4
```

### Integrar em outros projetos Flask

O aplicativo foi projetado para ser facilmente integrado em outros projetos Flask:

```python
from flask import Flask, request, render_template_string
app = Flask(__name__)
app.secret_key = 'seu-segredo'

# Importar as funções necessárias do app.py
from app import init_captcha, generate_captcha, validate_captcha

# Inicializar CAPTCHA em seu aplicativo
init_captcha(app)

@app.route('/meu-formulario', methods=['GET', 'POST'])
def meu_formulario():
    mensagem = ""
    
    if request.method == 'POST':
        captcha_input = request.form.get('captcha')
        captcha_text = session.get('captcha_text')
        
        if validate_captcha(captcha_input, captcha_text):
            # CAPTCHA válido, processar o formulário
            mensagem = "CAPTCHA correto! Formulário enviado."
        else:
            mensagem = "CAPTCHA incorreto. Tente novamente."
    
    # Gerar nova imagem CAPTCHA
    captcha_img, captcha_text = generate_captcha(length=5)  # 5 caracteres
    session['captcha_text'] = captcha_text
    
    # Renderizar template com a imagem CAPTCHA
    return render_template_string('''
        <form method="post">
            <img src="data:image/png;base64,{{ captcha_img }}" alt="CAPTCHA">
            <input type="text" name="captcha" required>
            <button type="submit">Enviar</button>
            <p>{{ mensagem }}</p>
        </form>
    ''', captcha_img=captcha_img, mensagem=mensagem)

if __name__ == '__main__':
    app.run(debug=True)
```

### Uso da API

O aplicativo também fornece endpoints de API para usar em aplicações frontend separadas:

1. Gerar um novo CAPTCHA:
```
GET /api/captcha?length=6
```
Resposta:
```json
{
  "image": "base64_encoded_image_data",
  "token": "unique_token"
}
```

2. Verificar um CAPTCHA:
```
POST /api/verify
Content-Type: application/json

{
  "token": "token_from_previous_request",
  "captcha": "user_input"
}
```
Resposta:
```json
{
  "success": true|false
}
```

## Licença

MIT