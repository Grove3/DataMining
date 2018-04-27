import time
import codecs
import csv
import json
import io
import os
import http.client
import re
import unicodedata

def main():

	movieIds = []
	tvIds = []
	data = []
	dataObj = {}
	delete = []

	loadJson('tmdb', 'movie_ids_tmdb', movieIds)
	loadJson('tmdb', 'tv_series_ids_tmdb', tvIds)

	for movie in movieIds:
		name = movie['original_title']
		name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode("ascii")
		name = re.sub("[\(\[].*?[\)\]]", "", name)
		name = re.sub("[:!$%\'\";,.&-]", "", name)
		if name and not name.startswith(" ") and not movie['adult']:
			name = name.replace(' III', ' 3')
			name = name.replace(' II', ' 2')
			name = name.replace(' IV', ' 4')
			name = name.lower()
			data.append({'name': name, 'id': movie['id'], 'popularity': movie['popularity']})
		
	data.sort(key=pop_extract_time, reverse=True)

	print('Checking for duplicates, Please wait...')

	for ind, movie in enumerate(data):
		try:
			index = dataObj[movie['name']]['index']
			delete.append(ind)
		except:
			dataObj[movie['name']] = {'index': ind}

	delete.reverse()
	print('Deleting: ' + str(len(delete)))

	for d in delete:
		data.remove(data[d])

	print('Sorting movies by name')
	data.sort(key=extract_time)

	if os.path.isfile('./tmdb/movie_ids.json'):
		os.remove('./tmdb/movie_ids.json')
	for movie in data:
		writeToJSONFile('./tmdb', 'movie_ids', movie, 'a')

	data = []
	dataObj = {}
	delete = []

	for tv in tvIds:
		name = tv['original_name']
		name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode("ascii")
		name = re.sub("[\(\[].*?[\)\]]", "", name)
		name = re.sub("[:!$%\'\";,.&-]", "", name)
		if name and not name.startswith(" "):
			name = name.replace(' III', ' 3')
			name = name.replace(' II', ' 2')
			name = name.replace(' IV', ' 4')
			name = name.lower()
			data.append({'name': name, 'id': tv['id'], 'popularity': tv['popularity']})
		
	data.sort(key=pop_extract_time, reverse=True)

	print('Checking for duplicates, Please wait...')

	for ind, tv in enumerate(data):
		try:
			index = dataObj[tv['name']]['index']
			delete.append(ind)
		except:
			dataObj[tv['name']] = {'index': ind}

	delete.reverse()
	print('Deleting: ' + str(len(delete)))

	for d in delete:
		data.remove(data[d])

	print('Sorting tv series by name')
	data.sort(key=extract_time)

	if os.path.isfile('./tmdb/tv_series_ids.json'):
		os.remove('./tmdb/tv_series_ids.json')
	for tv in data:
		writeToJSONFile('./tmdb', 'tv_series_ids', tv, 'a')



#-------------------------------------------------------------------------------------------------------------------------------------------------
# Write data to json file

def writeToJSONFile(path, fileName, data, writeStatus):

	filePathNameWExt = './' + path + '/' + fileName + '.json'
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
			data[x] = {'id': movie['id'], 'popularity': movie['popularity']}

#-------------------------------------------------------------------------------------------------------------------------------------------------

main()