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

	netflixURL = []
	netflixURLTV = []
	genreList = []
	fileName = []

	#Open Chrome driver
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	options.add_argument('window-size=2000x3000')
	driver = webdriver.Chrome(chrome_options=options)

	# Opens list of URLs
	openURL(netflixURL, netflixURLTV, genreList, fileName)

	url = 'https://www.netflix.com/au/login'
	USERNAME = ''
	PASSWORD = ''
	
	driver.get(url)
	# wait up to 10 seconds for the elements to become available
	driver.implicitly_wait(5)
	
	# use css selectors to grab the login inputs
	email = driver.find_element_by_css_selector('input[name=email]')
	password = driver.find_element_by_css_selector('input[name=password]')
	login = driver.find_element_by_css_selector('button[type="submit"]')

	email.send_keys(USERNAME)
	password.send_keys(PASSWORD)

	login.click()

	driver.get('https://www.netflix.com/SwitchProfile?tkn=A523JK2EC5ANTLAYQ7ALJN77TQ')

	# Parsing content for each genre
	netflix(netflixURL, genreList, fileName, driver)

	netflixTV(netflixURLTV, genreList, fileName, driver)

	driver.quit()

#-------------------------------------------------------------------------------------------------------------------------------------------------
#open list of URLs

def openURL(netflixURL, netflixURLTV, genreList, fileName):

	with open('movieList.csv') as movieList:
		reader = csv.reader(movieList)
		for row in reader:
			netflixURL.append(row[0])
			netflixURLTV.append(row[6])
			genreList.append(row[4])
			fileName.append(row[5])
	print('Loaded URLs')

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Netflix

def netflix(netflixURL, websiteGenre, fileName, driver):

	# local variables
	netflix = 'https://netflix.com/au'
	movieList = []
	logo = '/images/logos/netflix.png'

	for i in range(1, len(netflixURL)):
		print(websiteGenre[i] + '------------------')
		driver.get(netflixURL[i])
		driver.implicitly_wait(5)
		scroll(driver)
		#driver.get_screenshot_as_file('./netflix/' + fileName[i] + '.png')

		html = driver.page_source
		page_soup = soup(html, "html.parser")
		containers = page_soup.findAll("div", {"class":"title-card-container"})

		for container in containers:
			url = container.div.div.a["href"]
			for x in range(1, len(url)):
				if url[x] == '/':
					y = [x, 0]
				if url[x] == '?':
					y[1] = x
			ids = url[y[0]+1:y[1]]
			data = {}
			data['name'] = container.div.div.a["aria-label"]
			data['name'] = unicodedata.normalize('NFKD', data['name']).encode('ASCII', 'ignore').decode("ascii")
			data['name'] = data['name'].replace(' III', ' 3')
			data['name'] = data['name'].replace(' II', ' 2')
			data['name'] = data['name'].replace(' IV', ' 4')
			data['id'] = int(ids)
			data['type'] = 'movie'
			data['url'] = netflix + url
			data['genre'] = [{'title': websiteGenre[i]}]
			data['poster_path'] = ''
			data['banner_art'] = ''
			data['stream'] = 'netflix'
			data['logo'] = logo
			data['classification'] = []
			data['runtime'] = 0
			data['release_date'] = ''
			data['overview'] = ''

			movieList.append(data)

		if os.path.isfile('./netflix/movies/' + fileName[i] + '.json'):
			os.remove('./netflix/movies/' + fileName[i] + '.json')

		for j in range(0, len(movieList)):
			writeToJSONFile('./netflix/movies/' + fileName[i], movieList[j], 'a')
		
		movieList = []

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Netflix TV

def netflixTV(netflixURLTV, websiteGenre, fileName, driver):

	# local variables
	netflix = 'https://netflix.com/au'
	tvList = []
	logo = '/images/logos/netflix.png'

	for i in range(1, len(netflixURLTV)):
		if not netflixURLTV[i] == '':
			print(websiteGenre[i] + '---------tv---------')
			driver.get(netflixURLTV[i])
			driver.implicitly_wait(5)
			scroll(driver)
			#driver.get_screenshot_as_file('./netflix/' + fileName[i] + '.png')
			
			html = driver.page_source
			page_soup = soup(html, "html.parser")
			containers = page_soup.findAll("div", {"class":"title-card-container"})
			
			for container in containers:
				url = container.div.div.a["href"]
				for x in range(1, len(url)):
					if url[x] == '/':
						y = [x, 0]
					if url[x] == '?':
						y[1] = x
				ids = url[y[0]+1:y[1]]
				data = {}
				data['name'] = container.div.div.a["aria-label"]
				data['name'] = unicodedata.normalize('NFKD', data['name']).encode('ASCII', 'ignore').decode("ascii")
				data['name'] = data['name'].replace(' III', ' 3')
				data['name'] = data['name'].replace(' II', ' 2')
				data['name'] = data['name'].replace(' IV', ' 4')
				data['type'] = 'tv'
				data['id'] = int(ids)
				data['url'] = netflix + url
				data['genre'] = [{'title': websiteGenre[i]}]
				data['poster_path'] = ''
				data['banner_art'] = ''
				data['stream'] = 'netflix'
				data['logo'] = logo
				data['classification'] = []
				data['runtime'] = 0
				data['release_date'] = ''
				data['overview'] = ''
				
				tvList.append(data)
	
			if os.path.isfile('./netflix/tv/' + fileName[i] + '.json'):
				os.remove('./netflix/tv/' + fileName[i] + '.json')
	
			for j in range(0, len(tvList)):
				writeToJSONFile('./netflix/tv/' + fileName[i], tvList[j], 'a')
			
			tvList = []


#-------------------------------------------------------------------------------------------------------------------------------------------------
# Write data to json file

def writeToJSONFile(fileName, data, writeStatus):

	filePathNameWExt = fileName + '.json'
	with io.open(filePathNameWExt, writeStatus, encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False)
		f.write('\n')

#-------------------------------------------------------------------------------------------------------------------------------------------------
#Web Scroll function

def scroll(driver):
	SCROLL_PAUSE_TIME = 3

	# Get scroll height
	last_height = driver.execute_script("return document.body.scrollHeight")

	while True:
		# Scroll down to bottom
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		
		# Wait to load page
		time.sleep(SCROLL_PAUSE_TIME)
		
		# Calculate new scroll height and compare with last scroll height
		new_height = driver.execute_script("return document.body.scrollHeight")
		if new_height == last_height:
			break
		last_height = new_height

#-------------------------------------------------------------------------------------------------------------------------------------------------

main()