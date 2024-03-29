'''
    PROYECTO DE INGENIERIA DE SOFTWARE 
            JINBOT (COMPASION)

'''
from flask import Flask, request
from recursos.sett import token as tk
from recursos.services import replace_start, obtener_mensaje_whatsapp, administrar_chatbot


app = Flask(__name__)

@app.route('/webhook', methods=['GET'])  # type: ignore
def verificar_token():
    '''
        Verificamos que la conexión sea segura para poder establecer el chat.
    '''
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
    '''
        Se recuperan los datos enviados y procede a general el mensaje de vuelva.
    '''
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = replace_start(message['from'])
        message_id = message['id']
        text = obtener_mensaje_whatsapp(message)
        administrar_chatbot(text, number, message_id)
        return 'enviado'
    except Exception as e:
        return 'no enviado ' + str(e)


if __name__ == '__main__':
    app.run()