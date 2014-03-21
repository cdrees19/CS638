#!/usr/bin/python

import sys
sys.path.insert(0,'/home/patrick/AUDL_server')

import os
os.chdir('../')
import AUDLclasses

def server_start__test():

    try:
        execfile('server.py')
    except:
        print "Could not start the server successfully"
        
