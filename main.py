import time
import codecs
import csv
import json
import io
import os
import http.client
import re
import unicodedata
import subprocess


def main():
	start = time.time()

	genreList = []
	fileName = []
	movieList = []
	tvList = []
	procs = []
	streams = ["netflix.py", "stan.py", "amazon.py", "foxtel.py", "processtmdb.py"]
	
#	#Scrap websites
	for stream in streams:
		procs.append(subprocess.Popen([stream], shell=True))
	for p in procs:
		p.wait()
	

	openURL(genreList, fileName)


#	#Movies
	streams = ['netflix', 'stan', 'amazon', 'foxtel']
	importContents(streams, movieList, fileName, '/movies/')
	movieList.sort(key=extract_time)
	movieList = checkDuplicates(movieList)

	insertIdsFile(movieList, 'movie_ids', 'movie')
	insertIdsOnline(movieList)

	if os.path.isfile('./jsonFiles/allMovies.json'):
		os.remove('./jsonFiles/allMovies.json')
	for movie in movieList:
		writeToJSONFile('jsonFiles', 'allMovies', movie, 'a')

#	loadJson('jsonFiles', 'allMovies', movieList)
	insertContent(movieList)
	insertContentOnline(movieList)

	if os.path.isfile('./jsonFiles/allMovies.json'):
		os.remove('./jsonFiles/allMovies.json')
	for movie in movieList:
		writeToJSONFile('jsonFiles', 'allMovies', movie, 'a')



	#TV Showes
	importContents(streams, tvList, fileName, '/tv/')
	tvList.sort(key=extract_time)
	tvList = checkDuplicates(tvList)

	insertIdsFile(tvList, 'tv_series_ids', 'tv')
	insertIdsOnline(tvList)

	if os.path.isfile('./jsonFiles/allTvs.json'):
		os.remove('./jsonFiles/allTvs.json')
	for tv in tvList:
		writeToJSONFile('jsonFiles', 'allTvs', tv, 'a')

#	loadJson('jsonFiles', 'allTvs', tvList)
	insertContent(tvList)
	insertContentOnline(tvList)

	if os.path.isfile('./jsonFiles/allTvs.json'):
		os.remove('./jsonFiles/allTvs.json')
	for tv in tvList:
		writeToJSONFile('jsonFiles', 'allTvs', tv, 'a')



	if os.path.isfile('./jsonFiles/everything.json'):
		os.remove('./jsonFiles/everything.json')
	for movie in movieList:
		writeToJSONFile('jsonFiles', 'everything', movie, 'a')
	for tv in tvList:
		writeToJSONFile('jsonFiles', 'everything', tv, 'a')

	addToCache(movieList, tvList)

	end = time.time()
	total = (((end - start)/60)/60)
	print(str(total) + 'hr')



#-------------------------------------------------------------------------------------------------------------------------------------------------
#Import all content	

def importContents(streams, movieList, fileName, type):

	contents = []

	if type == '/movies/':
		for i in range(0, len(streams)):
			for j in range(1, len(fileName)):
				print('Importing ' + streams[i] + '-' + fileName[j])
				if os.path.isfile('./' + streams[i] + type + fileName[j] + '.json'):
					loadJson('./' + streams[i] + type, fileName[j], contents)
		
				for content in contents:
					data = {}
					data['name'] = content['name']
					data['id'] = 0
					data['popularity'] = 0
					if not content['poster_path'] == '':
						data['poster_path'] = content['poster_path']
					else:
						data['poster_path'] = ''
					data['stream'] = []
					data['genre'] = content['genre']
					data['type'] = content['type']
					data['tmdb'] = {"poster_path": "", "banner_art": content['banner_art'], "release_date": content['release_date'], "runtime": content['runtime'], "vote_average": 0, "vote_count": 0, "budget": 0, "revenue": 0, "imdb_id": "", "overview": content['overview'], "videos": {}, "credits": {}}
					data['stream'].append({"name":content['stream'], "id":content['id'], "url":content['url'], "logo":content['logo']})
					data['classification'] = content['classification']
			
					movieList.append(data)

				contents = []
	
	else:
		for i in range(0, len(streams)):
			for j in range(1, len(fileName)):
				print('Importing ' + streams[i] + '-' + fileName[j])
				if os.path.isfile('./' + streams[i] + type + fileName[j] + '.json'):
					loadJson('./' + streams[i] + type, fileName[j], contents)
		
				for content in contents:
					data = {}
					data['name'] = content['name']
					data['id'] = 0
					data['popularity'] = 0
					if not content['poster_path'] == '':
						data['poster_path'] = content['poster_path']
					else:
						data['poster_path'] = ''
					data['stream'] = []
					data['genre'] = content['genre']
					data['type'] = content['type']
					data['tmdb'] = {"poster_path": "", "banner_art": content['banner_art'], "last_air_date": content['release_date'], "episode_run_time": [content['runtime']], "vote_average": 0, "vote_count": 0, "overview": "", "videos": {}, "credits": {}}
					data['stream'].append({"name":content['stream'], "id":content['id'], "url":content['url'], "logo":content['logo']})
					data['classification'] = content['classification']
			
					movieList.append(data)

				contents = []

#-------------------------------------------------------------------------------------------------------------------------------------------------
#Check Duplicates

def checkDuplicates(content):

	print('Checking for duplicates, Please wait...')

	data = {}
	delete = [] 

	for ind, movie in enumerate(content):
		a = False
		name = movie['name']
		name = re.sub("[\(\[].*?[\)\]]", "", name)
		name = re.sub("[:!$%\'\";,.&-]", "", name)
		name = name.replace(' ','').lower()
		
		try:
			index = data[name]['index']
			for stream in content[index]['stream']:
				if stream['name'] == movie['stream'][0]['name']:
					a = True
			if not a:
				content[index]['stream'].append(movie['stream'][0])
			
			if not content[index]['poster_path'] and movie['poster_path']:
				content[index]['poster_path'] = movie['poster_path']

			for newGenre in movie['genre']:
				if newGenre not in content[index]['genre']:
					content[index]['genre'].append(newGenre)

			delete.append(ind)

		except:
			data[name] = {'index': ind}

	delete.reverse()

	for d in delete:
		content.remove(content[d])

	return(content)

#-------------------------------------------------------------------------------------------------------------------------------------------------
#Insert IDs from TMDB fle

def insertIdsFile(contents, fileName, type):

	tmdbIds = {}
	cacheIds = {}
	cacheFound = 0
	tmdbFound = 0
	notFound = 0

	print('Import cache Ids')
	loadObjectData('jsonFiles', 'cache', cacheIds)
	print('Import TMDB Ids')
	loadObjectData('tmdb', fileName, tmdbIds)
	

	print('Inserting IDs, please wait...')
	
	for content in contents:
		x = content['name']
		x = unicodedata.normalize('NFKD', x).encode('ASCII', 'ignore').decode("ascii")
		if x:
			x = re.sub("[\(\[].*?[\)\]]", "", x)
			x = re.sub("[:!$%\'\";,.&-]", "", x)
			x = x.replace(' ','').lower()
			if x in cacheIds and cacheIds[x]['type'] == type:
				content['id'] = cacheIds[x]['id']
				content['popularity'] = cacheIds[x]['popularity']
				cacheFound += 1

	for content in contents:
		if content['id'] == 0:
			x = content['name']
			x = unicodedata.normalize('NFKD', x).encode('ASCII', 'ignore').decode("ascii")
			if x:
				x = re.sub("[\(\[].*?[\)\]]", "", x)
				x = re.sub("[:!$%\'\";,.&-]", "", x)
				x = x.replace(' ','').lower()
				if x in tmdbIds:
					content['id'] = tmdbIds[x]['id']
					content['popularity'] = tmdbIds[x]['popularity']
					tmdbFound += 1

	for content in contents:
		x = content['name']
		x = unicodedata.normalize('NFKD', x).encode('ASCII', 'ignore').decode("ascii")
		if x:
			x = re.sub("[\(\[].*?[\)\]]", "", x)
			x = re.sub("[:!$%\'\";,.&-]", "", x)
			x = x.replace(' ','').lower()
			if x in tmdbIds:
				content['popularity'] = tmdbIds[x]['popularity']

	for content in contents:
		if content['id'] == 0:
			notFound +=1
			

	print(str(cacheFound) + ' cache IDs found')
	print(str(tmdbFound) + ' tmdb IDs found')
	print(str(notFound) + ' IDs NOT found')

#-------------------------------------------------------------------------------------------------------------------------------------------------
#Insert IDs from TMDB online

def insertIdsOnline(contents):

	found = 0

	for content in contents:
		if content['id'] == 0:
			name = content['name']
			name = re.sub("[\(\[].*?[\)\]]", "", name)
			name = re.sub("[:!$%\'\";,.&-]", "", name)
			name2 = name.replace(' ','')
			name = name.replace(' ','+').lower()
			urlAddress = "/3/search/movie?api_key={API KEY}&query=" + name
			conn = http.client.HTTPSConnection("api.themoviedb.org")
			payload = "{}"
			conn.request("GET", urlAddress, payload)
			res = conn.getresponse()
			data = res.read()
			if res.status == 200:
				data = data.decode("utf-8")
				data = json.loads(data)
				if data['total_results'] > 0:
					for s in range(0, len(data['results'])):
						temp = data['results'][s]['title']
						temp = re.sub("[\(\[].*?[\)\]]", "", temp)
						temp = re.sub("[:!$%\'\";,.&-]", "", temp)
						temp = temp.replace(' ','')
						if name2.lower() == temp.lower():
							content['id'] = data['results'][s]['id']
							content['popularity'] = data['results'][s]['popularity']
							content['type'] = 'movie'
							print(content['name'] + "---------------")
							found += 1
							break
					else:
						print(content['name'] + ' break loop************')						
				else:
					urlAddress = "/3/search/tv?api_key={API KEY}&query=" + name
					conn = http.client.HTTPSConnection("api.themoviedb.org")
					payload = "{}"
					conn.request("GET", urlAddress, payload)
					res = conn.getresponse()
					data = res.read()
					if res.status == 200:
						data = data.decode("utf-8")
						data = json.loads(data)
						if data['total_results'] > 0:
							for s in range(0, len(data['results'])):
								temp = data['results'][s]['name']
								temp = re.sub("[\(\[].*?[\)\]]", "", temp)
								temp = re.sub("[:!$%\'\";,.&-]", "", temp)
								temp = temp.replace(' ','')
								if name2.lower() == temp.lower():
									content['id'] = data['results'][s]['id']
									content['type'] = 'tv'
									content['popularity'] = data['results'][s]['popularity']
									print(content['name'] + "----------------------------------------------------------")
									found += 1
									break
							else:
								print(content['name'] + ' break loop************')							
						else:
							print(content['name'] + "------No ID found------")

	print(str(found) + ' IDs found online')

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Load Content

def insertContent(contents):

	cache = []
	missed = []
	tempGenre = []
	temp = {}
	found = 0
	notFound = 0

	print('Import Contents')
	loadJson('jsonFiles', 'cache', cache)
	cache.sort(key=extract_time)

	for ind, movie in enumerate(cache):
		temp[movie['id']] = {'index': ind, 'type': movie['type']}


	for content in contents:
		if content['id'] != 0:
			if content['type'] == 'movie':
				try:
					index = temp[content['id']]['index']
					if (content['type'] == temp[content['id']]['type']):
						content['genre'] = cache[index]['genre']
						content['poster_path'] = cache[index]['poster_path']
						content['tmdb']['poster_path'] = cache[index]['tmdb']['poster_path']
						content['tmdb']['banner_art'] = cache[index]['tmdb']['banner_art']
						content['tmdb']['release_date'] = cache[index]['tmdb']['release_date']
						content['tmdb']['runtime'] = cache[index]['tmdb']['runtime']
						content['tmdb']['vote_average'] = cache[index]['tmdb']['vote_average']
						content['tmdb']['vote_count'] = cache[index]['tmdb']['vote_count']
						content['tmdb']['budget'] = cache[index]['tmdb']['budget']
						content['tmdb']['revenue'] = cache[index]['tmdb']['revenue']
						content['tmdb']['imdb_id'] = cache[index]['tmdb']['imdb_id']
						content['tmdb']['overview'] = cache[index]['tmdb']['overview']
						content['tmdb']['videos'] = cache[index]['tmdb']['videos']
						content['tmdb']['credits'] = cache[index]['tmdb']['credits']
				except:
					missed.append(content['id'])
			else:
				try:
					index = temp[content['id']]['index']
					if (content['type'] == temp[content['id']]['type']):
						content['genre'] = cache[index]['genre']
						content['poster_path'] = cache[index]['poster_path']
						content['tmdb']['poster_path'] = cache[index]['tmdb']['poster_path']
						content['tmdb']['banner_art'] = cache[index]['tmdb']['banner_art']
						content['tmdb']['first_air_date'] = cache[index]['tmdb']['first_air_date']
						content['tmdb']['last_air_date'] = cache[index]['tmdb']['last_air_date']
						content['tmdb']['episode_run_time'] = cache[index]['tmdb']['episode_run_time']
						content['tmdb']['number_of_episodes'] = cache[index]['tmdb']['number_of_episodes']
						content['tmdb']['number_of_seasons'] = cache[index]['tmdb']['number_of_seasons']
						content['tmdb']['vote_average'] = cache[index]['tmdb']['vote_average']
						content['tmdb']['vote_count'] = cache[index]['tmdb']['vote_count']
						content['tmdb']['overview'] = cache[index]['tmdb']['overview']
						content['tmdb']['videos'] = cache[index]['tmdb']['videos']
						content['tmdb']['credits'] = cache[index]['tmdb']['credits']
				except:
					missed.append(content['id'])

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Load TMDB Content

def insertContentOnline(contents):

	tempGenre = []

#  or content['tmdb']['videos'] == {} or content['tmdb']['credits'] == {}
	for content in contents:
		if content['tmdb']['poster_path'] == '' or content['tmdb']['poster_path'] == 'null' or content['tmdb']['banner_art'] == '':
			if content['type'] == 'movie':
				if content['id'] != 0:
					print('Inserting Movie content for '+ content['name'] +', Please Wait')
					urlAddress = "/3/movie/" + str(content['id']) + "?api_key={API KEY}&append_to_response=videos%2Ccredits"
					conn = http.client.HTTPSConnection("api.themoviedb.org")
					payload = "{}"
					conn.request("GET", urlAddress, payload)
					res = conn.getresponse()
					data = res.read()
					if res.status == 200:
						data = data.decode("utf-8")
						data = json.loads(data)
						for genre in data['genres']:
							tempGenre.append({'title': genre['name']})
						for genre in tempGenre:
							if genre not in content['genre']:
								content['genre'].append(genre)
						content['tmdb']['poster_path'] = data['poster_path']
						content['tmdb']['banner_art'] = data['backdrop_path']
						try:
							content['tmdb']['release_date'] = data['release_date'][:4]
						except:
							content['tmdb']['release_date'] = ''
						content['tmdb']['runtime'] = data['runtime']
						content['tmdb']['vote_average'] = data['vote_average']
						content['tmdb']['vote_count'] = data['vote_count']
						content['tmdb']['budget'] = data['budget']
						content['tmdb']['revenue'] = data['revenue']
						content['tmdb']['imdb_id'] = data['imdb_id']
						content['tmdb']['overview'] = data['overview']
						try:
							content['tmdb']['videos'] = data['videos']['results'][0]
						except:
							content['tmdb']['videos'] = {}
						content['tmdb']['credits'] = {'cast': data['credits']['cast'][:6], 'crew': data['credits']['crew'][:6]}
						if data['poster_path']:
							content['poster_path'] = 'https://image.tmdb.org/t/p/original/' + data['poster_path']
				else:
					noID = content['name']
					print(content['name'] + ' No ID')
			else:
				if content['id']:
					print('Inserting TV content for '+ content['name'] +', Please Wait')
					urlAddress = "/3/tv/" + str(content['id']) + "?api_key={API KEY}&append_to_response=videos%2Ccredits"
					conn = http.client.HTTPSConnection("api.themoviedb.org")
					payload = "{}"
					conn.request("GET", urlAddress, payload)
					res = conn.getresponse()
					data = res.read()
					if res.status == 200:
						data = data.decode("utf-8")
						data = json.loads(data)
						for genre in data['genres']:
							tempGenre.append({'title': genre['name']})
						for genre in tempGenre:
							if genre not in content['genre']:
								content['genre'].append(genre)
						content['tmdb']['poster_path'] = data['poster_path']
						content['tmdb']['banner_art'] = data['backdrop_path']
						try:
							content['tmdb']['first_air_date'] = data['first_air_date'][:4]
						except:
							content['tmdb']['first_air_date'] = ''
						try:
							content['tmdb']['last_air_date'] = data['last_air_date'][:4]
						except:
							content['tmdb']['last_air_date'] = ''
						content['tmdb']['episode_run_time'] = data['episode_run_time']
						content['tmdb']['number_of_episodes'] = data['number_of_episodes']
						content['tmdb']['number_of_seasons'] = data['number_of_seasons']
						content['tmdb']['vote_average'] = data['vote_average']
						content['tmdb']['vote_count'] = data['vote_count']
						content['tmdb']['overview'] = data['overview'] 
						try:
							content['tmdb']['videos'] = data['videos']['results'][0]
						except:
							content['tmdb']['videos'] = {}
						content['tmdb']['credits'] = {'cast': data['credits']['cast'][:6], 'crew': data['credits']['crew'][:6]}
						if data['poster_path']:
							content['poster_path'] = 'https://image.tmdb.org/t/p/original/' + data['poster_path']
				else:
					noID = content['name']
					print(content['name'] + ' No ID')

		tempGenre = []


#-------------------------------------------------------------------------------------------------------------------------------------------------
# Add new Content to cache

def addToCache(contents, tvList):

	cache = []
	temp = {}

	print('Adding new content to cache')
	loadJson('jsonFiles', 'cache', cache)
	cache.sort(key=extract_time)

	for tv in tvList:
		contents.append(tv)

	for ind, movie in enumerate(cache):
		temp[movie['id']] = {'index': ind}

	for content in contents:
		if content['id'] != 0:
			try:
				index = temp[content['id']]['index']
			except:
				writeToJSONFile('jsonFiles', 'cache', content, 'a')

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Write data to json file

def writeToJSONFile(path, fileName, data, writeStatus):

	filePathNameWExt = r'./' + path + '/' + fileName + '.json'
	with io.open(filePathNameWExt, writeStatus, encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False)
		f.write('\n')

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Get TMdB id

def loadJson(path, fileName, data):

	filePathNameWExt = './' + path + '/' + fileName + '.json'
	with io.open(filePathNameWExt, encoding="utf-8") as f:
		for line in f:
			data.append(json.loads(line))

#-------------------------------------------------------------------------------------------------------------------------------------------------

def extract_time(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return str(json['name'])
    except KeyError:
        return 0

#-------------------------------------------------------------------------------------------------------------------------------------------------

def pop_extract_time(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return int(json['popularity'])
    except KeyError:
        return 0

#-------------------------------------------------------------------------------------------------------------------------------------------------

# Sort list TMDB movieData

def obj_extract_time(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return str(json[title])
    except KeyError:
        return 0

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Sort list TMDB movieData

def tv_extract_time(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return str(json['original_name'])
    except KeyError:
        return 0

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


def loadObjectData(path, fileName, data):

	temp = []

	loadJson(path, fileName, temp)
	temp.sort(key=extract_time)
	for movie in temp:
		x = movie['name']
		x = unicodedata.normalize('NFKD', x).encode('ASCII', 'ignore').decode("ascii")
		if x:
			x = re.sub("[\(\[].*?[\)\]]", "", x)
			x = re.sub("[:!$%\'\";,.&-]", "", x)
			x = x.replace(' ','').lower()
			try:
				data[x] = {'id': movie['id'], 'popularity': movie['popularity'], 'type': movie['type']}
			except:
				data[x] = {'id': movie['id'], 'popularity': movie['popularity']}

#-------------------------------------------------------------------------------------------------------------------------------------------------


main()