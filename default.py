import sys, unicodedata, urlparse
import xbmc, xbmcgui, xbmcaddon, xbmcvfs, xbmcplugin, simplejson

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'tvshows')

addon = xbmcaddon.Addon('script.tv.show.last.episode')
path = xbmc.translatePath(addon.getAddonInfo('path'))

def jsonrpc(method, resultKey, params):
  query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "' + method + '", "params": ' + params + ', "id": 1}')
  result = simplejson.loads(unicode(query, 'utf-8', errors='ignore'))
  if result.has_key('result') and result['result'] != None and result['result'].has_key(resultKey):
    return result['result'][resultKey]
  else:
    return []

def display_episode_list(seriesList):
  for series in seriesList:
    episode = series['episode']
    label = u"S%sE%s - %s (%s, aired: %s, added: %s)"%(series['season'], series['number'], series['title'], episode['title'], episode['firstAired'], episode['dateAdded'][:10])
    li = xbmcgui.ListItem(label, iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=base_url, listitem=li, isFolder=False)
  xbmcplugin.endOfDirectory(addon_handle)

def get_tv_show_list():
  tvshows = jsonrpc('VideoLibrary.GetTVShows', 'tvshows', '{ "properties": ["title", "thumbnail"] }, "id": "libTvShows"}')
  result = []
  for tvshow in tvshows:
    episodes = jsonrpc(
      'VideoLibrary.GetEpisodes',
      'episodes',
      '{"tvshowid": %d, "properties": ["title", "season", "episode", "thumbnail"], "sort": {"order": "descending", "method": "season"}, "limits": {"start": 1, "end": 1}}'%tvshow['tvshowid']
    )
    episode = episodes[0]
    result.append({
      'title': tvshow['title'],
      'season': ("%.2d" % float(episode['season'])),
      'episode': {
        'number': ("%.2d" % float(episode['episode'])),
        'title': episode['title'],
        'firstAired': '2014-01-02',
        'dateAdded': '2014-02-03'
      }
    })
  return result

def display_sort_order_selection():
  fanart = addon.getAddonInfo('fanart')

  firstAired = xbmcgui.ListItem(addon.getLocalizedString(32001), iconImage=xbmc.translatePath(path + '/resources/media/calendar.png'))
  firstAired.setProperty('fanart_image', fanart)
  xbmcplugin.addDirectoryItem(
    handle=addon_handle,
    url=base_url + '?order=firstAired',
    listitem=firstAired, 
    isFolder=True
  )

  seriesTitle = xbmcgui.ListItem(addon.getLocalizedString(32002), iconImage=xbmc.translatePath(path + '/resources/media/keyboard.png'))
  seriesTitle.setProperty('fanart_image', fanart)
  xbmcplugin.addDirectoryItem(
    handle=addon_handle,
    url=base_url + '?order=seriesTitle',
    listitem=seriesTitle, 
    isFolder=True
  )

  dateAdded = xbmcgui.ListItem(addon.getLocalizedString(32003), iconImage=xbmc.translatePath(path + '/resources/media/plus-circle.png'))
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

print 'before call'
print get_tv_show_list()
print 'after call'
