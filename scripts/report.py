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
from pprint import pprint
from firebase import firebase
import json

TOOLSPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class report(object):
    def __init__(self,logFile, proj):
        self.proj = proj
        self.logFile = logFile
        self.idFile = os.path.join(TOOLSPATH,"user.txt")
        self.userId = self.userID()
        self.connection = self.openFirebase()
        self.testData = []

    def openFirebase(self):
        #connection = firebase.FirebaseApplication('https://elementos-10281.firebaseio.com/', None)
        #auth = firebase.FirebaseAuthentication('Elementos2018', 'elementosdesistemas@gmail.com', extra={'id': '123'})
        #connection.authentication = auth
        #print(auth.extra)

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
        return("GrupoA")

    def hw(self):
        tree = ET.parse(self.logFile)
        root = tree.getroot()
        ts = time.time()
        i = 0

        for n in root.iter('testcase'):
            testName = n.attrib['classname']
            runtime = n.attrib['time']

            p = n.find('failure')
            if p is None:
                status = 'Ok'
            else:
                status = 'Failure'

            p = n.find('system-out')
            log = p.text
            testName = testName[7:]
            self.testData.append({'name': testName, 'ts': str(int(ts)), 'status':status})

    def send(self):
        for n in self.testData:
            url = '/'+self.userId+'/'+self.proj+'/'+n['name']+'/'+n['ts']
            result = self.connection.put(url, name='status', data=n['status'], params={'print': 'pretty'})
            #print(result)

