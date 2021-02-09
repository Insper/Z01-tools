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
from pymongo import MongoClient
from datetime import datetime
from config import *

class report(object):
    def __init__(self, logFile, proj, ProjType):
        self.proj = proj
        self.logFile = logFile
        self.ts = int(time.time())
        self.Travis = CI_TRAVIS
        self.groupId = self.getGrupId(ROOT_PATH + '/GRUPO.json')
        self.userName = self.getUserGit()
        self.branchName = self.getBranchGit()
        self.db = None
        self.openMongo()
        self.testData = []
        self.error = 0
        if ProjType is 'HW':
            self.error = self.hw()
        elif ProjType is 'NASM':
            self.error = self.nasm()
        elif ProjType is 'JAVA':
            self.error = self.error

    def openMongo(self):
        mongo = MongoClient(host='35.173.122.31', username='myUserAdmin', password='L838gavGe5tuWPH', authSource='admin')
        self.db = mongo.elementos_test

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

    def nasm(self, nasm=None):
        if nasm != None:
            self.logFile = nasm
        ts = int(time.time())
        if type(self.logFile) is dict:
            self.testData.append({'name': self.logFile['name'], 'ts': str(ts), 'status': self.logFile['status'] })
        else:
            for log in self.logFile:
                self.testData.append({'name': log['name'], 'ts': str(ts), 'status': log['status'] })

    def java(self, logFile):

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
                self.error = self.error + 1

    def send(self):
        try:
            for n in self.testData:
                post_id = {'tag':SEMESTRE_ID, 'group':self.groupId, 'project': self.proj, 'test': n['name'], 'branch': self.branchName}
                ref = self.db.tests.find_one(post_id)
                if ref is None:
                    post_id['created'] = datetime.now()
                    post_id['runs'] = []
                    self.db.tests.insert(post_id)
                    ref = self.db.tests.find_one(post_id)
                import pdb; pdb.set_trace()
                ref['updated'] = datetime.now()
                ref['Travis'] = str(self.Travis)
                ref['status'] = n['status']
                ref['runs'].append({'status': n['status'], 'ts': n['ts']})
                self.db.tests.save(ref)
                print('.. .', end='', flush=True)
            print('')
        except Exception as e:
           print(e)
           print('[log] Sem conexão com a internet')
