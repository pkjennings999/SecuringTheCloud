from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive as PyDriveGoogleDrive
#from tkinter import Tk
#from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfile
#from threadsafe_tkinter import *
from easygui import fileopenbox
from easygui import filesavebox
import ntpath
from Crypto.Cipher import AES
from app.models import Group
import os

class GoogleDrive():
    gauth = None
    drive = None

    def __init__(self):
        self.gauth = GoogleAuth()
        self.gauth.LoadCredentialsFile("mycreds.txt")
        if self.gauth.credentials is None:
            # Authenticate if they're not there
            self.gauth.LocalWebserverAuth()
        elif self.gauth.access_token_expired:
            # Refresh them if expired
            self.gauth.Refresh()
        else:
            # Initialize the saved creds
            self.gauth.Authorize()
        # Save the current credentials to a file
        self.gauth.SaveCredentialsFile("mycreds.txt")

        self.drive = PyDriveGoogleDrive(self.gauth)

    def getFiles(self):
        return self.drive.ListFile({'q': "'1a_ZOqi75h6nTvsUEPDi8NGUrb9Tk-dkh' in parents and trashed=false"}).GetList()

    def getFilesInFolder(self, folder):
        return self.drive.ListFile({'q': "'" + folder + "' in parents and trashed=false"}).GetList()

    def uploadFile(self, folder, groupId):
        #Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
        filepath = fileopenbox() # show an "Open" dialog box and return the path to the selected file
        file = self.drive.CreateFile({'title': ntpath.basename(filepath), 'parents': [{'kind': 'drive#fileLink', 'id': folder}]})
        f = open(filepath, 'rb')
        self.encrypt(groupId, f.read())
        file.SetContentFile('encrypted.bin')
        file.Upload()
        #if os.path.exists('encrypted.bin'):
        #    os.remove('encrypted.bin')

    def downloadFile(self, id, title, groupId):
        file = self.drive.CreateFile({'id': id})
        file.GetContentFile('title')
        file.GetContentFile('encrypted.bin')
        #Tk().withdraw()
        destination = filesavebox()
        if destination is None:
            return
        self.decrypt(groupId, destination)
        #file.GetContentFile(destination)

    def createGroup(self, title):
        folder = self.drive.CreateFile({'title': title, 'mimeType' : 'application/vnd.google-apps.folder', 'parents': [{'kind': 'drive#fileLink', 'id': '1a_ZOqi75h6nTvsUEPDi8NGUrb9Tk-dkh'}]})
        folder.Upload()
        return folder['id']

    def encrypt(self, groupId, data):
        key = Group.objects.get(id=groupId).key
        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        file_out = open("encrypted.bin", "wb")
        [ file_out.write(x) for x in (cipher.nonce, tag, ciphertext) ]

    def decrypt(self, groupId, destination):
        key = Group.objects.get(id=groupId).key
        file_in = open("encrypted.bin", "rb")
        nonce, tag, ciphertext = [ file_in.read(x) for x in (16, 16, -1) ]
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)
        typeofdata = type(data)
        file_out = open(destination, "wb")
        file_out.write(data)

    def fucksake(self):
        with open('E:\\TEST1.PNG', 'rb') as f1: 
            with open('E:\\uggggggh.png', 'wb') as f2:
                f2.write(f1.read())