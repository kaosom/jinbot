from gevent import monkey
monkey.patch_all()

from flask import Flask, request
from recursos.sett import token as tk
from recursos.services import replace_start, obtener_Mensaje_whatsapp, administrar_chatbot
import gevent.pywsgi

app = Flask(__name__)


@app.route('/webhook', methods=['GET'])  # type: ignore
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == tk and challenge is not None:
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return e, 403


@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = replace_start(message['from'])
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        text = obtener_Mensaje_whatsapp(message)
        administrar_chatbot(text, number, messageId)
        return 'enviado'

    except Exception as e:
        return 'no enviado ' + str(e)


if __name__ == '__main__':
    http_server = gevent.pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()