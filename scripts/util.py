from config import *
from log import logError, logSim

# Abre arquivo de configuração a partir de
# um diretorio do tipo teste
def openConfigFile(testDir):

    configFile = testDir+CONFIG_FILE

    os.path.abspath(configFile)

    # caminho do arquivo de configuracao
    pwd = os.path.dirname(configFile)+"/"

    # file
    f = ""

    # Verificando se é diretorio
    if not os.path.exists(configFile):
        logError("Favor passar como parametro um diretorio do tipo test")
        return(None)

    # verifica se exist arquivo de config
    try:
        f = open(configFile, 'r')
        return(f)
    except:
        logError("Arquivo config.txt não encontrado")
        return(False)

def parseConfigFile(testDir, nasmFile=None ):
    f = openConfigFile(testDir)

    dict = {'name': '', 'tipe': ''}

    if f is not False:
        for l in f:
            if len(l.strip()):
                if l.strip()[0]!='#':
                    if (l.strip().find('.nasm') > 0) or (l.strip().find('.vm') > 0):
                        par   = l.rstrip().split()
                        if(l.strip().find('.vm')):
                            name = par[0][:-3]
                        else:
                            name = par[0][:-5]
                        nTest = int(par[1])

                        # verifica se é para executar compilar
                        # apenas um arquivo da lista
                        if nasmFile is not None:
                            if name != nasmFile:
                                continue

                           
def rmFile(f):
    try:
        os.remove(f)
    except OSError:
        pass
