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

	stan = 'https://play.stan.com.au/programs/'
	url = 'https://www.stan.com.au/?intent=authenticate'
	stanPlay = "/play"
	logo = '/images/logos/stan.png'
	size = "?resize=300px:200px"
	USERNAME = ''
	PASSWORD = ''
	genreList = []
	fileName = []
	mainJson = []
	movies = []
	tvs = []
	allContents = []

	openURL(genreList, fileName)

	#Open Chrome driver
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	options.add_argument('window-size=2000x3000')
	driver = webdriver.Chrome(chrome_options=options)

	#driver.get(url)
	# wait up to 10 seconds for the elements to become available
	#time.sleep(2)
	
	# use css selectors to grab the login inputs
	#email = driver.find_element_by_css_selector('input[data-reactid="254"]')
	#password = driver.find_element_by_css_selector('input[type=password]')
	#login = driver.find_element_by_css_selector('button[name="submit"]')

	#email.send_keys(USERNAME)
	#password.send_keys(PASSWORD)
	#login.click()

	driver.get('https://v6-pages-api.stan.com.au/sitemap.json')

	html = soup(driver.page_source, 'lxml')
	contents = json.loads(html.find("body").text)
	entries = contents['entries']

	for entrie in entries:
		data = {}
		data['title'] = entrie['title']
		data['url'] = entrie['url']
		mainJson.append(data)

	for mainJ in mainJson:
		driver.get(mainJ['url'])
		html = soup(driver.page_source, 'lxml')
		contents = json.loads(html.find("body").text)
		entries = contents['entries']

		for entrie in entries:
			data = {}
			data['name'] = entrie['title']
			if data['name'] == '':
				data['name'] = entrie['altTitle']

			data['name'] = unicodedata.normalize('NFKD', data['name']).encode('ASCII', 'ignore').decode("ascii")
			data['name'] = data['name'].replace(' III', ' 3')
			data['name'] = data['name'].replace(' II', ' 2')
			data['name'] = data['name'].replace(' IV', ' 4')
			data['name'] = data['name'].replace('Kill Bill: Volume 1', 'Kill Bill: Vol. 1')
			data['name'] = data['name'].replace('Kill Bill: Volume 2', 'Kill Bill: Vol. 2')

			data['id'] = int(entrie['id'])
			data['url'] = stan + entrie['id'] + stanPlay

			if entrie['programType'] == 'series':
				data['type'] = 'tv'
			else:
				data['type'] = entrie['programType']

			data['genre'] = []
			for i in range(0, len(entrie['tags'])):
				data['genre'].append({'title': entrie['tags'][i]['title']})

			for i in range(0, len(data['genre'])):
				data['genre'][i]['title'] = data['genre'][i]['title'].replace('Sci-Fi', 'Science Fiction')
				data['genre'][i]['title'] = data['genre'][i]['title'].replace('Animated', 'Animation')

			data['poster_path'] = entrie['images']['Poster Art']['url']

			for key in entrie['images']:
				if str(key)  == 'Banner-L0':
					data['banner_art'] = entrie['images']['Banner-L0']['url']
					break
				elif str(key)  == 'Banner-L1':
					data['banner_art'] = entrie['images']['Banner-L1']['url']
					break
				else: 
					data['banner_art'] = ''
					
			data['stream'] = 'stan'
			data['logo'] = logo
			data['classification'] = entrie['classifications']
			data['runtime'] = entrie['runtime']
			data['release_date'] = str(entrie['releaseYear'])

			if entrie['longDescription']:
				data['overview'] = entrie['longDescription']
			else:
				data['overview'] = entrie['description']

			allContents.append(data)

	for content in allContents:
		x = False
		if content['type'] == 'movie':
			for movie in movies:
				if content['id'] == movie['id']:
					x = True
					break				
			if not x:			
				movies.append(content)
		else:
			for tv in tvs:
				if content['id'] == tv['id']:
					x = True
					break
			if not x:
				tvs.append(content)

	stanMovies(movies, genreList, fileName)

	stanTvs(tvs, genreList, fileName)

	driver.quit()

#-------------------------------------------------------------------------------------------------------------------------------------------------
#Movies function

def stanMovies(movies, genreList, fileName):

	movieList = [[] for y in range(13)]

	for movie in movies:
		genres = movie['genre']
		a = b = c = d = False
		for genre in genres:
			if genre['title'] == 'Action' or  genre['title'] == 'Adventure' and not a:
				movieList[1].append(movie)
				a = True
			elif genre['title'] == 'Family' or  genre['title'] == 'Kids' and not b :
				movieList[2].append(movie)
				b= True
			elif genre['title'] == 'Classic':
				movieList[3].append(movie)
			elif genre['title'] == 'Comedy':
				movieList[4].append(movie)
			elif genre['title'] == 'Documentary':
				movieList[5].append(movie)
			elif genre['title'] == 'Drama' or genre['title'] == 'Musical' and not c:
				movieList[6].append(movie)
				c = True
			elif genre['title'] == 'Horror':
				movieList[7].append(movie)
			elif genre['title'] == 'Romance':
				movieList[9].append(movie)
			elif genre['title'] == 'Sci-Fi' or  genre['title'] == 'Fantasy' and not d:
				d = True
				movieList[10].append(movie)
			elif genre['title'] == 'Thriller':
				movieList[11].append(movie)
			elif len(genres) <= 1:
				movieList[12].append(movie)

	
	for j in range(1, len(movieList)-1):
		if os.path.isfile('./stan/movies/' + fileName[j] + '.json'):
			os.remove('./stan/movies/' + fileName[j] + '.json')
		for i in range(0, len(movieList[j])):
			writeToJSONFile('./stan/movies/' + fileName[j], movieList[j][i], 'a')

	if os.path.isfile('./stan/movies/missed.json'):
		os.remove('./stan/movies/missed.json')

	for i in range(0, len(movieList[12])):
		writeToJSONFile('./stan/movies/missed', movieList[j][i], 'a')

#-------------------------------------------------------------------------------------------------------------------------------------------------
#TVs function

def stanTvs(tvs, genreList, fileName):

	tvList = [[] for y in range(13)]

	for tv in tvs:
		genres = tv['genre']
		a = b = c = d = False
		for genre in genres:
			if genre['title'] == 'Action' or  genre['title'] == 'Adventure' and not a:
				tvList[1].append(tv)
				a = True
			elif genre['title'] == 'Family' or  genre['title'] == 'Kids' and not b :
				tvList[2].append(tv)
				b= True
			elif genre['title'] == 'Classic':
				tvList[3].append(tv)
			elif genre['title'] == 'Comedy':
				tvList[4].append(tv)
			elif genre['title'] == 'Documentary':
				tvList[5].append(tv)
			elif genre['title'] == 'Drama' or genre['title'] == 'Musical' and not c:
				tvList[6].append(tv)
				c = True
			elif genre['title'] == 'Horror':
				tvList[7].append(tv)
			elif genre['title'] == 'Romance':
				tvList[9].append(tv)
			elif genre['title'] == 'Sci-Fi' or  genre['title'] == 'Fantasy' and not d:
				d = True
				tvList[10].append(tv)
			elif genre['title'] == 'Thriller':
				tvList[11].append(tv)
			elif len(genres) <= 1:
				tvList[12].append(tv)

	
	for j in range(1, len(tvList)-1):
		if os.path.isfile('./stan/tv/' + fileName[j] + '.json'):
			os.remove('./stan/tv/' + fileName[j] + '.json')
		for i in range(0, len(tvList[j])):
			writeToJSONFile('./stan/tv/' + fileName[j], tvList[j][i], 'a')

	if os.path.isfile('./stan/tv/missed.json'):
		os.remove('./stan/tv/missed.json')

	for i in range(0, len(tvList[12])):
		writeToJSONFile('./stan/tv/missed', tvList[j][i], 'a')

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Write data to json file

def writeToJSONFile(fileName, data, writeStatus):

	filePathNameWExt = fileName + '.json'
	with io.open(filePathNameWExt, writeStatus, encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False)
		f.write('\n')

#-------------------------------------------------------------------------------------------------------------------------------------------------
#open list of URLs

def openURL(genreList, fileName):

	with open('movieList.csv') as movieList:
		reader = csv.reader(movieList)
		for row in reader:
			genreList.append(row[4])
			fileName.append(row[5])
	print('Loaded URLs')

#-------------------------------------------------------------------------------------------------------------------------------------------------

main()