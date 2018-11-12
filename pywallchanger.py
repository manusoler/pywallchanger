#!/usr/bin/env python
# coding: UTF-8

'''Cambia el fondo de pantalla cada cierto tiempo,
por defecto cada 30 minutos.'''

import gtk
import pygtk

import confhandler
import interfaz

def main():
    '''
    Funcion que inicia la ejecución de pywallchanger
    '''
    try:
        pywallchanger = interfaz.Interfaz()
        gtk.gdk.threads_init()
        gtk.main()
    except KeyboardInterrupt:
        pass
    

if __name__ == "__main__":
    main()

