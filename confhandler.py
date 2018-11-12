# coding: UTF-8

'''
Gestiona el archivo de configuración de pywallchanger
'''

import os
import string
import ConfigParser

# Localización de la carpeta con la configuración del monitor para el usuario
DIR_CONF_PATH = os.path.join(os.environ["HOME"],".pywallchanger")
# Localización del archivo de configuración del usuario
CONF_PATH = os.path.join(DIR_CONF_PATH,"pywallchanger.conf")


class ConfigError(Exception):
    '''
    Excepción lanzada cuando existen errores al leer/escribir en el archivo
        de configuración.
    '''
    def __init__(self, value):
        '''
        Instanciador de la clase.
        '''
        self.value = value
        Exception.__init__(self, value)


def crear_configuracion(wallpapers="", tiempo="30", aleatorio=False, estilo="stretched", accion=1):
    '''
    Crea un nuevo archivo de configuración con valores por defecto o bien
        con lo valores especificados.
    También crea la  carpeta de configuración del proyecto en la home
        del usuario en caso de no existir.
    '''
    if not os.path.lexists(DIR_CONF_PATH):
        os.mkdir(DIR_CONF_PATH)  # Creamos la carpeta .wallchanger en la home del usuario si no esta creada

    conf = ConfigParser.ConfigParser()
    # En primer lugar se crean las distintas secciones
    conf.add_section("config")
    # Ahora creamos las opciones y le añadimos sus valores
    wall = ""
    if wallpapers:
        wall = string.join(wallpapers, ";")
    conf.set("config", "wallpapers", wall)
    conf.set("config", "tiempo", tiempo)
    conf.set("config", "aleatorio", str(aleatorio))
    conf.set("config", "estilo", estilo)
    conf.set("config", "accion", str(accion))
    # Finalmente creamos el archivo y escribimos la configuración.
    f = open(CONF_PATH, "w")
    conf.write(f)
    f.close()
    # Devolvemos las características aplicadas
    return (wallpapers, tiempo, aleatorio, estilo, accion)

def escribir_configuracion(wallpapers, tiempo, aleatorio, estilo, accion):
    '''
    Escribe en el archivo de configuración los nuevos valores establecidos.
        wallpapers: Una lista con la ruta de los wallpapers a cambiar.
        tiempo: Tiempo en minutos a los que ir cambiando los fondos.
        aleatorio: Booleano indicando si los salvapantallas deberían seguir un orden aleatorio.
        estilo: Estilo del fondo. centered, stretched, escaled, zoom, wallpaper.
        accion: Entero que indica 1 se muestran las preferencias o 2 pasa al siguiente wallpaper

    Lanza una excepción de tipo ConfigError	cuando no se encuentra el archivo
        de configuración o bien cuando este está mal formado.
        En cualquier caso la mejor solución sería volver a crearlo con
        los nuevos valores.
    '''
    conf = ConfigParser.ConfigParser()
    if not conf.read([CONF_PATH]):
        raise ConfigError("Archivo de configuración no encontrado.")
    try:	
        # Escribimos los wallpapers a monitorizar
        if wallpapers:
            conf.set("config", "wallpapers", string.join(wallpapers, ";"))
        else:		
            conf.set("config", "wallpapers", "")
        # Escribimos el tiempo
        conf.set("config", "tiempo", tiempo)
        # Escribimos el aleatorio
        conf.set("config", "aleatorio", str(aleatorio))
        # Escribimos el estilo
        conf.set("config", "estilo", estilo)
        # Escribimos la accion
        conf.set("config", "accion", str(accion))
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        raise ConfigError("Archivo de configuración mal formado.")
    else:
        f = open(CONF_PATH, "w")
        conf.write(f)
        f.close()

def leer_configuracion():
    '''
    Lee el archivo de configuración del usuario y devuelve una lista con
        *)Una lista con los wallpapers a cambiar.
        *)Tiempo de cambio entre wallpapers en minutos
        *)aleatorio: Booleano indicando si los salvapantallas deberían seguir un orden aleatorio.
        *)estilo: Estilo del fondo. centered, stretched, escaled, zoom, wallpaper.
        *)accion: Entero que indica 1 se muestran las preferencias o 2 pasa al siguiente wallpaper
    Lanza una excepción ConfigError si el archivo no se encuentra.
    '''
    conf = ConfigParser.ConfigParser()
    try:
        if not conf.read([CONF_PATH]):
            raise ConfigError("Archivo de configuración no encontrado.")
    except ConfigParser.MissingSectionHeaderError:
        raise ConfigError("Archivo de configuración mal formado.")

    try:
        # Obtenemos los wallpapers
        wallpapers = conf.get("config", "wallpapers").split(";")
        # Obtenemos el tiempo
        tiempo = conf.get("config", "tiempo")
        # Obtenemos aleatorio
        aleatorio = True
        if conf.get("config", "aleatorio") == "False":
            aleatorio = False
        # Obtenemos el estilo
        estilo = conf.get("config", "estilo")
        # Obtenemos la acción
        accion = int(conf.get("config", "accion"))
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        raise ConfigError("Archivo de configuración mal formado.")
    else:
        return (wallpapers, tiempo, aleatorio, estilo, accion)
