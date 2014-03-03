import os.path, sqlite3
import os, sys, re, socket, urllib, unicodedata, threading, urlparse
import xbmc, xbmcgui, xbmcaddon, xbmcvfs, xbmcplugin


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
 
xbmcplugin.setContent(addon_handle, 'movies')

__addon__     = xbmcaddon.Addon()
__addonid__   = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')
__language__  = __addon__.getLocalizedString


def displayEpisodeList(episodeList):
  for episode in episodeList:
    label = u"[%s] - S%02dE%02d - %s"%(episode['firstAired'], int(episode['season']), int(episode['episode']), episode['title'])
    print label
    li = xbmcgui.ListItem(label, iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=base_url, listitem=li, isFolder=False)
  xbmcplugin.endOfDirectory(addon_handle)

def getDatabaseFile():
  folder, files = xbmcvfs.listdir('special://database/')
  for file in files:
    if 'MyVideos' in file:
      return xbmc.translatePath('special://database/' + file)

def getLastEpisode(conn, idShow, season):
  episodeQuery = 'SELECT max(c13) FROM episodeview WHERE idShow = ? AND c12 = ?'
  cursor = conn.cursor()
  cursor.execute(episodeQuery, (idShow, season))
  return cursor.fetchone()[0]
  

def getTVShowList():
  tvshowQuery = 'SELECT idShow, strTitle, max(c12), c05 FROM episodeview GROUP BY strTitle ORDER BY strTitle'
  conn = sqlite3.connect(getDatabaseFile())
  cursor = conn.cursor()
  tvshows = cursor.execute(tvshowQuery)

  episodeList = []
  for tvshow in tvshows:
    episodeList.append({ 'title': tvshow[1], 'season': tvshow[2], 'firstAired': tvshow[3],
               'episode': getLastEpisode(conn, tvshow[0], tvshow[2]) })
  return episodeList
    
displayEpisodeList(getTVShowList())

