# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 09:28:26 2017

@author: Jordan
Simple file upload to Drive. Includes logic to authenticate in browser once, but streamline process for future sessions
Uses PyDrive library
https://pypi.python.org/pypi/PyDrive
"""


#%% Setup

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
gauth = GoogleAuth()
#gauth.LocalWebserverAuth()
gauth.LoadCredentialsFile('mycreds.txt')
if gauth.credentials is None:
	gauth.LocalWebserverAuth() # Auth if no credentials
	gauth.SaveCredentialsFile('mycreds.txt')
elif gauth.access_token_expired:
	gauth.Refresh() # Refresh otherwise
else:
	gauth.Authorize() # Initialize

drive = GoogleDrive(gauth)

#%% Main
file1 = drive.CreateFile({'title': 'Hello.txt'})
file1.SetContentString('Hello')
file1.Upload() # Files.insert()

file1['title'] = 'HelloWorld.txt'  # Change title of the file
file1.Upload() # Files.patch()

content = file1.GetContentString()  # 'Hello'
file1.SetContentString(content+' World!')  # 'Hello World!'
file1.Upload() # Files.update()

file2 = drive.CreateFile()
file2.SetContentFile('dino.jpg')
file2.Upload()
print('Created file %s with mimeType %s' % (file2['title'],
file2['mimeType']))
# Created file hello.png with mimeType image/png

