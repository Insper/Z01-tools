#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Rafael Corsi @ insper.edu.br
# Agosto @ 2018
# Disciplina Elementos de Sistemas
#
# Envia relatório do teste realizado.

import string
import random
import os.path
import xml.etree.ElementTree as ET
import time
from firebase import firebase
import json
import os
from joblib import Parallel, delayed

TOOLSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class report(object):
    def __init__(self, logFile, proj, ProjType):
        self.proj = proj
        self.logFile = logFile
        self.idFile = os.path.join(TOOLSPATH,"user.txt")
        self.userId = self.userID()
        self.connection = self.openFirebase()
        self.testData = []
        self.Travis = False
        if os.environ.get('Travis') is not None:
            self.Travis = True

        self.error = None
        if ProjType is 'HW':
            self.error = self.hw()

    def openFirebase(self):
#        authentication = firebase.FirebaseAuthentication('InsperComp', 'elementosdesistemas@gmail.com', extra={'id': 0})
        connection = firebase.FirebaseApplication('https://elementos-10281.firebaseio.com/', authentication=None)
        return(connection)

    def userID(self):
        #if os.path.isfile(self.idFile):
        #    f = open(self.idFile,"r+")
        #    userid = f.readline()
        #else:
        #    f = open(self.idFile,"w+")
        #    userid = id_generator(size=18)
        #    f.write(userid)
        #    print("----")
        #f.close()
        return("Professor")

    def hwModuleFail(self):
        failModules = []
        for n in self.testData:
            if n['status'] is 'Failure':
                failModules.append(n['name'])
        return(failModules)

    def hw(self):
        try:
            tree = ET.parse(self.logFile)
        except IOError:
            return(-1)
        root = tree.getroot()
        ts = int(time.time())
        error = 0

        for n in root.iter('testcase'):
            testName = n.attrib['classname']
            runtime = n.attrib['time']

            p = n.find('failure')
            if p is None:
                status = 'Ok'
            else:
                status = 'Failure'
                error = error + 1

            p = n.find('system-out')
            log = p.text
            testName = testName[7:]
            self.testData.append({'name': testName, 'ts': str(ts), 'status':status})
        return(error)

    def assemblyTeste(self, logFile):
        ts = int(time.time())
        if type(logFile) is dict:
            self.testData.append({'name': logFile['name'], 'ts': str(ts), 'status': logFile['status'] })
        else:
            for log in logFile:
                self.testData.append({'name': log['name'], 'ts': str(ts), 'status': log['status'] })

    def assembler(self, logFile):
        cnt = 0
        ts = int(time.time())
        try:
            f = open(logFile, 'r')
        except IOError:
            return(1)
        for line in f:
            s = line.split()
            print(line[:-1])
            self.testData.append({'name': s[2], 'ts': str(ts), 'status': s[0] })
            if s[0] == 'FAIL':
                cnt = cnt + 1
        return(cnt)

    def singleSend(self, n):
 #       n = self.testData[i]
        if self.Travis:
            url = '/'+self.userId+'/'+'Travis/'+self.proj+'/'+n['name']+'/'+n['ts']
        else:
            url = '/'+self.userId+'/'+self.proj+'/'+n['name']+'/'+n['ts']
            self.connection
        result = self.connection.put(url, name='status', data=n['status'], params={'print': 'pretty'})
        print('.. .', end='', flush=True)

    def parSend(self):
        Parallel(n_jobs=4)(delayed(self.singleSend)(n) for n in self.testData)

    def send(self):
        for n in self.testData:
            if self.Travis:
                url = '/'+self.userId+'/'+'Travis/'+self.proj+'/'+n['name']+'/'+n['ts']
            else:
                url = '/'+self.userId+'/'+self.proj+'/'+n['name']+'/'+n['ts']
                self.connection
            result = self.connection.put(url, name='status', data=n['status'], params={'print': 'pretty'})
            print('.. .', end='', flush=True)
        print('')

