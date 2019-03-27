#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Rafael Corsi @ insper.edu.br
# Agosto @ 2018
# Disciplina Elementos de Sistemas
#
# Envia relatório do teste realizado.

import sys
import os.path
import xml.etree.ElementTree as ET
import time
import json
import os
import firebase_admin
from firebase_admin import credentials, db

TOOLSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

LOG_DB_PASS = 'PASS'
LOG_DB_FAIL = 'FAIL'

class report(object):
    def __init__(self, logFile, proj, ProjType):

        self.Travis = False
        if os.environ.get('TRAVIS'):
            self.Travis = True
        else:
            self.Travis = False
        self.proj = proj
        self.logFile = logFile
        self.idFile = os.path.abspath(TOOLSPATH+"/../../GRUPO.json")
        self.userId = self.userID()
        self.openFirebase()
        self.testData = []
        self.error = None
        if ProjType is 'HW':
            self.error = self.hw()
        if ProjType is 'NASM':
            self.error = self.nasm()

    def openFirebase(self):
        firebase_admin.initialize_app(None, { 'databaseURL': 'https://elementos-10281.firebaseio.com/'})

    def userID(self):

        if self.Travis == True:
            return('Travis')
        try:
            if os.path.isfile(self.idFile):
                with open(self.idFile) as f:
                    data = json.load(f)
                    name = data['Nome-Grupo'].lstrip()[0]
                    return(name)
        except:
            print("  ******************************************")
            print("  * [ERROR] Corrija o arquivo GRUPO.json!  *")
            print("  ******************************************")
            return('Erro')

    def hwModuleFail(self):
        failModules = []
        for n in self.testData:
            if n['status'] is LOG_DB_FAIL:
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
                status = LOG_DB_PASS
            else:
                status = LOG_DB_FAIL
                error = error + 1

            p = n.find('system-out')
            log = p.text
            testName = testName[7:]
            self.testData.append({'name': testName, 'ts': str(ts), 'status':status})
        return(error)

    def nasm(self):
        ts = int(time.time())
        if type(self.logFile) is dict:
            self.testData.append({'name': self.logFile['name'], 'ts': str(ts), 'status': self.logFile['status'] })
        else:
            for log in self.logFile:
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
            if s[0] == LOG_DB_FAIL:
                cnt = cnt + 1
        return(cnt)

    def send(self):
        try:
            for n in self.testData:
                if self.Travis == False:
                    url = '/'+self.userId+'/'+self.proj+'/'+n['name']+'/'+n['ts']
                    db.reference(url).set({'status': n['status']})
                    print('.. .', end='', flush=True)
            print('')
        except:
            print('[log] Sem conexão com a internet')
