# PyCaptchaFlask

Uma aplicação Flask que implementa funcionalidade de CAPTCHA para proteger formulários contra bots e spam.

## Funcionalidades

- Geração de imagens CAPTCHA
- Verificação de respostas de CAPTCHA
- Proteção de formulários contra submissões automatizadas
- Exemplo de integração em formulário de login

## Requisitos

- Python 3.8+
- Flask
- Pillow (PIL)
- Flask-WTF

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

## Estrutura do Projeto

```
pycaptchaflask/
│
├── app.py                  # Aplicação principal Flask
├── captcha/                # Módulo de CAPTCHA
│   ├── __init__.py
│   ├── generator.py        # Gerador de imagens CAPTCHA
│   └── validator.py        # Validador de respostas CAPTCHA
│
├── static/                 # Arquivos estáticos (CSS, JS, etc.)
│   ├── css/
│   └── js/
│
├── templates/              # Templates HTML
│   ├── base.html
│   ├── index.html
│   └── form.html
│
└── requirements.txt        # Dependências do projeto
```

## Uso

Exemplo de como usar o CAPTCHA em um formulário Flask:

```python
from flask import Flask, render_template, request, redirect, url_for
from captcha.generator import generate_captcha
from captcha.validator import validate_captcha

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_response = request.form.get('captcha')
        
        if validate_captcha(user_response):
            return redirect(url_for('success'))
        else:
            return render_template('index.html', error='CAPTCHA incorreto')
    
    captcha_image, captcha_text = generate_captcha()
    # Salvar captcha_text na sessão ou em cache
    
    return render_template('index.html', captcha_image=captcha_image)
```

## Licença

MIT