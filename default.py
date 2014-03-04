import sqlite3
import sys, unicodedata, urlparse
import xbmc, xbmcgui, xbmcaddon, xbmcvfs, xbmcplugin

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

# files, songs, artists, albums, movies, tvshows, episodes, musicvideos
xbmcplugin.setContent(addon_handle, 'tvshows')

__addon__     = xbmcaddon.Addon()
__addonid__   = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__author__    = __addon__.getAddonInfo('author')
__version__   = __addon__.getAddonInfo('version')
__language__  = __addon__.getLocalizedString


def display_episode_list(seriesList):
  for series in seriesList:
    episode = series['episode']
    label = u"S%02dE%02d - %s (%s, %s)"%(int(series['season']), int(episode['number']), series['title'], episode['title'], episode['firstAired'])
    li = xbmcgui.ListItem(label, iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=base_url, listitem=li, isFolder=False)
  xbmcplugin.endOfDirectory(addon_handle)

def get_database_file():
  folder, files = xbmcvfs.listdir('special://database/')
  for file in files:
    if 'MyVideos' in file:
      return xbmc.translatePath('special://database/' + file)

def get_last_episode(conn, idShow, season):
  episodeQuery = 'SELECT MAX(CAST(c13 AS INTEGER)), c00, c05 FROM episodeview WHERE idShow = ? AND c12 = ?'
  cursor = conn.cursor()
  cursor.execute(episodeQuery, (idShow, season))
  episode = cursor.fetchone()
  return { 'number': episode[0], 'title': episode[1], 'firstAired': episode[2] }


def get_tv_show_list():
  tvshowQuery = 'SELECT idShow, strTitle, MAX(CAST(c12 AS INTEGER)) FROM episodeview GROUP BY idShow'
  conn = sqlite3.connect(get_database_file())
  cursor = conn.cursor()
  tvshows = cursor.execute(tvshowQuery)

  episodeList = []
  for tvshow in tvshows:
    episodeList.append({ 'title': tvshow[1], 'season': tvshow[2], 'episode': get_last_episode(conn, tvshow[0], tvshow[2]) })
  return episodeList

def display_sort_order_selection():
  xbmcplugin.addDirectoryItem(
    handle=addon_handle,
    url=base_url + '?order=firstAired',
    listitem=xbmcgui.ListItem('Sort by first aired date', iconImage='DefaultFolder.png'), 
    isFolder=True
  )
  xbmcplugin.addDirectoryItem(
    handle=addon_handle,
    url=base_url + '?order=seriesTitle',
    listitem=xbmcgui.ListItem('Sort by TV show title', iconImage='DefaultFolder.png'), 
    isFolder=True
  )
  xbmcplugin.endOfDirectory(addon_handle)

if args:
  order = args['order'][0]
  unsortedEpisodeList = get_tv_show_list()
  if order in 'seriesTitle':
    sortedEpisodeList = sorted(unsortedEpisodeList, key=lambda x: x['title'])
  if order in 'firstAired':
    sortedEpisodeList = sorted(unsortedEpisodeList, key=lambda x: x['episode']['firstAired'], reverse=True)
  display_episode_list(sortedEpisodeList)
else:
  display_sort_order_selection()

