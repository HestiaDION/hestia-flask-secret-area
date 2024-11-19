from flask import Flask, request, jsonify
import requests
import pyrebase
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Configuração do logger
logging.basicConfig(level=logging.INFO)

config = {
    'apiKey': "AIzaSyCOeuoN9WcaROPhmQeTDJPHaJRO3O-k2ik",
    'authDomain': "hestia-396ff.firebaseapp.com",
    'projectId': "hestia-396ff",
    'storageBucket': "hestia-396ff.appspot.com",
    'messagingSenderId': "122637492984",
    'appId': "1:122637492984:web:5b68a7fe7035c99635510d",
    'databaseURL': ''
}

# Iniciando o Firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

@app.route('/login', methods=['POST'])
def login():
    logging.info("Requisição de login recebida.")
    
    data = request.get_json()
    logging.info(f"Dados recebidos no login: {data}")

    email = data.get('email')
    password = data.get('password')

    # Validação básica dos dados
    if not email or not password:
        logging.warning("Email ou senha ausentes.")
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    try:
        # Consultar a API externa
        logging.info(f"Consultando a API externa para o email: {email}")
        response = requests.get(f'https://hestia-api-postgres.onrender.com/token/access/{email}')
        response.raise_for_status()

        user_data = response.json()
        logging.info(f"Resposta da API externa: {user_data}")

        if user_data is None or user_data == "":
            logging.warning("Email não encontrado na API externa.")
            return jsonify({'error': 'Email não encontrado'}), 404

        # Autenticação no Firebase
        logging.info("Autenticando no Firebase.")
        user = auth.sign_in_with_email_and_password(email, password)
        token = user['idToken']
        logging.info("Autenticação bem-sucedida.")

        return jsonify({'token': token})

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao consultar a API externa: {e}")
        return jsonify({'error': 'Erro ao consultar a API externa'}), 500
    except pyrebase.exceptions.FirebaseException as e:
        logging.error(f"Erro na autenticação com Firebase: {e}")
        return jsonify({'error': 'Autenticação falhou'}), 401
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        return jsonify({'error': 'Erro inesperado no servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)