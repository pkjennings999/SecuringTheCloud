from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive as PyDriveGoogleDrive
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfile
import ntpath

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

    def uploadFile(self):
        Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
        filepath = askopenfilename() # show an "Open" dialog box and return the path to the selected file
        file = self.drive.CreateFile({'title': ntpath.basename(filepath), 'parents': [{'kind': 'drive#fileLink', 'id': '1a_ZOqi75h6nTvsUEPDi8NGUrb9Tk-dkh'}]})
        file.SetContentFile(filepath)
        file.Upload()

    def downloadFile(self, id, title):
        file = self.drive.CreateFile({'id': id})
        file.GetContentFile('title')
        Tk().withdraw()
        destination = asksaveasfile()
        if destination is None:
            return
        file.GetContentFile(destination.name)
        destination.close()

    def createGroup(self, title):
        folder = self.drive.CreateFile({'title': title, 'mimeType' : 'application/vnd.google-apps.folder', 'parents': [{'kind': 'drive#fileLink', 'id': '1a_ZOqi75h6nTvsUEPDi8NGUrb9Tk-dkh'}]})
        folder.Upload()
        return folder['id']