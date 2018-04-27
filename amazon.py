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

	amazonURL = []
	amazonURLTV = []
	genreList = []
	fileName = []

	#Open Chrome driver
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	options.add_argument('window-size=2000x3000')
	driver = webdriver.Chrome()
	#chrome_options=options
	# Opens list of URLs
	openURL(amazonURL, amazonURLTV, genreList, fileName)

	# local variables
	url = 'https://www.amazon.com/ap/signin?accountStatusPolicy=P1&clientContext=356-6438026-5845501&language=en_US&openid.assoc_handle=amzn_prime_video_desktop_us&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.primevideo.com%2Fauth%2Freturn%2Fref%3Dav_auth_ap%3F_encoding%3DUTF8%26location%3D%252Fref%253Ddv_auth_ret%253F_encoding%253DUTF8%2526ie%253DUTF8%2526query%253Dp_n_entity_type%25253DMovie%252526search-alias%25253Dinstant-video%252526index%25253Dfe-amazon-video%252526adult-product%25253D0%252526bq%25253D%252528and%252520sort%25253A%252527featured-rank%252527%252520%252528and%252520%252528and%252520%252528or%252520av_primary_genre%25253A%252527children%252527%252520av_primary_genre%25253A%252527family%252527%252529%252520%252528not%252520av_secondary_genre%25253A%252527indian%252527%252529%252529%252520%252528not%252520%252528or%252520regulatory_rating%25253A%25252718%252520%252527%252520regulatory_rating%25253A%252527nr%252527%252529%252529%252529%252529%252526av_offered_in_territory%25253DAU'
	USERNAME = ''
	PASSWORD = ''

	driver.get(url)
	# wait up to 10 seconds for the elements to become available
	driver.implicitly_wait(3)
	
	# use css selectors to grab the login inputs
	email = driver.find_element_by_css_selector('input[name=email]')
	password = driver.find_element_by_css_selector('input[name=password]')
	login = driver.find_element_by_css_selector('input[type="submit"]')

	email.send_keys(USERNAME)
	password.send_keys(PASSWORD)
	driver.implicitly_wait(10)

	login.click()

	# Parsing content for each genre
	amazon(amazonURL, genreList, fileName, driver)

	amazonTV(amazonURLTV, genreList, fileName, driver)

	driver.quit()

#-------------------------------------------------------------------------------------------------------------------------------------------------
#open list of URLs

def openURL(amazonURL, amazonURLTV, genreList, fileName):

	with open('movieList.csv') as movieList:
		reader = csv.reader(movieList)
		for row in reader:
			amazonURL.append(row[3])
			amazonURLTV.append(row[9])
			genreList.append(row[4])
			fileName.append(row[5])
	print('Loaded URLs')

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Amazon

def amazon(amazonURL, websiteGenre, fileName, driver):

	amazon = 'https://www.primevideo.com'
	logo = '/images/logos/amazon.png'
	movieList = []

	for i in range(1, len(amazonURL)):
		if not amazonURL[i] == '':
			print(websiteGenre[i] + '------------------')
			driver.get(amazonURL[i])
			driver.implicitly_wait(5)
			nextPage = True
		
			while nextPage:
				html = driver.page_source
				page_soup = soup(html, "html.parser")
				containers = page_soup.findAll("li", {"class":"av-result-card"})
				
				if containers:
					for container in containers:
						ids = container.findAll("input", {"name":"titleID"})					
						url = container.findAll("a", {"class":"av-play-icon"})
						year = container.findAll("span", {"class":"av-result-card-year"})
						overview = container.findAll("p", {"class":"av-result-card-synopsis"})
						data = {}
						data['name'] = container.div.div.h2.a.text
						data['name'] = unicodedata.normalize('NFKD', data['name']).encode('ASCII', 'ignore').decode("ascii")
						data['name'] = data['name'].replace(' III', ' 3')
						data['name'] = data['name'].replace(' II', ' 2')
						data['name'] = data['name'].replace(' IV', ' 4')
						data['name'] = data['name'].replace('Kill Bill: Volume 1', 'Kill Bill: Vol. 1')
						data['name'] = data['name'].replace('Kill Bill: Volume 2', 'Kill Bill: Vol. 2')
						data['type'] = 'movie'
						if len(ids):
							data['id'] = ids[0]['value']
						else:
							data['id'] = ''
						if url:
							data['url'] = amazon + url[0]['href']
						else:
							data['url'] = amazon + container.a['href']
						data['genre'] = [{'title': websiteGenre[i]}]
						data['poster_path'] = container.a.img['src']
						data['banner_art'] = ''
						data['stream'] = 'amazon'
						data['logo'] = logo
						data['classification'] = []
						data['runtime'] = 0
						data['release_date'] = str(year[0].text)
						data['overview'] = overview[0].text
						movieList.append(data)
					
					x = page_soup.findAll("ol", {"id":"av-pagination"})
					z = x[0].findAll("li")
					if z[len(z)-1]['class'][0] == 'av-pagination-next-page':
						y = amazon + z[len(z)-1].a['href']
						nextPage = True
						driver.get(y)
					else:
						print(z[len(z)-1]['class'])
						nextPage = False
				else:
					nextPage = False

			if os.path.isfile('./amazon/movies/' + fileName[i] + '.json'):
				os.remove('./amazon/movies/' + fileName[i] + '.json')

			for j in range(0, len(movieList)):
				writeToJSONFile('./amazon/movies/' + fileName[i], movieList[j], 'a')

			movieList = []

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Amazon Tv

def amazonTV(amazonURLTV, websiteGenre, fileName, driver):

	amazon = 'https://www.primevideo.com'
	logo = '/images/logos/amazon.png'
	tvList = []
	newtv = []

	for i in range(1, len(amazonURLTV)):
		if not amazonURLTV[i] == '':
			print(websiteGenre[i] + '---------TV---------')
			driver.get(amazonURLTV[i])
			driver.implicitly_wait(5)
			nextPage = True
		
			while nextPage:
				html = driver.page_source
				page_soup = soup(html, "html.parser")
				containers = page_soup.findAll("li", {"class":"av-result-card"})
				
				if containers:
					for container in containers:
						ids = container.findAll("input", {"name":"titleID"})
						year = container.findAll("span", {"class":"av-result-card-year"})
						overview = container.findAll("p", {"class":"av-result-card-synopsis"})
						data = {}
						data['name'] = container.div.div.h2.a.text
						data['name'] = unicodedata.normalize('NFKD', data['name']).encode('ASCII', 'ignore').decode("ascii")
						data['name'] = data['name'].replace(' III', ' 3')
						data['name'] = data['name'].replace(' II', ' 2')
						data['name'] = data['name'].replace(' IV', ' 4')
						data['type'] = 'tv'
						data['id'] = ids[0]['value']
						data['url'] = amazon + container.a['href']
						data['genre'] = [{'title': websiteGenre[i]}]
						data['poster_path'] = container.a.img['src']
						data['banner_art'] = ''
						data['stream'] = 'amazon'
						data['logo'] = logo
						data['classification'] = []
						data['runtime'] = 0
						data['release_date'] = str(year[0].text)
						data['overview'] = overview[0].text
						tvList.append(data)
					
					x = page_soup.findAll("ol", {"id":"av-pagination"})
					z = x[0].findAll("li")
					if z[len(z)-1]['class'][0] == 'av-pagination-next-page':
						y = amazon + z[len(z)-1].a['href']
						nextPage = True
						driver.get(y)
					else:
						print(z[len(z)-1]['class'])
						nextPage = False
				else:
					nextPage = False

			for tv in tvList:
				x = False
				for new in newtv:
					if tv['name'] == new['name']:
						x = True
						break
					else:
						x = False
				if not x:
					newtv.append(tv)

			if os.path.isfile('./amazon/tv/' + fileName[i] + '.json'):
				os.remove('./amazon/tv/' + fileName[i] + '.json')

			for j in range(0, len(newtv)):
				writeToJSONFile('./amazon/tv/' + fileName[i], newtv[j], 'a')

			tvList = []
			newtv = []

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Write data to json file

def writeToJSONFile(fileName, data, writeStatus):

	filePathNameWExt = fileName + '.json'
	with io.open(filePathNameWExt, writeStatus, encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False)
		f.write('\n')

#-------------------------------------------------------------------------------------------------------------------------------------------------

main()