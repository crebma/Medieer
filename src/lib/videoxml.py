#!/usr/bin/env python
# This file is part of Medieer.
# 
#     Medieer is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     Medieer is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

from lxml import etree
from sqlobject import SQLObjectNotFound

# TODO: SWITCH TO BEAUTIFULSOUP IF POSSIBLE
# TODO: CHANGE TO GENERATORS
# TODO: ONE CLASS PER OUTPUT TYPE
# TODO: ADD DATA ABOUT HOW OUTPUT WORKS - SINGLE FILE, MULTIPLE FILE

class VideoXML():
    SINGLE_FILE = 0
    MULTIPLE_FILES = 1
    output_types = ['single file', 'multiple files']
    
    def __init__(self, log):
        self.log = log
       
    def format_title(self, title, episode, media_type):
        self.log.debug("Media type: %s" % media_type)
        if media_type == 'TV':
            self.log.debug('TV Show, adding Episode number')
            return 'Episode %02d: %s' % (episode, title)
        else:
            self.log.debug('Movie, leaving title')
            return title

    def toxml(self, pretty=False):
        return etree.tostring(self.xml, encoding='UTF-8', xml_declaration=False)
        
    def makeVideoXML(self, video):
        self.xml = etree.Element('video')
        
        title = etree.SubElement(self.xml, 'title')
        title.text = self.format_title(video.title, video.episode_number, video.media_type)

        year = etree.SubElement(self.xml, 'year')
        year.text = str(video.released.year)

        genre = etree.SubElement(self.xml, 'genre')
        genre.text = video.listGenres(prepend_media_type=False)[0]

        mpaa = etree.SubElement(self.xml, 'mpaa')
        mpaa.text = video.rating

        director = etree.SubElement(self.xml, 'director')
        try:
            director.text = video.director.name
        except SQLObjectNotFound:
            director.text = ''

        actors = etree.SubElement(self.xml, 'actors')
        actors.text = '     '.join(video.listActors()[:3])

        description = etree.SubElement(self.xml, 'description')
        description.text = video.description

        length = etree.SubElement(self.xml, 'length')
        length.text = str(video.runtime)
        
    
    def makeVideoDirectory(self, media):
        self.xml = etree.Element('xml')
        self.viddb = etree.SubElement(self.xml, 'viddb')
        for video in media:
            self.addVideo(video)
            
    def addVideo(self, video):
        movie = etree.SubElement(self.viddb, 'movie')
        
        origtitle = etree.SubElement(movie, 'origtitle')
        origtitle = self.format_title(video.title, video.episode_number, video.media_type)
        
        year = etree.SubElement(movie, 'year')
        year.text = str(video.released.year)
        
        genre = etree.SubElement(movie, 'genre')
        genre.text = ','.join(video.listGenres())
        
        mpaa = etree.SubElement(movie, 'mpaa')
        mpaa.text = 'Rated %s' % video.rating
        
        director = etree.SubElement(movie, 'director')
        try:
            director.text = video.director.name
        except SQLObjectNotFound:
            director.text = ''
        
        actors = etree.SubElement(movie, 'actors')
        actors.text = '     '.join(video.listActors()[:3])
        
        description = etree.SubElement(movie, 'description')
        description.text = video.description
        
        path = etree.SubElement(movie, 'path')
        path.text = video.file_URI
        
        length = etree.SubElement(movie, 'length')
        length.text = str(video.runtime)
        
        videocodec = etree.SubElement(movie, 'videocodec')
        videocodec.text = video.codec
        
        poster = etree.SubElement(movie, 'poster')
        poster.text = video.poster_local_URI

        return movie