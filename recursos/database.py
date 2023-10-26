import mysql.connector
class DB:
    '''
        Objeto para poder recuperar la base de datos. 
    '''
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="mysql-javiertevillo.alwaysdata.net",
            user="324312",
            password="Mecatr0nica",
            database='javiertevillo_chat'
        )

        self.cursor = self.connection.cursor()
        print("Conexion exitosa.")

    # ========================================
    # ADMIN MODE
    # ========================================
    
    
    def formatear(self) -> None: 
        try:
            sql = "DELETE FROM `database`"
            self.cursor.execute(sql)
            sql = "ALTER TABLE `database` AUTO_INCREMENT = 1"
            self.cursor.execute(sql)
            print("Borrado con exito y reiniciado indices con exito.")
        except Exception as e:
            print("Excepción en get_status_encuesta_finalizada: ", e)
            return 0
    def get_status_encuesta_finalizada(self) -> bool:
        '''
        Cuando se llega a un limite especifico el estado de la encuenta finalizada 
        cambia para ahora entrar en modo administrador. Aqui solamente retorna el 
        estado de dicha variable. 
        '''
        try:
            sql = "SELECT encuesta_finalizada FROM `global` WHERE referencia = 1"
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            return result[0]
        except Exception as e:
            print("Excepción en get_status_encuesta_finalizada: ", e)
            return 0

    def set_status_encuesta_finalizada(self) -> None:
        '''
        Cambiamos el estado de la encuesta finalizada para entrar en admin mode. 
        '''
        try:
            sql = f"UPDATE `global` SET encuesta_finalizada = 1 WHERE id = 1"
            # Usar 'sql' en lugar de 'self.sql'
            self.cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            print("Excepcion ocurrida en setStatusEncuestaFinalizada: ", e)

    def get_counter_admin_mode(self, telefono):
        try:
            sql = "SELECT counter FROM `evaluadores` WHERE numero_evaluador = %s"
            self.cursor.execute(sql, (telefono,))
            self.value = self.cursor.fetchone()
            return self.value[0]
        except Exception as e:
            print("Exception en recuperar posicion: ", e)

    def set_counter_admin_mode(self, telefono, admin_counter, position=None):
        '''
        El counter sirve para decir en que punto tenemos que estar dentro del flujo
        del chat, sirve para avanzar o retroceder.
        A la posicion actual se le suma un valor o en todo caso se indica con el 
        valor position = un valor para posicionarse en dicha posicion.  
        '''
        if position is None:
            if admin_counter is not None:
                admin_counter += 1
        else:
            admin_counter = position
        try:
            sql = "UPDATE `evaluadores` SET counter = %s WHERE numero_evaluador = %s"
            self.cursor.execute(sql, (admin_counter, telefono))
            self.connection.commit()
        except Exception as e:
            print("set_counter_admin_mode error: ", e)

    def set_datos(self, telefono, inicio, final):
        try:        # Corregir la columna 'numero' a 'telefono'
            if self.cursor.execute(f"SELECT numero_evaluador FROM `evaluadores` WHERE numero_evaluador = {telefono}") is not None:
                sql = f"UPDATE `evaluadores` SET inicio = %s WHERE numero_evaluador = %s"
                # Usar 'sql' en lugar de 'self.sql'
                self.cursor.execute(sql, (inicio, telefono))
                sql = f"UPDATE `evaluadores` SET final = %s WHERE numero_evaluador = %s"
                # Usar 'sql' en lugar de 'self.sql'
                self.cursor.execute(sql, (final, telefono))
            else:
                sql = f"INSERT INTO `evaluadores` (numero_evaluador, inicio, final) VALUES (%s, %s, %s)"
                self.cursor.execute(sql, (telefono, inicio, final))
            self.connection.commit()
        except Exception as e:
            print("set datos", e)

    def get_status_evaluador(self, telefono):
        try:
            sql = "SELECT status FROM `evaluadores` WHERE numero_evaluador = %s"
            self.cursor.execute(sql, (telefono,))
            result = self.cursor.fetchone()

            if result is not None:
                return result[0]

            return 0
        except Exception as e:
            print("Excepción en get_status_evaluador: ", e)
            return 0

    def get_rango_de_evaluacion(self, telefono):
        try:
            self.sql = f"SELECT inicio,final FROM `evaluadores` WHERE numero_evaluador = %s"
            self.cursor.execute(self.sql, (telefono,))
            self.value = self.cursor.fetchone()
            if self.value is not None:
                print(self.value)
                return self.value[0], self.value[1]
            return 0
        except Exception as e:
            print("Exception en recuperar posicion: ", e)

    def get_indice_dentro_del_rango(self, telefono):
        try:
            self.sql = f"SELECT indice_dentro_rango FROM `evaluadores` WHERE numero_evaluador = %s"
            self.cursor.execute(self.sql, (telefono,))
            self.value = self.cursor.fetchone()
            return self.value[0]
        except Exception as e:
            print("Exception en recuperar posicion: ", e)

    def get_indices_para_evaluar(self, telefono):
        try:
            self.sql = f"SELECT inicio, final FROM `evaluadores` WHERE numero_evaluador = %s"
            self.cursor.execute(self.sql, (telefono,))
            self.value = self.cursor.fetchone()
            if self.value is not None:
                return self.value
            return 0
        except Exception as e:
            print("Exception en recuperar posicion: ", e)

    def update_indices(self, telefono, indice):
        try:
            sql = "UPDATE `evaluadores` SET indice_dentro_rango = %s WHERE numero_evaluador = %s"
            # Usar 'sql' en lugar de 'self.sql'
            self.cursor.execute(sql, (indice, telefono))
            self.connection.commit()
        except Exception as e:
            print("Excepcion ocurrida en update_indices: ", e)
            
    def set_datos_administradores(self, telefono, inicio, final):
        '''
        En la primera vez que el contador llega el limite deseado los
        administradores registrado en sett se suben a la base de datos asi como los indices que van a recorrer. 
        '''
        try: 
            sql = f"INSERT INTO `evaluadores` (numero_evaluador, inicio, final) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (telefono, inicio, final))
        except Exception as e: 
            print("Exepcion en set_datos_administradores ", e)
        
         
    # ========================================
    # USER MODE
    # ========================================

    def get_total(self) -> int:
        '''
        Retorna el total de filas dentro de la base de datos de usuarios.
        '''
        self.sql = "SELECT id FROM `database`"
        try:
            self.cursor.execute(self.sql)
            self.value = self.cursor.fetchall()
            print("Total de solicitudes: ", len(self.value))
            return len(self.value)
        except Exception as e:
            print("Excepcion: ", e)

    def verificar_existencia(self, telefono):
        try:
            # Utiliza una consulta parametrizada para evitar la inyección SQL
            sql = "SELECT telefono FROM `database` WHERE telefono = %s"
            self.cursor.execute(sql, (telefono,))
            value = self.cursor.fetchone()

            # Si no se encuentra ningún registro, retorna False; de lo contrario, retorna True
            return value is not None
        except Exception as e:
            print("Excepción en verificar existencia:", e)
            return False  # Retorna False en caso de error

    def recuperar_posicion(self, telefono):
        '''
        Devuelve la posicion dentro del flujo del chat para mantener orden dentro 
        de la secuenta se mensajes gracias al counter.
        '''
        if self.verificar_existencia(telefono):
            try:
                self.sql = f"SELECT counter FROM `database` WHERE telefono = %s"
                self.cursor.execute(self.sql, (telefono,))
                self.value = self.cursor.fetchone()
                if self.value is not None:
                    return self.value[0]
                return 0
            except Exception as e:
                print("Exception en recuperar posicion: ", e)
        else:
            print("Retorno cero")
            return 0

    def modificar_posicion(self, telefono, counter, position=None):
        if position is None:
            if counter is not None:
                counter += 1
            self.insertar(telefono, counter, 'counter')
        else:
            counter = position
            self.insertar(telefono, position, 'counter')

    def insertar(self, telefono: str, valor, columna: str):
        if self.verificar_existencia(telefono):
            # Corregir la columna 'numero' a 'telefono'
            sql = f"UPDATE `database` SET {columna} = %s WHERE telefono = %s"
            # Usar 'sql' en lugar de 'self.sql'
            self.cursor.execute(sql, (valor, telefono))
        else:
            # Corregir la sintaxis de la inserción
            sql = f"INSERT INTO `database` (telefono, {columna}) VALUES (%s, %s)"
            # Intercambiar 'telefono' y 'valor' en la tupla de valores
            self.cursor.execute(sql, (telefono, valor))

        self.connection.commit()

    def getStatus(self, id):
        try:
            sql = "SELECT status FROM `database` WHERE id = %s"
            self.cursor.execute(sql, (id,))
            result = self.cursor.fetchone()

            if result is not None:
                return result[0]

            return 0
        except Exception as e:
            print("Excepción en funcion getStatus: ", e)
            return 0

    def set_status(self, id, status):
        try:
            sql = f"UPDATE `database` SET status = %s WHERE id = %s"
            # Usar 'sql' en lugar de 'self.sql'
            self.cursor.execute(sql, (status, id))
            self.connection.commit()
        except Exception as e:
            print("Excepcion ocurrida en setStatus: ", e)

    def get_all_information(self) -> tuple:
        '''
        Retorna la lista con todos los datos de la tabla de usuarios. 
        '''
        try:
            sql = "SELECT * FROM `database`"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            print('Result: ', result)
            print("type", type(result))
            if result is not None:
                return result
            return 0
        except Exception as e:
            print("Excepción en get_all_information: ", e)
            return 0

    def get_solo_una_informacion(self, id):
        try:
            sql = "SELECT * FROM `database` WHERE id = %s"
            self.cursor.execute(sql, (id, ))
            result = self.cursor.fetchone()
            print('Result: ', result)
            return f'Nombre: {result[2]}\nJustificacion: {result[3]}\nDinero: {result[4]},\nLink: {result[5]}'
        except Exception as e:
            print("Excepción en get-solo_una_informacion: ", e)
            return 0