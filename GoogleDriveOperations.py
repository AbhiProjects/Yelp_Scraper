from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

def createAuthorizer():
	try:
		gauth = GoogleAuth()
		
		# Authentication Method For Server
		gauth.LoadCredentialsFile("mycreds.txt")
		if gauth.credentials is None:
		# Authenticate if they're not there
			gauth.LocalWebserverAuth()
		elif gauth.access_token_expired:
		# Refresh them if expired
			gauth.Refresh()
		else:
		# Initialize the saved creds
			gauth.Authorize()
		# Save the current credentials to a file
		gauth.SaveCredentialsFile("mycreds.txt")
		
		# Use This When Running Locally
		#gauth.LocalWebserverAuth()
		
		drive = GoogleDrive(gauth)
	except Exception, e:
		print 'Exception In Google Drive Authorization Process'
		print str(e)
	else:
		return drive

def createGoogleDriveFolder(drive,FolderID,FolderName):
	try:
		folder = drive.CreateFile({'parents':[{'isRoot': False,'id': FolderID}],'title': FolderName,'mimeType': 'application/vnd.google-apps.folder'})
		folder.Upload()
	except Exception, e:
		print 'Exception In Creation Of Google Drive Folder Generation Operation For Folder Name',FolderName
		print str(e)
	else:
		return folder['id']
		
def getFolderList(drive,FolderID ='root'):
	try:
		Data = []
		fileList = drive.ListFile({'q': "'%s' in parents and trashed=false" %(FolderID)}).GetList()
	
		for file in fileList:
			if file['mimeType'] == 'application/vnd.google-apps.folder':
				Data.append((file['title'],file['id']))
	except Exception, e:
		print 'Exception In Google Drive Folder List Generation Operation For Folder Id',FolderID
		print str(e)
	else:	
		return Data
		
def folderCheck(drive,SubFolder,Parent ='root'):
	try:
		ID = None
		Data = getFolderList(drive,Parent)
		if Data == None:
			return None

		for fileTupple in Data:
			if fileTupple[0] == SubFolder:
				ID = fileTupple[1]
				break
		else:
			ID = None
			
	except Exception, e:
		print 'Exception In Google Drive Check Folder Operation For',Parent,'And Child',SubFolder
		print str(e)
	else:
		return ID
	
def fileUpload(drive,FolderID,jsonFile):
	try:
		file = drive.CreateFile({'parents':[{'isRoot': False,'id': FolderID}]})
		file.SetContentFile(jsonFile) 
		file.Upload() 
	except Exception, e:
		print 'Exception In Google Drive File Upload Operation File',jsonFile
		print str(e)
	else:	
		FolderName = drive.ListFile({'q': "'%s' in parents and trashed=false" %(FolderID)}).GetList()[0]['title']
		print 'File Uploaded Successfully In The Folder',FolderName
		return file['id']
		
def googleDriveUpload(drive,Yelp_FolderID,City,jsonFile):
	try:
		FolderID = folderCheck(drive,City,Yelp_FolderID)
		if FolderID == None:
			FolderID = createGoogleDriveFolder(drive,Yelp_FolderID,City)
		fileUpload(drive,FolderID,jsonFile)
	except Exception as e:
		print 'File Upload Failure For File',jsonFile
		print str(e)
	else:
		return True
