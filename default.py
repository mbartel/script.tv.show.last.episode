import sqlite3
import sys, unicodedata, urlparse
import xbmc, xbmcgui, xbmcaddon, xbmcvfs, xbmcplugin

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'tvshows')

addon = xbmcaddon.Addon('script.tv.show.last.episode')
path = addon.getAddonInfo('path')

def display_episode_list(seriesList):
  for series in seriesList:
    episode = series['episode']
    label = u"S%02dE%02d - %s (%s, aired: %s, added: %s)"%(int(series['season']), int(episode['number']), series['title'], episode['title'], episode['firstAired'], episode['dateAdded'][:10])
    li = xbmcgui.ListItem(label, iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=base_url, listitem=li, isFolder=False)
  xbmcplugin.endOfDirectory(addon_handle)

def get_database_file():
  folder, files = xbmcvfs.listdir('special://database/')
  for file in files:
    if 'MyVideos' in file:
      return xbmc.translatePath('special://database/' + file)

def get_last_episode(conn, idShow, season):
  episodeQuery = 'SELECT MAX(CAST(c13 AS INTEGER)), c00, c05, dateAdded FROM episodeview WHERE idShow = ? AND c12 = ?'
  cursor = conn.cursor()
  cursor.execute(episodeQuery, (idShow, season))
  episode = cursor.fetchone()
  return { 'number': episode[0], 'title': episode[1], 'firstAired': episode[2], 'dateAdded': episode[3] }


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
  fanart = addon.getAddonInfo('fanart')

  firstAired = xbmcgui.ListItem('Sort by first aired date', iconImage=path + '/resources/media/calendar.png')
  firstAired.setProperty('fanart_image', fanart)
  xbmcplugin.addDirectoryItem(
    handle=addon_handle,
    url=base_url + '?order=firstAired',
    listitem=firstAired, 
    isFolder=True
  )

  seriesTitle = xbmcgui.ListItem('Sort by TV show title', iconImage=path + '/resources/media/keyboard.png')
  seriesTitle.setProperty('fanart_image', fanart)
  xbmcplugin.addDirectoryItem(
    handle=addon_handle,
    url=base_url + '?order=seriesTitle',
    listitem=seriesTitle, 
    isFolder=True
  )

  dateAdded = xbmcgui.ListItem('Sort by added to library date', iconImage=path + '/resources/media/plus-circle.png')
  dateAdded.setProperty('fanart_image', fanart)
  xbmcplugin.addDirectoryItem(
    handle=addon_handle,
    url=base_url + '?order=dateAdded',
    listitem=dateAdded, 
    isFolder=True
  )
  xbmcplugin.endOfDirectory(addon_handle)

# check settings
if args:
  order = args['order'][0]
else:
  order = None
  addOnSetting = addon.getSetting('sortOrder')
  if addOnSetting == '1':
    order = 'seriesTitle'
  if addOnSetting == '2':
    order = 'firstAired'
  if addOnSetting == '3':
    order = 'dateAdded'

# sort tv show list
if order:
  unsortedEpisodeList = get_tv_show_list()
  if order in 'seriesTitle':
    sortedEpisodeList = sorted(unsortedEpisodeList, key=lambda x: x['title'])
  if order in 'firstAired':
    sortedEpisodeList = sorted(unsortedEpisodeList, key=lambda x: x['episode']['firstAired'], reverse=True)
  if order in 'dateAdded':
    sortedEpisodeList = sorted(unsortedEpisodeList, key=lambda x: x['episode']['dateAdded'], reverse=True)
  display_episode_list(sortedEpisodeList)
else:
  display_sort_order_selection()

