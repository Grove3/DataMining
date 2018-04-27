from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from selenium import webdriver
import time
import codecs
import csv
import json
import io
import os
import unicodedata


#-------------------------------------------------------------------------------------------------------------------------------------------------
#Main function

def main():

	foxtelURL = []
	foxtelURLTV = []
	genreList = []
	fileName = []

	#Open Chrome driver
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	options.add_argument('window-size=2000x3000')
	driver = webdriver.Chrome(chrome_options=options)

	# Opens list of URLs
	openURL(foxtelURL, foxtelURLTV, genreList, fileName)

	url = 'https://now.foxtel.com.au/app/#/login'
	USERNAME = ''
	PASSWORD = ''
	
	driver.get(url)
	# wait up to 10 seconds for the elements to become available
	driver.implicitly_wait(5)
	
	# use css selectors to grab the login inputs
	email = driver.find_element_by_css_selector('input[type=email]')
	password = driver.find_element_by_css_selector('input[type=password]')
	login = driver.find_element_by_css_selector('button')

	email.send_keys(USERNAME)
	password.send_keys(PASSWORD)

	login.click()

	# Parsing content for each genre
	foxtel(foxtelURL, genreList, fileName, driver)

	foxtelTV(foxtelURLTV, genreList, fileName, driver)

	driver.quit()

#-------------------------------------------------------------------------------------------------------------------------------------------------
#open list of URLs

def openURL(foxtelURL, foxtelURLTV, genreList, fileName):

	with open('movieList.csv') as movieList:
		reader = csv.reader(movieList)
		for row in reader:
			foxtelURL.append(row[2])
			foxtelURLTV.append(row[8])
			genreList.append(row[4])
			fileName.append(row[5])
	print('Loaded URLs')

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Write data to json file

def writeToJSONFile(fileName, data, writeStatus):

	filePathNameWExt = fileName + '.json'
	with io.open(filePathNameWExt, writeStatus, encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False)
		f.write('\n')

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Foxtel

def foxtel(foxtelURL, websiteGenre, fileName, driver):

	# local variables
	foxtel = 'https://now.foxtel.com.au/app/#/movie/'
	pic = 'https://now.foxtel.com.au/app/imageHelper.php?id='
	movieList = []
	logo = '/images/logos/foxtel.png'

	for i in range(1, len(foxtelURL)):
		if not foxtelURL[i] == '':
			print(websiteGenre[i] + '------------------')
			driver.get(foxtelURL[i])
			driver.implicitly_wait(5)
			
			html = soup(driver.page_source, 'lxml')
			contents = json.loads(html.find("body").text)
			entries = contents['content']['contentGroup'][0]['items']
			
			for entrie in entries:
				data = {}
				data['name'] = entrie['title']
				data['name'] = unicodedata.normalize('NFKD', data['name']).encode('ASCII', 'ignore').decode("ascii")
				data['name'] = data['name'].replace(' III', ' 3')
				data['name'] = data['name'].replace(' II', ' 2')
				data['name'] = data['name'].replace(' IV', ' 4')
				data['name'] = data['name'].replace('Rocky V', 'Rocky 5')
				data['name'] = data['name'].replace('LOTR', 'The Lord of the Rings')
				data['name'] = data['name'].replace('Middle School: Worst Years Of My...', 'Middle School: The Worst Years of My Life')
				data['name'] = data['name'].replace('Pirates Of The Caribbean: Dead Men..', 'Pirates of the Caribbean: Dead Men Tell No Tales')
				data['name'] = data['name'].replace('Fantastic Beasts & Where To Find...', 'Fantastic Beasts and Where To Find Them')
				data['type'] = 'movie'
				if (data['name'][:7] != 'Trailer'):
					if(entrie['showId'][:8] != 'PRnoshow'):
						data['id'] = int(entrie['showId'])
					else:
						data['id'] = entrie['showId']
					data['url'] = foxtel + entrie['showId']
					data['genre'] = [{'title': websiteGenre[i]}]
					data['poster_path'] = pic + entrie['portraitImage'] + '&w=800'
					data['banner_art'] = ''
					data['stream'] = 'foxtel'
					data['logo'] = logo
					data['classification'] = []
					data['runtime'] = 0
					data['release_date'] = ''
					data['overview'] = ''
					
				movieList.append(data)
	
			if os.path.isfile('./foxtel/movies/' + fileName[i] + '.json'):
				os.remove('./foxtel/movies/' + fileName[i] + '.json')
	
			for j in range(0, len(movieList)):
				writeToJSONFile('./foxtel/movies/' + fileName[i], movieList[j], 'a')
			
			movieList = []

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Foxtel TV

def foxtelTV(foxtelURLTV, websiteGenre, fileName, driver):

	# local variables
	foxtel = 'https://now.foxtel.com.au/app/#/movie/'
	pic = 'https://now.foxtel.com.au/app/imageHelper.php?id='
	tvList = []
	logo = '/images/logos/foxtel.png'

	for i in range(1, len(foxtelURLTV)):
		if not foxtelURLTV[i] == '':
			print(websiteGenre[i] + '---------tv---------')
			driver.get(foxtelURLTV[i])
			driver.implicitly_wait(5)
			
			html = soup(driver.page_source, 'lxml')
			contents = json.loads(html.find("body").text)
			entries = contents['content']['contentGroup'][0]['items']
			
			for entrie in entries:
				data = {}
				data['name'] = entrie['title']
				data['name'] = unicodedata.normalize('NFKD', data['name']).encode('ASCII', 'ignore').decode("ascii")
				data['name'] = data['name'].replace(' III', ' 3')
				data['name'] = data['name'].replace(' II', ' 2')
				data['name'] = data['name'].replace(' IV', ' 4')
				data['type'] = 'tv'
				if (data['name'][:7] != 'Trailer'):
					if(entrie['showId'][:8] != 'PRnoshow'):
						data['id'] = int(entrie['showId'])
					else:
						data['id'] = entrie['showId']
					
					data['url'] = foxtel + entrie['showId']
					data['genre'] = [{'title': websiteGenre[i]}]
					data['poster_path'] = pic + entrie['portraitImage'] + '&w=800'
					data['banner_art'] = ''
					data['stream'] = 'foxtel'
					data['logo'] = logo
					data['classification'] = []
					data['runtime'] = 0
					data['release_date'] = ''
					data['overview'] = ''
					
					tvList.append(data)
	
			if os.path.isfile('./foxtel/tv/' + fileName[i] + '.json'):
				os.remove('./foxtel/tv/' + fileName[i] + '.json')
	
			for j in range(0, len(tvList)):
				writeToJSONFile('./foxtel/tv/' + fileName[i], tvList[j], 'a')
			
			tvList = []

main()