from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive as PyDriveGoogleDrive
from easygui import fileopenbox
from easygui import filesavebox
import ntpath
from Crypto.Cipher import AES
from app.models import Group

class GoogleDrive():
    gauth = None
    drive = None

    def __init__(self):
        self.gauth = GoogleAuth()
        # I didn't want to promt the user for permission every time the 
        # program was run. I felt that once was enough. Therefore, I save the 
        # generated credentials to a text file. If there are credentials there,
        # I use them. Otherwise the user is prompted for permission
        self.gauth.LoadCredentialsFile("mycreds.txt")
        if self.gauth.credentials is None:
            # Authenticate if credentials not there
            self.gauth.LocalWebserverAuth()
        elif self.gauth.access_token_expired:
            # Refresh credentials if expired
            self.gauth.Refresh()
        else:
            # Initialize the saved credentials
            self.gauth.Authorize()
        # Save the current credentials to a file
        self.gauth.SaveCredentialsFile("mycreds.txt")

        self.drive = PyDriveGoogleDrive(self.gauth)

    # Returns all the files in the default folder of the program on the drive
    def getFiles(self):
        return self.drive.ListFile({'q': "'1a_ZOqi75h6nTvsUEPDi8NGUrb9Tk-dkh' in parents and trashed=false"}).GetList()

    # Returns all the files in a given folder in the drive
    def getFilesInFolder(self, folder):
        return self.drive.ListFile({'q': "'" + folder + "' in parents and trashed=false"}).GetList()

    # Upload a given file to a given folder in the drive
    def uploadFile(self, folder, groupId):
        # Show an "Open" dialog box and return the path to the selected file
        filepath = fileopenbox() 
        # If the dialog is closed without selecting a location, do nothing
        if filepath is None:
            return
        # Initialise a google drive file
        file = self.drive.CreateFile({'title': ntpath.basename(filepath), 'parents': [{'kind': 'drive#fileLink', 'id': folder}]})
        # Open a folder, and prepare to write bytes to it. The encryption method requires the data to be represented as bytes
        f = open(filepath, 'rb')
        # Encrypt the data
        self.encrypt(groupId, f.read())
        # Set the content of the google drive file to be the encrypted data and upload
        file.SetContentFile('encrypted.bin')
        file.Upload()

    # Download a given file from a given folder in the drive 
    def downloadFile(self, id, title, groupId):
        # Initialise a google drive file, using the file in the drive as given by the id
        file = self.drive.CreateFile({'id': id})
        # Save the file to a binary file
        file.GetContentFile('encrypted.bin')
        # Show a "Save as" dialog box and return the path
        destination = filesavebox()
        # If the dialog is closed without selecting a location, do nothing
        if destination is None:
            return
        # Decrypt the file and store it in the given destination
        self.decrypt(groupId, destination)

    # Delete a given file from the drive
    def deleteFile(self, id):
        file = self.drive.CreateFile({'id': id})
        file.Trash()

    # Create a group folder in the drive
    def createGroup(self, title):
        # Initialise a google drive file in the root folder for the application, and given it a given name
        folder = self.drive.CreateFile({'title': title, 'mimeType' : 'application/vnd.google-apps.folder', 'parents': [{'kind': 'drive#fileLink', 'id': '1a_ZOqi75h6nTvsUEPDi8NGUrb9Tk-dkh'}]})
        # Upload the file and return it's id to be stored in the respective group model instance
        folder.Upload()
        return folder['id']

    # Encrypt a given file
    def encrypt(self, groupId, data):
        # Pull the key from the group
        key = Group.objects.get(id=groupId).key
        # Create a cipher
        cipher = AES.new(key, AES.MODE_EAX)
        # Encrypt the file
        ciphertext, tag = cipher.encrypt_and_digest(data)
        # Open a file, and prepare the write bytes to it
        file_out = open("encrypted.bin", "wb")
        # Write the encrypted data to the file
        [ file_out.write(x) for x in (cipher.nonce, tag, ciphertext) ]

    # Decrypt a given file
    def decrypt(self, groupId, destination):
        # Pull the key from the group
        key = Group.objects.get(id=groupId).key
        # Load the encrypted data
        file_in = open("encrypted.bin", "rb")
        nonce, tag, ciphertext = [ file_in.read(x) for x in (16, 16, -1) ]
        # Create a cipher
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        # Decrypt the data
        data = cipher.decrypt_and_verify(ciphertext, tag)
        # Write the file to the given destination
        file_out = open(destination, "wb")
        file_out.write(data)