# coding: UTF-8

'''Clases y ventanas de la interfaz de pywallchanger.'''

import os
import sys
import random
import gconf
import threading
import gtk
import gtk.glade
import pygtk
import pynotify

import confhandler

PATH = os.path.abspath(os.path.dirname(sys.argv[0]))
PIX_PATH = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]),
                           "..", "pixmaps"))

STYLE_DIC = {0:"centered", 
             1:"stretched",
             2:"escaled",
             3:"zoom",
             4:"wallpaper"}

STYLE_DIC2 = {"centered":0, 
             "stretched":1,
             "escaled":2,
             "zoom":3,
             "wallpaper":4}


class Changer(threading.Thread):
    '''Hilo encargado de cambiar el fondo de pantalla
       cada x minutos.'''

    def __init__(self, wallpapers, tiempo, aleatorio, estilo):
        """Constructor, para establecer los valores iniciales"""
        self.stop_event = threading.Event()
        self.stop = False
        # Lista de rutas de los wallpapers a cambiar
        self.wallpapers = wallpapers
        # Tiempo de cambio entre cada wallpaper
        self.tiempo = tiempo
        self.aleatorio = aleatorio
        self.estilo = estilo
        # Indice del wallpaper actual
        self.index = 0
        threading.Thread.__init__(self)

    def run(self):
        '''Bucle de ejecución de la hebra.'''
        while not self.stop:
            # Hacemos el evento bloqueante
            self.stop_event.clear()
            if len(self.wallpapers):
                # Si el usuario usa Gnome
                if os.popen( "ps --user " + os.environ.get( "USER" ) + "| grep gnome-panel").readline():
                    client = gconf.client_get_default()
                    if self.aleatorio:
                        client.set_string("/desktop/gnome/background/picture_filename", self.wallpapers[random.randint(0, len(self.wallpapers)-1)])
                    else:
                        client.set_string("/desktop/gnome/background/picture_filename", self.wallpapers[self.index])
                        # Actualizamos el indice
                        self.index += 1
                        if self.index >= len(self.wallpapers):
                            self.index = 0
                        
                    client.set_string("/desktop/gnome/background/picture_options", self.estilo)
                # Si el usuario usa KDE
                # elif os.popen( "ps --user " + os.environ.get( "USER" ) + "| grep kdesktop" ).readline():
                #    cmd = "dcop kdesktop KBackgroundIface setWallpaper \"%s\" 1 " % (output_img)
                #    os.popen(cmd)
    
            # Esperamos hasta que se pase el tiempo o se avise
            self.stop_event.wait(float(self.tiempo)*60)


class Interfaz:
    '''Interfaz del programa.'''
    def __init__(self):
        '''Constructor para inicializar las variables.'''
        try:
            # Leemos el archivo de configuración
            self.wallpapers, self.tiempo, self.aleatorio, self.estilo, self.accion = confhandler.leer_configuracion()
        except confhandler.ConfigError:
            # Creamos un nuevo archivo de configuración
            self.wallpapers, self.tiempo, self.aleatorio, self.estilo, self.accion = confhandler.crear_configuracion()

        # Cargamos del archivo glade el menú
        self.glade = gtk.glade.XML(os.path.join(PATH, "pywallchanger.glade"), root="menu")
        # Conectamos todas las señales
        self.glade.signal_autoconnect(self)
        # Creamos un statusicon a partir de una imagen
        self.tray = gtk.status_icon_new_from_file(os.path.join(PIX_PATH, "pywallchanger.svg"))
        # Conectamos sus señales
        self.tray.connect("popup-menu", self.on_tray_popup_event)
        self.tray.connect("activate", self.on_tray_activate_event)
        self.tray.set_tooltip("pyWallChanger")
        # Y la hacemos visible
        self.tray.set_visible(True)
        # Indicamos que elprograma ha comenzado a funcionar
        if pynotify.init("pyWallChanger"):
            n = pynotify.Notification("pyWallChanger",
                                      "pyWallChanger se está ejecutando en la barra de tareas.",
                                      "file://" + os.path.join(PIX_PATH, "pywallchanger.svg"))
            n.show()
        # Y iniciamos la hebra que cambia los wallpapers
        self.changer = Changer(self.wallpapers, self.tiempo, self.aleatorio, self.estilo)
        self.changer.start()

    def on_tray_popup_event(self, status_icon, button, activate_time):
        # Mostramos el menú emergente
        self.glade.get_widget("menu").popup(None, None, None, button, activate_time)

    def on_tray_activate_event(self, status_icon, *args):
        if self.accion == 1:
            # Mostramos las preferencias
            configuracion = Preferencias().mostrar()
            if configuracion:
                # Establecemos nuestra nueva configuracion
                self.wallpapers, self.tiempo, self.aleatorio, self.estilo, self.accion = configuracion
                # Y se la decimos a la hebra
                self.changer.wallpapers = self.wallpapers
                self.changer.tiempo = self.tiempo
                self.changer.aleatorio = self.aleatorio
                self.changer.estilo = self.estilo
                # Avisamos a la hebra que refresque
                self.changer.stop_event.set()
        else:
            # Cargamos el siguiente fondo
            self.changer.stop_event.set()

    def on_preferencias_activate(self, widget):
        '''Mostramos el archivo de configuracion
           y obtenemos la nueva configuracion establecida
           por el usuario'''
        configuracion = Preferencias().mostrar()
        if configuracion:
            # Establecemos nuestra nueva configuracion
            self.wallpapers, self.tiempo, self.aleatorio, self.estilo, self.accion = configuracion
            # Y se la decimos a la hebra
            self.changer.wallpapers = self.wallpapers
            self.changer.tiempo = self.tiempo
            self.changer.aleatorio = self.aleatorio
            self.changer.estilo = self.estilo
            self.changer.accion = self.accion
            # Avisamos a la hebra que refresque
            self.changer.stop_event.set()

    def on_acerca_de_activate(self, widget):
        MyAboutDialog()

    def on_adelante_activate(self, widget):
        self.changer.stop_event.set()

    def on_salir_activate(self, widget):
        gtk.main_quit()
        # Avisamos a la hebra de que se pare
        self.changer.stop = True
        self.changer.stop_event.set()

class Preferencias:
    '''Clase para la ventana de preferencias
    de la aplicación.'''
    def __init__(self):
        '''Inicializa las variables de la clase.'''
        # Cargamos del archivo glade la ventana
        self.glade = gtk.glade.XML(os.path.join(PATH, "pywallchanger.glade"), root="dpreferencias")
        # Conectamos todas las señales
        self.glade.signal_autoconnect(self)
        # Creamos una variable para la ventana de preferencias
        self.window = self.glade.get_widget("dpreferencias")
        # Creamos una lista donde meter las imagenes de los wallpaper y su ruta
        self.model = gtk.ListStore(gtk.gdk.Pixbuf, str)
        # Añadimos esa lista al iconview
        self.glade.get_widget("iconview").set_model(self.model)
        # Y le decimos que va a estar en la col0
        self.glade.get_widget("iconview").set_pixbuf_column(0)
        # Ahora leemos el archivo de configuración
        try:
            wallpapers, tiempo, aleatorio, estilo, accion = confhandler.leer_configuracion()
        except confhandler.ConfigError:
            wallpapers, tiempo, aleatorio, estilo, accion = confhandler.crear_configuracion()
        # Mostramos la configuracion en la interfaz
        if wallpapers:
            for wall in wallpapers:
                if wall:
                    self.model.append([gtk.gdk.pixbuf_new_from_file_at_size(wall, 100,100), wall])
        self.glade.get_widget("spntiempo").set_value(float(tiempo))
        if aleatorio:
            self.glade.get_widget("chkbtnRandom").set_active(True)
        self.glade.get_widget("cmbEstilo").set_active(STYLE_DIC2[estilo])
        if accion == 2:
            self.glade.get_widget("rbFondo").set_active(True)
        # Finalmente mostramos la ventana
        self.window.show_all()

    def on_btnAnadir_pressed(self, widget):
        '''Muestra un filechooser para añadir una nueva
        imagen a la lista de wallpapers.'''
        # Creamos el filechooser
        filecho = gtk.FileChooserDialog("Añadir imagen...",
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_OPEN,
                                                 gtk.RESPONSE_OK))
        # Establecemos que se puedan elegir varios wallpapers
        filecho.set_select_multiple(True)
        # Creamos un filtro
        filtro = gtk.FileFilter()
        # Le establecemos el nombre
        filtro.set_name("Imágenes")
        # Le añadimos los tipos de filtro
        filtro.add_mime_type("image/png")
        filtro.add_mime_type("image/jpeg")
        filtro.add_mime_type("image/gif")
        filtro.add_pattern("*.png")
        filtro.add_pattern("*.jpg")
        filtro.add_pattern("*.gif")
        # Y le añadimos el filtro al filechooser
        filecho.add_filter(filtro)  
        # Finalmente mostramos el filechooser
        respuesta = filecho.run()
        if respuesta == gtk.RESPONSE_OK:
            # Si escogió imagen y le dió aceptar, añadimos la imagen al iconview y su ruta
            walls = filecho.get_filenames()
            if walls:
                for wall in walls:
                    self.model.append([gtk.gdk.pixbuf_new_from_file_at_size(wall, 100,100), wall])
        # Eliminamos el filechooser
        filecho.destroy()

    def on_btnEliminar_pressed(self, widget):
        '''Elimina el wallpaper seleccionado del iconview'''
        # Obtenemos el cursor del iconview
        cursor = self.glade.get_widget("iconview").get_cursor()
        if cursor:  # Si no es None
            # Nos hacemos del iterador
            iterador = self.model.get_iter(cursor[0][0])
            # Y lo eliminamos de la lista
            self.model.remove(iterador)

    def on_btnLimpiar_pressed(self, widget):
        '''Limpia el contenido del iconview'''
        self.model.clear()

    def mostrar(self):
        '''Muestra la ventana de preferencias y devuelve:
            None si el usuario canceló o una tupla con wallpapers y tiempo.'''
        # Mostramos el dialogo
        respuesta = self.window.run()
        # Si el usuario ha aceptado
        if respuesta == gtk.RESPONSE_OK:
            # Obtenemos los wallpapers
            # Obtenemos un iterador que apunta a la primera fila de los wallpapers
            iterador = self.model.get_iter_first()
            wallpapers = []
            # Recorremos la lista añadiendo la ruta de los wallpapers
            while iterador is not None:
                wallpapers.append(self.model.get_value(iterador, 1))
                iterador = self.model.iter_next(iterador)
            # Obtenemos el tiempo
            tiempo = str(self.glade.get_widget("spntiempo").get_value())
            # Obtenemos el aleatorio
            aleatorio = False
            if self.glade.get_widget("chkbtnRandom").get_active():
                aleatorio = True
            # Obtenemos el estilo
            estilo = STYLE_DIC[self.glade.get_widget("cmbEstilo").get_active()]
            # Obtenemos la accion
            accion = 1
            if self.glade.get_widget("rbFondo").get_active():
                accion = 2
            # Lo escribimos en el archivo de configuración
            try:
                confhandler.escribir_configuracion(wallpapers, tiempo, aleatorio, estilo, accion)
            except confhandler.ConfigError:
                confhandler.crear_configuracion(wallpapers, tiempo, aleatorio, estilo, accion)
            # Destruimos el dialogo
            self.window.destroy()
            # Y devolvemos la configuracion
            return (wallpapers, tiempo, aleatorio, estilo, accion)
        else:
            # Destruimos el dialogo
            self.window.destroy()
            # Y devolvemos None
            return None


class MyAboutDialog(gtk.AboutDialog):
    def __init__(self):
        super(MyAboutDialog, self).__init__()

        self.set_name("pyWallChanger")
        self.set_comments("¡Cambia tu fondo de pantalla de manera automática!")
        self.set_version("0.4")
        self.set_copyright("Copyright © 2009 Manuel Soler Moreno")
        self.set_license(file(os.path.join(PATH, "LICENSE"), "r").read())
        self.set_authors([file(os.path.join(PATH, "AUTHORS"), "r").read()])
        self.set_artists(["Icons by the Tango Desktop Project"])
        self.set_logo(gtk.gdk.pixbuf_new_from_file(os.path.join(PIX_PATH, "pywallchanger.svg")))
        self.set_modal(True)
        self.show_all()
        self.run()
        self.destroy()

