import urllib,urllib2,re,xbmcplugin,xbmcaddon,xbmcgui, sys, os, time, base64

__addonID__  = "plugin.video.tuxbox"
__settings__ = xbmcaddon.Addon(__addonID__)
ip = __settings__ .getSetting('ipaddress')
fetchepg = __settings__ .getSetting('epg')
smartepg = __settings__ .getSetting('smartepg')
username = __settings__ .getSetting('username')
password = __settings__ .getSetting('password')

# v0.0.6 by Lars Nordmeyer

base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')

class XBMCPlayer(xbmc.Player):
    def __init__( self, *args, **kwargs ):
        self.is_active = True
        print "#XBMCPlayer#"
    
    def onPlayBackPaused( self ):
        xbmc.log("#Im paused#")
        
    def onPlayBackResumed( self ):
        xbmc.log("#Im Resumed #")
        
    def onPlayBackStarted( self ):
        print "#Playback Started#"
        try:
            print "#Im playing :: " + self.getPlayingFile()
        except:
            print "#I failed get what Im playing#"
            
    def onPlayBackEnded( self ):
        print "#Playback Ended#"
        self.is_active = False
        
    def onPlayBackStopped( self ):
        print "## Playback Stopped ##"
        self.is_active = False
    
    def sleep(self, s):
        xbmc.sleep(s) 

def r_urlopen(req):
	req.add_header("Authorization", "Basic %s" % base64string)	
	try:
		response=urllib2.urlopen(req,None,5)
	except urllib2.URLError as e:
		print e.reason
		response=urllib2.urlopen(req,None,10)
		return response
	except urllib2.HTTPError:
		response=urllib2.urlopen(req,None,10)
		print "retry on HTTPError "+e.code
	return response

def CATEGORIES():
        addDir('','',1,'')
        addDir( '','',1,'')
                       
def INDEX(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = r_urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('').findall(link)
        for thumbnail,url,name in match:
                addDir(name,url,2,thumbnail)
                
def FETCHEPG(id):
	req = urllib2.Request("http://"+ip+"/control/epg?"+id)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = r_urlopen(req)
	link=response.read()
	response.close()
	match=re.compile("\d+\s(\d+)\s(\d+)\s(.+)\n").findall(link)
	#epg=match.match(link).groupdict()
	# "time.strftime("%H:%M",time.localtime(int(starttime)+int(duration)))+" "+epg+" "
	fullepg=""
	running_now=0
	for starttime,duration,epg in match:
		if time.time()>=(int(starttime)) and time.time()<=(int(starttime)+int(duration)):
			running_now=1
		if time.time()<=(int(starttime)+int(duration)) and running_now==1:
			if int(starttime)>(time.time()+5184000):
				break
			else:
				fullepg=fullepg+"| "+time.strftime("%H:%M",time.localtime(int(starttime)))+" "+epg+" "
	return fullepg

def VIDEOLINKS(url,mode):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = r_urlopen(req)
	link=response.read()
	response.close()
	if mode==1:
		match=re.compile("(\d+).(.*?)\n").findall(link)
		for no,service in match:
			url="http://"+ip+"/control/getbouquet?bouquet="+no+"&mode=TV"
        		addDir(service,url,mode,'')
	if mode==2:
		match=re.compile("(\d+).(.*?)\s(.*?)\n").findall(link)
		for no,id,service in match:
			#url="http://"+ip+"/control/getbouquet?bouquet="+no+"&mode=TV"
			url="http://"+ip+"/control/zapto?"+id
			epg=""
			if fetchepg=='true':
				epg=FETCHEPG(id)
				if epg=="" and smartepg=='true':
					req = urllib2.Request(url)
					req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
					response = r_urlopen(req)
					link=response.read()
					response.close()
					time.sleep(2)
					epg=FETCHEPG(id)		
        		addLink(service+" "+epg,url,'3',id,'')		
        
def LIVETV(url,name,id):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = r_urlopen(req)
	link=response.read()
	response.close()
	url="http://"+ip+"/control/build_live_url"
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = r_urlopen(req)
	link=response.read()
	response.close()
	#playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
	#playlist.clear()
	#playlist.add(link)
	#playlist.add(link)
	#nextitem=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=4"+"&id="+urllib.quote_plus(id)
	#playlist.add(nextitem)
	#xbmc.Player().play( playlist)
	player = XBMCPlayer(xbmc.PLAYER_CORE_MPLAYER)
        player.play(link)
        while player.is_active:
            player.sleep(100)
	#xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(link)
                       
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param




def addLink(name,url,mode,id,iconimage):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&id="+str(id)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	liz.setProperty('IsPlayable', 'false')
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
	return ok


def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
                     
params=get_params()
url=None
name=None
mode=None
id=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        id=urllib.unquote_plus(params["id"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "ID: "+str(id)

if mode==None or url==None or len(url)<1:
        print "http://"+ip+"/control/getbouquets"
        VIDEOLINKS("http://"+ip+"/control/getbouquets",1)
        #CATEGORIES()
       
elif mode==1:
        print ""+url
        VIDEOLINKS(url,2)
        #INDEX(url)

elif mode==2:
        print ""+url
        #INDEX(url)
        VIDEOLINKS(url,name)

elif mode==3:
	print ""+url
	LIVETV(url,name,id)
        #VIDEOLINKS(url,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
