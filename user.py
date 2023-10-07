
class User:
    def __init__(self):
        self.nombre = None
        self.justificacion = None
        self.dinero = None
        self.link = None
        self.correo = None

    def setNombre(self, nombre):
        self.nombre = nombre

    def setJustificacion(self, justificacion):
        self.justificacion = justificacion

    def setDinero(self, dinero):
        self.dinero = dinero

    def setLink(self, link):
        self.link = link

    def setCorreo(self, correo):
        self.correo = correo
