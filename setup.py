#!/usr/bin/env python
# coding: UTF-8

'''
Install or remove pyWallChanger from your system.
'''

import os
import os.path
import shutil
import optparse

# PATHS
EXEC_PATH = "/usr/bin"
PIX_PATH = "/usr/share/pixmaps"
DESK_PATH = "/usr/share/applications"
PATH = "/usr/share/pywallchanger"

# FILENAMES
EXEC = "pywallchanger"
FILES = ("confhandler.py", "interfaz.py", "pywallchanger.py", "pywallchanger.glade", "AUTHORS", "LICENSE")
PIXMAP = "pywallchanger.svg"
DESK = "pywallchanger.desktop"

def main():
    # Parse the arguments
    parser = optparse.OptionParser()
    parser.add_option("--install", action="store_true", dest="install", default="True", help="Install pyWallChanger on your system")
    parser.add_option("--remove", action="store_false", dest="install", help="Remove pyWallChanger from your system")
    options, arg = parser.parse_args()

    # Check if user is root
    if os.getuid():
        print "\nERROR: You must be root!\n"
        return 1

    # Install pyWallChanger
    # Creates the necesary dirs if don't exist and
    # copy all necesary content on them
    if options.install:
        print "Starting installation..."
        if not os.path.lexists(PATH):
            print "  * Creating folders..."
            os.mkdir(PATH, 0755)
        try:
            print "  * Copying files..."
            shutil.copy(EXEC, EXEC_PATH)
            os.chmod(os.path.join(EXEC_PATH, EXEC), 0755)
            for arch in FILES:
                shutil.copy(arch, PATH)
            shutil.copy(PIXMAP, PIX_PATH)
            shutil.copy(DESK, DESK_PATH)
        except IOError, e:
            print "Error during installation.\n  %s\n" % (e[1:])
        else:
            print "Success!!\nYou can now execute %s on a terminal or go to Aplications > Accesories > pyWallChanger on your Gnome menu." % EXEC
    # Remove pyWallChanger
    else:
        print "Uninstalling pyWallChanger..."
        try:
            if os.path.lexists(PATH):
                for arch in FILES:
                    os.remove(os.path.join(PATH, arch))
                os.rmdir(PATH)
            os.remove(os.path.join(EXEC_PATH, EXEC))
            os.remove(os.path.join(PIX_PATH, PIXMAP))
            os.remove(os.path.join(DESK_PATH, DESK))
        except OSError, e:
            print "Error during uninstallation.\n  %s" % (e[1:])
        else:
            print "\nUninstall finished\n"


if __name__=="__main__":
    main()
