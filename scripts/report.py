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
import subprocess
import firebase_admin
from firebase_admin import credentials, db

TOOLSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

LOG_DB_PASS = 'PASS'
LOG_DB_FAIL = 'FAIL'

class report(object):
    def __init__(self, logFile, proj, ProjType):
        self.proj = proj
        self.logFile = logFile
        self.ts = int(time.time())
        self.Travis = self.getTravis()
        self.groupId = self.getGrupId(os.path.abspath(TOOLSPATH+"/../../GRUPO.json"))
        self.userName = self.getUserGit()
        self.branchName = self.getBranchGit()
        self.openFirebase()
        self.testData = []
        self.error = None
        if ProjType is 'HW':
            self.error = self.hw()
        if ProjType is 'NASM':
            self.error = self.nasm()

    def openFirebase(self):
        firebase_admin.initialize_app(None, { 'databaseURL': 'https://elementos-10281.firebaseio.com/'})

    def getGrupId(self, idFile):
        try:
            with open(idFile) as f:
                data = json.load(f)
                return(data['Nome-Grupo'].lstrip()[0])
        except:
            print("  ******************************************")
            print("  * [ERROR] Corrija o arquivo GRUPO.json!  *")
            print("  ******************************************")
            return('Erro')

    def getUserGit(self):
        try:
            return(subprocess.Popen( ['git', 'config', 'user.name'],   stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
        except:
            return('ERRO')

    def getBranchGit(self):
        try:
            return(subprocess.Popen( ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],   stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
        except:
            return('ERRO')

    def getTravis(self):
        if os.environ.get('TRAVIS'):
            travis = True
        else:
            travis = False
        return(travis)

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
            self.testData.append({'name': testName, 'ts': str(self.ts), 'status':status})
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
            self.testData.append({'name': s[2], 'ts': str(self.ts), 'status': s[0] })
            if s[0] == LOG_DB_FAIL:
                cnt = cnt + 1
        return(cnt)

    def send(self):
        try:
            for n in self.testData:
                url = '/'+self.groupId+'/'+self.proj+'/'+n['name']+'/'+n['ts']
                db.reference(url).set({'status': n['status'], 'name':self.userName, 'branch':self.branchName, 'Travis':str(self.Travis)})
                print('.. .', end='', flush=True)
            print('')
        except:
           print('[log] Sem conexão com a internet')
