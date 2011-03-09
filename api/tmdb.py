#!/usr/bin/env python
import json
import sys
import re

from urllib2 import urlopen, HTTPError
from urllib import quote_plus
from datetime import datetime

import data
from sqlobject import SQLObjectNotFound

class APIBase():
    lang = 'en'
    
    def __init__(self):
        pass
    
    def _hasLeadingSlash(self, term):
        if len(term) > 0:
            try:
                term.index('/')
            except ValueError:
                return False
            else:
                return True
        else:
            return True
        
    def makeURL(self, path, term=''):
        if not self._hasLeadingSlash(term):
            term = '/%s' % term
        
        self.url = "%(proto)s://%(host)s%(path)s%(term)s" % \
                    {'proto': self.protocol,
                     'host': self.host,
                     'path': path,
                     'term': term}
            
    def getResponse(self):
        if not self.url:
            raise APIError('No defined URL to access')
        
        try:
            self.server_response = urlopen(self.url)
        except HTTPError:
            raise APIError("Couldn't open %s for reading" % self.url)

        self._server_msg = self._server_response.msg
        
        if "OK" not in self._server_msg:
            raise APIError("Server responded with something I can't handle.")
        else:
            self._response_data = self._server_response.read()

class TMDB(APIBase):
    self.output = output
    self.path_format = '/%(version)s/%(api)s/%(lang)s/%(output)s/%(apikey)s'
    self.apikey = '32143db63692aa6a5cb01336cc06211b'
    self.protocol = 'http'
    self.host = 'api.themoviedb.org'
    self.version = '2.1'
    self.output = 'json'
    self.api = 'tmdb'
    
    def getAPIMethod(self, domain, method):
        calledAPI = "%s.%s" % (domain.capitalize(), method)
        return calledAPI
    
    def pathParams(self):
        return {'version': self.version, 
                'api': self.api_method,
                'lang': self.lang,
                'output': self.output,
                'apikey': self.apikey,}

    def lookup(self, search_term, domain = 'movie'):
        self.domain = domain        
        if isinstance(search_term, str):
            if re.search(self.imdb_id_pattern, search_term):
                self.method = 'imdbLookup'
            else:
                self.method = 'search'
        else:
            self.method = 'getInfo'
            
        self.api_method = self.getAPIMethod(self.domain, self.method)
        path = self.path_format % self.pathParams()
        self.makeURL(path, search_term)
        self.getResponse()
        
        movies = self.parseResponse(method)

        if method == 'search' and domain == 'movie':
            for movie in movies:
                self.lookup(movie.)

        
        if two_pass:
            movie_ids = self.parseResponse(method)
            for mid in movie_ids:
                
                
                    

    
                     

class TMDB():
    token = ''
    connection = None

    def __init__(self, apikey = '', output = 'json'):
        if apikey:
            self.apikey = apikey
        
        self.urls = TMDBUrls()
        
        connection = connect()
        
    def getMovieInfoByName(self, name):
        this_id = self.getMovieIDByName(name)
        return self.getMovieInfoByTMDB_ID(this_id)

    def getMovieIDByName(self, name):
        self.domain = 'movie'
        self.action = 'search'
        self.searchTerm = quote_plus(name)
        
        try:
            movie_list = Movie.select("""movie.title LIKE '%s'""" % name)
            if movie_list.count() == 1:
                self.tmdb_id = movie_list[0].tmdb_id
            else:
                raise SQLObjectNotFound
        except SQLObjectNotFound:
            self.url = "%s/%s" % (self.urls.generateURL(self.domain, self.action), self.searchTerm)

            movie_info = self._getResponse(self.url)[0]
            self.tmdb_id = movie_info['id']
        
        return self.tmdb_id
        
    def genreCount(self):
        return len(list(Genre.select()))
        
    def getMovieInfoByTMDB_ID(self, tmdb_id=''):
        self.domain = 'movie'
        self.action = 'getInfo'
        if tmdb_id:
            self.tmdb_id = tmdb_id
        
        try:    
            movie_list = Movie.select(Movie.q.tmdb_id==self.tmdb_id)
            if movie_list.count() == 1:
                oMovie = movie_list[0]
            elif movie_list.count() == 0:
                raise SQLObjectNotFound
            else:
                raise AttributeError
        except SQLObjectNotFound:
        
            self.url = "%s/%s" % (self.urls.generateURL(self.domain, self.action), self.tmdb_id)        
            self.movie_info = self._getResponse(self.url)[0]
                    
            oMovie = Movie(tmdb_id = self._getKey('id', 0),
                           imdb_id = self._getKey('imdb_id', ''),
                           title = self._getKey('name', ''),
                           year = int(self._getYearFromDate(self._getKey('released', ''))),
                           mpaa = Movie.ratings.index(self._getKey('certification', 'NR')),
                           director = self._getDirector(self._getKey('cast', [])),
                           actors = self._getPrimaryActors(self._getKey('cast', [])),
                           description = self._getKey('overview', ''),
                           length = int(self._getKey('runtime', 0)),
                           poster_remote_URI = self._getPosterURL(self._getKey('posters', '')),
                           )

            for genre in self._getGenres(self._getKey('genres', '')):
                oMovie.addGenre(genre)
        
        return oMovie
        
    def _getYearFromDate(self, dateStr):
        if '-' in dateStr:
            return dateStr.split('-')[0]
        else:
            return datetime.now().year
        
    def _getKey(self, key, default):
        try:
            value = self.movie_info[key]
        
            if value == None or value == '':
                return default
            else:
                return value
        except KeyError:
            return default
            
        
    def _getPosterURL(self, posterDict):
        for poster in posterDict:
            try:
                if poster['image']['size'] == "cover":
                    return poster['image']['url']
            except KeyError:
                if poster['image']['size'] == 'mid':
                    return poster['image']['url']
        
        return ''
                    
    
    def _getGenres(self, genreDict):
        self.genres = []
        for genre in genreDict:
            try:
                self.genres.append(Genre.byTmdb_id(int(genre['id'])))
            except KeyError:
                pass
        
        return self.genres

    
    def populateGenres(self):
        self.domain = 'genres'
        self.action = 'getList'
        self.url = self.urls.generateURL(self.domain, self.action)
        self.genre_info = self._getResponse(self.url)
        
        for genre in self.genre_info:
            try:
                g = Genre(name=genre['name'], tmdb_id=int(genre['id']))
            except KeyError:
                pass
        
        
    
    def _getDirector(self, castDict):
        for member in castDict:
            try:
                if member['job'] == 'Director':
                    return member['name']
            except KeyError:
                return ''

    
    def _getPrimaryActors(self, castDict):
        actors = []
        for member in castDict:
            try:
                if member['job'] == 'Actor':
                    actors.append(member['name'])
            except KeyError:
                pass
        return '     '.join(actors[:3])

class APIError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)    

        
if __name__ == '__main__':
    connect()
    t = TMDB()
    this_id = t.getMovieIDByName('Aliens')
    print "ID: ", this_id
    this_movie = t.getMovieInfoByTMDB_ID(this_id)
    print this_movie.toxml()
    
    