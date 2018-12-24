# Rafael Corsi @ insper.edu.br
# Dez/2017
# Disciplina Elementos de Sistemas

import sys, os, shutil, subprocess

if not os.environ.get('TRAVIS'):
    # import GdkPixbuf module
    import gi
    gi.require_version("Notify", "0.7")
    from gi.repository import Notify, GdkPixbuf

ROOT_PATH = subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')
sys.path.insert(0, ROOT_PATH + '/Projetos/Z01-tools/scripts/')

from config import *

imagePath = TOOL_SCRIPT_PATH + '/data/'

class notificacao(object):
    def __init__(self, msg):
        # Use GdkPixbuf to create the proper image type
        self.imageError = imagePath + 'process-stop.svg'
        self.imageOk = imagePath + 'process-completed.svg'
        self.imageAlert = imagePath + 'dialog-warning.svg'

        self.notification = ''
        self.image = ''
        self.msg = '<b>'+msg+'</b>'

    def do(self, icon, msg):
        if not os.environ.get('TRAVIS'):
            Notify.init("Z01.1")
            self.notification = Notify.Notification.new(msg)

            self.image = GdkPixbuf.Pixbuf.new_from_file(icon)
            self.notification.set_icon_from_pixbuf(self.image)
            self.notification.set_image_from_pixbuf(self.image)
            self.notification.show()

    def error(self, msg=None):
        if msg is None:
            cmsg = self.msg
        else:
            cmsg = self.msg + msg
        self.do(self.imageError, cmsg)

    def ok(self, msg=None):
        if msg is None:
            cmsg = self.msg
        else:
            cmsg = self.msg + msg
        self.do(self.imageOk, cmsg)

    def alert(self, msg=None):
        if msg is None:
            cmsg = self.msg
        else:
            cmsg = self.msg + msg
        self.do(self.imageAlert, cmsg)

    def hw(self, report):
        if report.error:
            failModules = report.hwModuleFail()
            s = '\n Falhou ' + failModules[0]
            if(report.error > 1):
                    s += ' e mais ' + str(report.error-1) +' modulo(s)'
            else:
                    s += ' e só'
            self.error(s)
        else:
            self.ok()


if __name__ == "__main__":
    n = notificacao()
    n.alert('Teste ok')
