#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

import os,random
from bs4 import BeautifulSoup
from GoogleDriveOperations import *
import urllib2,urllib,socket
import html5lib,HTMLParser
import string,json,csv,time

ROOT_FOLDER = 'Yelp_Data'
BASE_FOLDER = 'Data'
BASE_URL = 'http://www.yelp.com/search?find_desc=%s&find_loc=%s&start=%s'
START_BASE_URL = 'http://www.yelp.com/search?find_desc=%s&find_loc=%s'

CSV_HEADER = ['City_Search','Cusine_Search','Name','Category','Rating','Reviews','Address','City','State','Zip','Phone']

def CreateFolder(FolderName):
	try:
		os.makedirs(os.path.join(BASE_FOLDER,FolderName))
		print 'Folder',FolderName,'Created'
		print
	except OSError:
		pass

def jsonRead(FileName):
	try:
		f=open(os.path.join(BASE_FOLDER,FileName)+'.json','r')
		Data=json.loads(f.read())
		f.close()
	except Exception as e:
		print 'JSON File Read Error.'
		print str(e)
	else:
		return Data
	return None	

def jsonWrite(FileName,Data,openType):
	try:
		f=open(os.path.join(BASE_FOLDER,FileName)+'.json',openType)
		json.dump(Data,f,indent=4,sort_keys=True)
		f.close()
	except Exception as e:
		print 'JSON File Write Error.'
		print str(e)
	else:
		return 'OK'
	return None
	
def csvWrite(FileName,Data,openType):
	try:
		f=open(os.path.join(BASE_FOLDER,FileName)+'.csv',openType)
		csvWriter = csv.writer(f)
		csvWriter.writerow( Data )
		f.close()
	except Exception as e:
		print 'CSV File Write Error.'
		print str(e)
	else:
		return 'OK'
	return None
	
def buildPageReterive(URL):
	try:
		User_Agent_List = [	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0',
							'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
							'​Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
							'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.112 Safari/535.1',
							'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3',
							'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0',
							'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; FSL 7.0.6.01001)',
							'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0',
							'Mozilla/5.0 (iPad; U; CPU OS 5_1 like Mac OS X) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B367 Safari/531.21.10 UCBrowser/3.4.3.532',
							'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
							'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36'
						  ]
		
		User_Agent = random.choice(User_Agent_List)
		Agent = {'User-Agent':User_Agent}
		PageRequest = urllib2.Request(URL,headers=Agent)
		PageResponse = urllib2.urlopen(PageRequest,timeout = 4)	
	except socket.timeout, e:
		print 'Internet Connection Lost'
	except urllib2.HTTPError as e:
		print 'The Server Couldn\'t Fulfill The Request.'
		print 'Error Code:', e.code
		print 'Error Message:',e.reason
	except urllib2.URLError as e:
		print 'We Failed To Reach A Server.'
		print 'Reason: ', e.reason
	except:
		print 'Error In Obtaining Data From',URL
	else:
		HTML = PageResponse.read()
		PageResponse.close()
		return HTML
	return None
	
def soupCreator(HTML,SoupElement,SoupFinder):
	try:
		soup = BeautifulSoup(HTML,'html5lib')
		Data = soup.find_all(SoupElement,{'class':SoupFinder})
	except:
		print "Error Occurred In Parsing Response"
	else:
		return Data
	return []
	
def removeNonPrintable(Text):
	return filter(lambda x: x in string.printable, Text)
	
def obtainCityList():
	cityList = []
	cityJson = jsonRead('City')
	for item in cityJson:
		strCity = ', '.join(item)
		cityList.append(strCity)
	cityList = [item.replace(' ','+') for item in cityList]
	return cityList
	
def obtainCusineList():
	f=open('Cusines.txt','r')
	Data=f.read()
	f.close()
	Data = Data.split('\n')
	Data = [item.replace(' ','+') for item in Data]
	return Data[:-1]

def emptyRestaurant(City_List,Cusine):
	dictRestaurant = {}
	dictRestaurant['Name']=''
	dictRestaurant['Category'] = []
	dictRestaurant['Rating']=''
	dictRestaurant['Reviews']=''
	dictRestaurant['Address']=''
	dictRestaurant['City']=''
	dictRestaurant['State']=''
	dictRestaurant['Zip']=''
	dictRestaurant['Phone']=''
	dictRestaurant['City_Search'] = City_List
	dictRestaurant['Cusine_Search'] = Cusine
	return dictRestaurant
	
def Single_Search_Page_List(Cusine,City,Cusine_Counter):
	try:
		if Cusine_Counter == '0':
			HTML = buildPageReterive(START_BASE_URL%(Cusine,City))
		else:	
			HTML = buildPageReterive(BASE_URL%(Cusine,City,Cusine_Counter))
		if HTML == None:
			print 'No HTML Data Found'
			raise Exception()
			
		Broken_Result_Check = soupCreator(HTML,'div','no-results')
		if Broken_Result_Check:
			return None
				
		Restaurant_List = soupCreator(HTML,'li','regular-search-result')
		if not Restaurant_List:
			print 'No Restaurant List Found'
			raise Exception()
			
	except Exception as e:
		print 'Single Search Page List Exception',Cusine,City,Cusine_Counter
		print 'Exception Occured:',e.__class__
		print 'Exception Message:', str(e)
		return []
	else:
		return Restaurant_List

def Category_Aggregrator(Restaurant,Restaurant_Name):
	try:
		Category = []
		Category_List = Restaurant.find('span',{'class':'category-str-list'}).find_all('a')
		for item in Category_List:
			Category.append(item.text)
	except Exception as e:
		print 'Category_Aggregrator Exception',Restaurant_Name
		print 'Exception Occured:',e.__class__
		print 'Exception Message:', str(e)
		return [] 
	else:
		return Category
		
def Address_Collector(Restaurant,Restaurant_Name):
	try:
		lst = []
		Address_Data = Restaurant.find('address')
		for Element in Address_Data.recursiveChildGenerator():
			if isinstance(Element, basestring):
				lst.append(Element.strip())
			elif Element.name == 'br':
				pass
	except Exception as e:
		print 'Address_Collector Exception',Restaurant_Name
		print 'Exception Occured:',e.__class__
		print 'Exception Message:', str(e)
		return []
	else:
		return lst
	
def Restaurant_Data_Collector(Restaurant_List,City,Cusine):
	Restaurant_Data = []
	for Restaurant in Restaurant_List:
		try:
			dictRestaurant = emptyRestaurant(City,Cusine)
			dictRestaurant['Name'] = Restaurant.find('a',{'class':'biz-name'}).find('span').text.strip()
			dictRestaurant['Category'] = Category_Aggregrator(Restaurant,dictRestaurant['Name'])
			
			print 'Restaurant Name',dictRestaurant['Name']
		
			try:
				dictRestaurant['Reviews'] = Restaurant.find('span',{'class':'review-count'}).text.strip().replace('reviews','').replace('review','').strip()
			except:
				dictRestaurant['Reviews'] = '0'
		
			try:
				dictRestaurant['Rating'] = Restaurant.find('i',{'class':'star-img'}).get('title').strip().replace('star rating','').strip()
			except:
				dictRestaurant['Rating'] = '0'
		
			try:
				Address = Address_Collector(Restaurant,dictRestaurant['Name'])
				if len(Address) == 2:
					dictRestaurant['Address'] = Address[0].strip()
					Address_Split = Address[-1].split(',')
					if len(Address_Split) == 2:
						dictRestaurant['City']= Address_Split[0].strip()
						dictRestaurant['State']= Address_Split[-1][0:3].strip()
						dictRestaurant['Zip']= Address_Split[-1][-5:].strip()
					else:
						print 'Address Split Not Avaliable',dictRestaurant['Name']
						raise Exception()
				else:
					print 'Address Not Avaliable',dictRestaurant['Name']
					raise Exception()
				
			except Exception as e:
				print 'Address Obtainer Exception'
				print 'Exception Occured:',e.__class__
				print 'Exception Message:', str(e)
				dictRestaurant['Address']='Unknown'
				dictRestaurant['City']='Unknown'
				dictRestaurant['State']='Unknown'
				dictRestaurant['Zip']='Unknown'
			
			dictRestaurant['Phone'] = Restaurant.find('span',{'class':'biz-phone'}).text.strip()
		
			for Key in dictRestaurant:
				if dictRestaurant[Key] is str:
					dictRestaurant[Key] = removeNonPrintable(dictRestaurant[Key])
				elif dictRestaurant[Key] is list:
					dictRestaurant[Key] = [str(removeNonPrintable(RestCategory)) for RestCategory in dictRestaurant[Key]]
		
		except Exception as e:
			print 'Address Data Collector Exception'
			print 'Exception Occured:',e.__class__
			print 'Exception Message:', str(e)
			continue
		else:
			Restaurant_Data.append(dictRestaurant)
	
	return Restaurant_Data
	
def createCSV(CSV_FILE_NAME):
	f = open(os.path.join(BASE_FOLDER,CSV_FILE_NAME)+'.csv','w')
	f.close()

def csvOperation(City):
	Data = []
	
	for File_Name in os.listdir(os.path.join(BASE_FOLDER,City)):
		if os.path.isfile(os.path.join(BASE_FOLDER,City,File_Name)) and File_Name.endswith('.json'):
			jsonData = jsonRead(os.path.join(City,File_Name[:-5]))
			if jsonData:
				Data = Data + jsonData
	
	CSV_FILE_NAME = os.path.join(City,City)
	createCSV(CSV_FILE_NAME)
	csvWrite(CSV_FILE_NAME,CSV_HEADER,'ab+')
	
	for dictRestaurant in Data:
		temp = []
		for Key in CSV_HEADER:
			temp.append(dictRestaurant[Key])
		csvWrite(CSV_FILE_NAME,temp,'ab+')
		
	print 'Total Number Of Restaurants Scrapped For City',City,'is',len(Data)

def Sleep_Timer(Big_Sleep=False):
	if Big_Sleep == True:
		Random_Time = [60,65,70,75,80,85,90,95,100,110,120]
	else:
		Random_Time = [15,20,25,30,35,40]
	
	Random_Sleep = random.choice(Random_Time)
	print 'Sleeping For',Random_Sleep,'Seconds'
	time.sleep(Random_Sleep)
						
def main():
	cityList = obtainCityList()
	cusineList = obtainCusineList()
	
	drive = createAuthorizer()
	if drive == None:
		print 'Google Drive Authentication Failure'
		return
	
	Yelp_FolderID = folderCheck(drive,ROOT_FOLDER,'root')
	if Yelp_FolderID == None:
		print ROOT_FOLDER ,'Folder Does Not Exist'
		return
	
	#cityList = ['Albuquerque,+NM','Tucson,+AZ','Fresno,+CA']
	#cusineList = ['Salvadorean']
	#cusineList.remove('Mexican')
	
	for City in cityList:
		CreateFolder(City)
		
		for Cusine in cusineList:
			try:
				print
				print 'Scrapping Data For City',City
				print 'Scrapping Data For Cusine',Cusine
				Cusine_Counter = 0
				Data = []
				Break_Counter = 0
				
				while True:
					print
					print 'Scrapping Page Start',Cusine_Counter
					Restaurant_List = Single_Search_Page_List(Cusine,City,str(Cusine_Counter))
					if Restaurant_List == None:
						break
					elif Restaurant_List == []:
						Break_Counter += 1
						if Break_Counter == 5:
							print 'Exiting The Cusine',Cusine
							break
						Sleep_Timer(Big_Sleep=True)
						continue
				
					Restaurant_Data = Restaurant_Data_Collector(Restaurant_List,City,Cusine)
					if Restaurant_Data:
						Data = Data + Restaurant_Data
				
					if Cusine_Counter % 20 == 0 and Cusine_Counter != 0:
						Sleep_Timer(Big_Sleep=False)
						
					if Cusine_Counter == 1000:
						break
					
					Cusine_Counter += 10

			except Exception as e:
				print 'Cusine List Exception',City,Cusine
				print 'Exception Occured:',e.__class__
				print 'Exception Message:', str(e)
				continue
			else:
				jsonWrite(os.path.join(City,Cusine),Data,'wb')
				print 'Cusine',Cusine,'Completed.'
				
				jsonFile = os.path.join(BASE_FOLDER,City,Cusine) +'.json'
				Result = googleDriveUpload(drive,Yelp_FolderID,City,jsonFile)
				if Result == None:
					print 'Error In While Google Drive Operation'
					
				Sleep_Timer(Big_Sleep=True)
				
		csvOperation(City)
		print 'City',City,'Completed'
		Sleep_Timer(Big_Sleep=True)
	
if __name__ == '__main__':		
	main()
