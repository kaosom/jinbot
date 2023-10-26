'''
    Logica dentras de los mensajes, seguir el flujo de la conversacion. 
'''

import smtplib
import json
import requests
from .database import DB
from . import sett
from .sett import TOTAL_SOLICITUDES


def obtener_mensaje_whatsapp(message):
    '''
        Verficicamos que sea un mensaje valido. 
    '''
    if 'type' not in message:
        text = 'mensaje no reconocido'
        return text

    type_message = message['type']
    if type_message == 'text':
        text = message['text']['body']
    elif type_message == 'button':
        text = message['button']['text']
    elif type_message == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif type_message == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no procesado'

    return text


def enviar_mensaje_whatsapp(data):
    '''
        Logica detras de enviar el mensaje con toda la informacion. 
    '''
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        response = requests.post(whatsapp_url, headers=headers, data=data, timeout=10)

        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e, 403


def text_message(number, text):
    '''
        Se le da el fomato de json a nuestra variable data para poder 
        trabajar con ella. 
    '''
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                    "body": text
            }
        }
    )
    return data


def button_reply_message(number, options, body, footer, sedd):
    '''
        Funcion para poder asignar los botones. 
    '''
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data


def reply_reaction_message(number, message_id, emoji):
    '''
        Asignar una reaccion al mensaje enviado de acuerdo a su id. 
    '''
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": message_id,
                "emoji": emoji
            }
        }
    )
    return data


def replytext_message(number, message_id, text):
    '''
        Respondemos al chat una vez seleccionado un boton.
    '''
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": {"message_id": message_id},
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data


def replace_start(s):
    '''
        En el formato original los numeros aparecen con 521 y se 
        cambia para que solamente tenga el 52. 
    '''
    if s.startswith("521"):
        return "52" + s[3:]
    else:
        return s


def mark_read_message(message_id):
    '''
        Marcamos como leido el mensake. 
    '''
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  message_id
        }
    )
    return data


def send_mail(datos):
    '''
        Logica detras del envio de correos electronicos a todos los usuarios
        con los resultados. 
    '''
    name_account = "ComPasion"
    email_account = "compasion.work@gmail.com"
    password_account = "yrtrzrhvtovtaqlt"

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(email_account, password_account)

    subject = 'Status de convocatoria ComPasion. 💵'
    for dato in datos:
        number = dato[0]
        name = dato[1]
        justification = dato[2]
        dinero = dato[3]
        link = dato[4]
        email = dato[5]
        status = dato[7]

        if status:
            message = "Felicidades!! Has conseguido el apoyo economico por parte de ComPasion. 😁"
        else:
            message = "Lamentamos informarte que tu apoyo por parte de ComPasion ha sido rechazado. 😔\n"

        message += f'Tu informacion registrada fue la siguiente:\nNumero: {number}\nNombre del Proyecto: {name}\nJustificacion: {justification}\nCantidad de dinero: {dinero}\nLink a video de YouTube: {link}'
        sent_email = ("From: {0} <{1}>\n"
                      "To: {2} <{3}>\n"
                      "Subject: {4}\n\n"
                      "{5}"
                      .format(name_account, email_account, name, email, subject, message))
        print(sent_email)
        try:
            server.sendmail(email_account, [email], sent_email)
        except Exception:
            print('Could not send email to {}. Error: {}\n'.format(email, str(Exception)))

    # Close smtp server
    server.close()


def administrar_chatbot(text, number, message_id):
    '''
        Logica detras del envio de mensajes. 
    '''
    base = DB()
    # Definimos las variables iniciales
    counter = base.recuperar_posicion(number) or 0
    total = base.get_total() or 0
    admin_mode = base.get_status_encuesta_finalizada() or 0
    # Se le da formato al texto.
    text = text.lower().strip()
    #Reiniciamos los valores
    if 'reiniciar.mecatr0nica.database' in text:
        base.formatear()
        return
    if 'reiniciar.mecatr0nica.evaluadores' in text:
        base.formatear()
        return
    if 'reiniciar.mecatr0nica.global' in text:
        base.formatear()
        return
    print('Counter -> ', counter)
    print('Mensaje -> ', text)
    list = []
    # Marcamos el mensaje como leido
    mark_read = mark_read_message(message_id)
    list.append(mark_read)
    if total <= TOTAL_SOLICITUDES and not admin_mode:

        if total == TOTAL_SOLICITUDES:
            # Tenemos que dividir cuanto les toca a cada uno
            # PENDIENTE 
            # Aqui cambiamos el admin_mode
            base.set_status_encuesta_finalizada()
            #Insertamos a los administradores
            datos = base.get_all_information()
            i = 0
            datos_por_administrador = len(datos) / len(sett.administradores)
            for admin in sett.administradores:
                print(admin)
                # Asigna los rangos en los que se va a mandar los mensajes asi como inserta admins
                base.set_datos_administradores(admin, i + 1, i + datos_por_administrador)
                i += datos_por_administrador
                message = "Iniciamos con la valoracion de solicitudes. Por favor escribe la palabra 'empezar' para comenzar."
                enviar_mensaje_whatsapp(text_message(admin, message))
            
        if counter == 0:
            body = "¡Hola! 👋 Bienvenido a ConPasion. ¿Cómo podemos ayudarte hoy?"
            footer = "Equipo Compasion"
            options = ["✅ Manual", "🤲 Quienes somos"]

            reply_button_data = button_reply_message(
                number, options, body, footer, "sed1")
            replyReaction = reply_reaction_message(number, message_id, "🫡")
            list.append(replyReaction)
            list.append(reply_button_data)
            base.modificar_posicion(number, counter)
        elif "manual" in text and len(text.split()) == 2 and counter == 1 :
            body = "En el orden que se te vaya pidiendo deberás escribir los siguientes datos:\n1. Nombre del proyecto que requiere un apoyo economico.\n2. Justificacion del proyecto (menos de 100 palabras)\n3.Cantidad de dinero.\n4. Video subido a YT para mostrar el proyecto.\n5. Correo para mandar resultados."
            footer = "ComPasion Contigo."
            options = ["✅ Empezar",
                       "❌ Cancelar"]

            reply_button_data = button_reply_message(
                number, options, body, footer, "sed2")
            list.append(reply_button_data)
            base.modificar_posicion(number, counter)
        elif "quienes somos" in text and len(text.split()) == 3 and counter == 1:
            body = "Somos Canico, una empresa dedicada a la innovación y excelencia en el desarrollo de software 👌. A través de nuestro proyecto de ayuda comunitaria 💟'conpasión'💟, nos esforzamos por hacer una diferencia positiva en la sociedad 💁🏻. Nuestra misión es crear software innovador que cumpla con los más altos estándares de calidad, seguridad y rendimiento, proporcionando herramientas a nuestros clientes para agilizar procesos administrativos, mejorando su eficiencia y productividad 😎.Nuestra visión es ser líderes en el mercado, reconocidos por nuestra excelencia en el desarrollo de soluciones tecnológicas vanguardistas que permiten la recopilación de información de manera normativa y responsable 😀. Nos dedicamos a apoyar a organizaciones de diversos sectores, brindándoles soluciones para capturar, analizar y recopilar información, fomentando la innovación y promoviendo la confianza en la era digital👾."
            footer = "ComPasion Contigo."
            options = ["✅ Manual"]

            reply_button_data = button_reply_message(
                number, options, body, footer, "sed2")

            list.append(reply_button_data)
        elif "empezar" in text and len(text.split()) == 2 and counter == 2:
            data = text_message(
                number, "Por favor escribe el nombre del proyecto.😊")
            list.append(data)
            base.modificar_posicion(number, counter)
        elif counter == 3:
            print('Dato a guardar en la base: ', text)
            base.insertar(number, text, 'nombre')
            body = "Nombre registrado correctamente.\n¿Quieres modificar el nombre o continuar? 👀"
            footer = "Equipo ComPasion"
            options = ["✅ Continuar", "❌ Modificar"]

            button_reply = button_reply_message(
                number, options, body, footer, "sed3")
            list.append(button_reply)
            base.modificar_posicion(number, counter)
        elif "cancelar" in text and len(text.split()) == 2:
            data = text_message(
                number, "Operacion cancelada. Que tengas un buen día. 😊")
            list.append(data)
            base.modificar_posicion(number, counter, position= 0)
        elif "modificar" in text and len(text.split()) == 2 and counter == 4:
            data = text_message(
                number, "Escribe nuevamente el nombre. 😊")
            list.append(data)
            base.modificar_posicion(number, counter, position=3)
        elif "continuar" in text and len(text.split()) == 2 and counter == 4:
            data = text_message(
                number, "Por favor escribe la justificacion.😊")
            list.append(data)
            base.modificar_posicion(number, counter)
        elif counter == 5:
            if len(text.split()) > 100:
                data = text_message(
                    number, "Recuerda que tienen que ser menos de 100 palabras. Por favor vuelve a escribirla.😊")
                list.append(data)
            else:
                print('Dato a guardar en la base: ', text)
                base.insertar(number, text, 'justificacion')
                body = "Justificacion registrado correctamente.\n¿Quieres modificar el nombre o continuar? 👀"
                footer = "Equipo ComPasion"
                options = ["✅ Continuar", "❌ Modificar"]

                button_reply = button_reply_message(
                    number, options, body, footer, "sed3")
                list.append(button_reply)
                base.modificar_posicion(number, counter)
        elif "modificar" in text and len(text.split()) == 2 and counter == 6:
            data = text_message(
                number, "Escribe nuevamente la justificacion. 😊")
            list.append(data)
            base.modificar_posicion(number, counter, position=5)
        elif "continuar" in text and len(text.split()) == 2 and counter == 6:
            data = text_message(
                number, "Por favor escribe la cantidad de dinero.😊")
            list.append(data)
            base.modificar_posicion(number, counter)

        elif counter == 7:
            print('Dato a guardar en la base: ', text)
            base.insertar(number, text, 'dinero')
            body = "Cantidad de dinero registrada.\n¿Quieres modificar la cantidad de dinero o continuar? 👀"
            footer = "Equipo ComPasion"
            options = ["✅ Continuar", "❌ Modificar"]
            button_reply = button_reply_message(
                number, options, body, footer, "sed3")
            list.append(button_reply)
            base.modificar_posicion(number, counter)
        elif "modificar" in text and len(text.split()) == 2 and counter == 8:
            data = text_message(
                number, "Escribe nuevamente la cantidad de dinero. 😊")
            list.append(data)
            base.modificar_posicion(number, counter, position=7)
        elif "continuar" in text and len(text.split()) == 2 and counter == 8:
            data = text_message(
                number, "Ingrese unicamente la URL del video de YouTube.😊\nPor favor asegurese que incluya 'youtube.com' dentro del link para validarlo. 😌")
            list.append(data)
            base.modificar_posicion(number, counter)

        elif counter == 9:
            if 'youtube.com' in text:
                body = "Video registrado.\n¿Quieres modificar la url o continuar? 👀"
                footer = "Equipo ComPasion"
                options = ["✅ Continuar", "❌ Modificar"]
                button_reply = button_reply_message(
                    number, options, body, footer, "sed3")
                list.append(button_reply)
                base.modificar_posicion(number, counter)
                print('Dato a guardar en la base: ', text)
                base.insertar(number, text, 'video')
            else:
                data = text_message(
                    number, "Recuerda que tiene que ser un link de YouTube valido.😊")
                list.append(data)
        elif "modificar" in text and len(text.split()) == 2 and counter == 10:
            data = text_message(
                number, "Escribe nuevamente la URL. 😊")
            list.append(data)
            base.modificar_posicion(number, counter, position=9)
        elif "continuar" in text and len(text.split()) == 2 and counter == 10:
            data = text_message(
                number, "Ingrese su correo electronico. 📧")
            list.append(data)
            base.modificar_posicion(number, counter)

        elif counter == 11:
            if '@' in text:
                print('Dato a guardar en la base: ', text)
                base.insertar(number, text, 'correo')
                body = "Correo registrado correctamente.\n¿Quieres modificar el correo o continuar? 👀"
                footer = "Equipo ComPasion"
                options = ["✅ Continuar", "❌ Modificar"]
                button_reply = button_reply_message(
                    number, options, body, footer, "sed3")
                list.append(button_reply)
                base.modificar_posicion(number, counter)
            else:
                data = text_message(
                    number, "Recuerda que tiene que ser un correo valido.😊")
                list.append(data)
        elif "modificar" in text and len(text.split()) == 2 and counter == 12:
            data = text_message(
                number, "Escribe nuevamente el correo. 😊")
            list.append(data)
            base.modificar_posicion(number, counter, position=11)
        elif "continuar" in text and len(text.split()) == 2 and counter == 12:
            data = text_message(
                number, "Muchas gracias por toda su informacion, se le enviara un correo indicando su status. 🕛")
            list.append(data)
            base.modificar_posicion(number, counter)
        else:
            data = text_message(
                number, "Por favor selecciona una opción valida. 👀")
            list.append(data)
    else:
        if number in sett.administradores: #Aqui se agrega la conficion que su estatus no este terminado
            # Recuperamos el counter de admin para saber en que paso se encuentra
            admin_counter = base.get_counter_admin_mode(number)
            print('admin counter: ', admin_counter)
            if admin_counter == 0:
                # En esta parte es cuando se les manda el menasje sobre la propuesta
                limite_inferior, limite_superior = base.get_rango_de_evaluacion(
                    number)
                print(f'De {limite_inferior} a {limite_superior}')
                indice_dentro_del_rango = base.get_indice_dentro_del_rango(number)
                print(f"Indice dentro del rango -> {indice_dentro_del_rango}")
                # Mantenemos las inspecciones dentro del rango indicado.
                if (limite_superior - limite_inferior) + 1 >= indice_dentro_del_rango:
                    if 'empezar' in text:
                        print(indice_dentro_del_rango)
                        body = base.get_solo_una_informacion(indice_dentro_del_rango)
                        footer = f"Propuesta No. {indice_dentro_del_rango}"
                        options = ["✅ Aceptar", "❌ Rechazar"]
                        reply_button_data = button_reply_message(
                            number, options, body, footer, "sed1")
                        list.append(reply_button_data)

                    elif 'continuar' in text:
                        print(indice_dentro_del_rango)
                        body = base.get_solo_una_informacion(indice_dentro_del_rango + 1)
                        footer = f"Propuesta No. {indice_dentro_del_rango + 1}"
                        options = ["✅ Aceptar", "❌ Rechazar"]
                        reply_button_data = button_reply_message(
                            number, options, body, footer, "sed1")
                        list.append(reply_button_data)
                        base.update_indices(number, indice_dentro_del_rango + 1)

                    if 'aceptar' in text:
                        print(indice_dentro_del_rango + 1)
                        base.update_indices(number, indice_dentro_del_rango )
                        base.set_status(indice_dentro_del_rango, 1)
                        body = 'Siguiente propuesta.'
                        footer = f"Propuesta No. {indice_dentro_del_rango}"
                        options = ["✅ Continuar"]
                        reply_button_data = button_reply_message(
                            number, options, body, footer, "sed1")
                        list.append(reply_button_data)
                    if 'rechazar' in text:
                        base.update_indices(number, indice_dentro_del_rango + 1)
                        base.set_status(indice_dentro_del_rango, 0)
                        body = 'Presiona continuar para ver la siguiente propuesta.'
                        footer = f"Propuesta No. {indice_dentro_del_rango}"
                        options = ["✅ Continuar"]
                        reply_button_data = button_reply_message(
                            number, options, body, footer, "sed1")
                        list.append(reply_button_data)
                else:
                    message = "Gracias por resolver tu parte de la evulación. Ha acabado tu trabajo 👀."
                    enviar_mensaje_whatsapp(text_message(number, message))
                    #Se cambia el estado del evaluadador para saber que ya termino.
                    # PENDIENTE
            else: 
                # Se le suma uno al counter del admin
                base.set_counter_admin_mode(number, admin_counter)
    for item in list:
        print(item)
        enviar_mensaje_whatsapp(item)
