from cryptography.fernet import Fernet
import warnings
import json
import os
import traceback
import sys
from getpass import getpass, getuser
from src.pygem.data_compare.common.common_functions import encrypt

def getData(c):
    try:
        print('Enter params for Comparison #'+c)
        comparison = {}
        #change params
        comparison['execute'] = input('execute: ')  
        comparison['primary_keys'] = input('primary_keys: ').split()  
        comparison['tolerance'] = input('tolerance: ') 
        comparison['comp_type'] = 'python'
        comparison['srcDatabase'] = input('srcDatabase: ') 
        comparison['srcSchema'] = input('srcSchema: ') 
        comparison['srcTable'] = input('srcTable: ') 
        comparison['src_query_path'] = input('src_query_path: ') 
        comparison['tgtDatabase'] = input('tgtDatabase: ') 
        comparison['tgtSchema'] = input('tgtSchema: ') 
        comparison['tgtTable'] = input('tgtTable: ')
        comparison['tgt_query_path'] = input('tgt_query_path: ')
    except Exception:
        print("Exception in getData {}".format(traceback.format_exc()))
    return comparison

def createTest():
    try:
        projectName = input("Enter Project Name: ")
        filePath = input("Enter Path: ")
        n = int(input("Number of comparisons to be performed: "))
        comparisons = {}
        for i in range(n):
            comparisons[str(i+1)] = getData(str(i+1))
        path = os.path.join(filePath, projectName+"_test.json")
        outFile = open(os.path.abspath(path), "w")
        compare = {}
        compare["comparisons"] = comparisons
        json.dump(compare, outFile, indent=4)
        outFile.close()
        print('------'+projectName+'_test.json created at '+filePath+'------')
    except Exception:
        print("Exception in createTest {}".format(traceback.format_exc()))

def createSuite():
    try:
        projectName = input("Enter Project Name: ")
        filePath = input("Enter Path: ")
        report_email = {}
        report_email['to'] = input('to: ') 
        report_email['cc'] = input('cc: ') 
        report_email['bcc'] = input('bcc: ') 
        report_email['subject'] = input('subject: ') 
        report_email['title'] = input('title: ') 
        path = os.path.join(filePath, projectName+"_suite.json")
        outFile = open(os.path.abspath(path), "w")
        report = {}
        report["report_email"] = report_email
        json.dump(report, outFile, indent=4)
        outFile.close()
        print('------'+projectName+'_suite.json created at '+filePath+'------')
    except Exception:
        print("Exception in createSuite {}".format(traceback.format_exc()))

"""def createDB():
    try:
        projectName = input("Enter Project Name: ")
        filePath = input("Enter Path: ")
        path = os.path.join(filePath, projectName+"_db.json")
        outFile = open(os.path.abspath(path), "w")
        connection = {}
        json.dump(connection, outFile, indent=4)
        outFile.close()
        print(projectName+'_db.json created at '+filePath)
    except Exception:
        print("Exception in createDB {}".format(traceback.format_exc()))"""

def insertConnection():
    try:
        path = input("Enter db.json Path: ")
        outFile = os.path.abspath(os.path.join(path))
        db = open(outFile, "r").read()
        connection = json.loads(db)
        connectionName = input("Enter Connection Name: ")
        while(connectionName in connection):
            connectionName = input("Connection already exists. Enter new Connection Name: ")
        newConnection = {}
        dbs = ['mysql', 'oracle', 'postgre', 'sqlite']
        dbType = int(input('Choose:\n1.MySQL\n2.Oracle\n3.PostgreSQL\n4.Sqlite\nResponse: '))
        newConnection['type'] = dbs[dbType-1] 
        if(newConnection['type']=='sqlite'):
            newConnection['location'] = input('location: ') 
        else:
            newConnection['database'] = input('database: ')
            newConnection['user'] = input('user: ')
            #encryption
            passwd = getpass('password: ')
            newConnection['password'] = encrypt(passwd).decode("utf-8")
            newConnection['host'] = input('host: ')
            newConnection['port'] = input('port: ')
        connection[connectionName]=newConnection
        outFile = open(path, "w")
        json.dump(connection, outFile, indent=4)
        outFile.close()
        print('------Inserted Connection '+connectionName+'------')
    except Exception:
        print("Exception in insertConnection {}".format(traceback.format_exc()))

def ret(str1, dict1, field):
        if(str1!=''):
            return str1
        return dict1[field]

def updateConnection():
    try:
        path = input("Enter db.json Path: ")
        outFile = os.path.abspath(os.path.join(path))
        db = open(outFile, "r").read()
        connection = json.loads(db)
        connectionName = input("Enter Connection Name: ")
        while(connectionName not in connection):
            connectionName = input("Connection doesn't exist. Enter valid Connection Name: ")
        dict1 = connection[connectionName]
        """response = int(input("Change db type?\n1.Yes\n2.No\nResponse: "))
        if(response==1):
            dbs = ['mysql', 'oracle', 'postgre', 'sqlite']
            dbType = int(input('Choose:\n1.MySQL\n2.Oracle\n3.PostgreSQL\n4.Sqlite\nResponse: '))
            dict1['type'] = dbs[dbType-1]"""
        if(dict1['type']=='sqlite'):
            dict1['location'] = ret(input('location: '), dict1, 'location')
        else:
            dict1['database'] = ret(input('database: '), dict1, 'database')
            dict1['user'] = ret(input('user: '), dict1, 'user')
            #encryption
            passwd = getpass('password: ')
            dict1['password'] = ret(encrypt(passwd).decode("utf-8"), dict1, 'password')
            dict1['host'] = ret(input('host: '), dict1, 'host')
            dict1['port'] = ret(input('port: '), dict1, 'port')
        connection[connectionName]=dict1
        outFile = open(path, "w")
        json.dump(connection, outFile, indent=4)
        outFile.close()
        print('------Updated Connection '+connectionName+'------')
    except Exception:
        print("Exception in updateConnection {}".format(traceback.format_exc()))

def deleteConnection():
    try:
        path = input("Enter db.json Path: ")
        outFile = os.path.abspath(os.path.join(path))
        db = open(outFile, "r").read()
        connection = json.loads(db)
        connectionName = input("Enter Connection Name: ")
        while(connectionName not in connection):
            connectionName = input("Connection doesn't exist. Enter valid Connection Name: ")
        del connection[connectionName]
        outFile = open(path, "w")
        json.dump(connection, outFile, indent=4)
        outFile.close()
        print('------Deleted Connection '+connectionName+'------')
    except Exception:
        print("Exception in deleteConnection {}".format(traceback.format_exc()))
      
if __name__ == "__main__":
    response = int(input("Choose:\n1.Create suite.json\n2.Create test.json\n3.Insert Connection\n4.Update Connection\n5.Delete Connection\n6.Exit\nResponse: "))
    while(response!=6):
        if(response==1):
            createSuite()
        elif(response==2):
            createTest()
        elif(response==3):
            insertConnection()
        elif(response==4):
            updateConnection()
        elif(response==5):
            deleteConnection()
        elif(response==6):
            break
        else:
            print('Invalid response!')
        response = int(input("Choose:\n1.Create suite.json\n2.Create test.json\n3.Insert Connection\n4.Update Connection\n5.Delete Connection\n6.Exit\nResponse: "))

        
