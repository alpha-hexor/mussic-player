import httpx
import re
import random
import base64
from urllib.parse import quote

#common stuff
common_yt_variables:dict = {
    'yt_client_version' : '1.20240923.01.01-canary_experiment_1.20240918.01.00',
    'yt_client_name' : '67',
    'yt-bootstrap' : "false",
    'android_yt_ver' : '7.08.53'
}

common_headers:dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "X-Youtube-Bootstrap-Logged-In" : common_yt_variables['yt-bootstrap'],
    "X-Youtube-Client-Name" : common_yt_variables["yt_client_name"],
    "X-Youtube-Client-Version" : common_yt_variables["yt_client_version"]
}

common_client:dict = {
    "client":{
        "hl":"en",
        "deviceMake":"",
        "deviceModel":"",
        "userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0,gzip(gfe)",
        "clientName":"WEB_REMIX",
        "clientVersion":common_yt_variables["yt_client_version"],
        "osName":"Windows",
        "osVersion":"10.0",
        "screenPixelDensity":2,
        "platform":"DESKTOP",
        "clientFormFactor":"UNKNOWN_FORM_FACTOR",
        "screenDensityFloat":1.5,
        "userInterfaceTheme":"USER_INTERFACE_THEME_DARK",
        "browserName":"Firefox",
        "browserVersion":"130.0",
        "acceptHeader":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "musicAppInfo" : {
            "webDisplayMode":"WEB_DISPLAY_MODE_BROWSER",
            "storeDigitalGoodsApiSupportStatus":{
                "playStoreDigitalGoodsApiSupportStatus":"DIGITAL_GOODS_API_SUPPORT_STATUS_UNSUPPORTED"
                
            }
        }
    }
}

class Music:
    def __init__(self):
        self.base_url = "https://music.youtube.com"
        
    def search_music(self,query:str)->str:
        """
        function to search music

        args:
            query:str -> music search query
        
        return: 
            music_video_url -> audio url
        """
        data = {}
        #http headers
        search_headers = common_headers
        
        search_headers['Referer'] = f"{self.base_url}/"
        
        search_headers['Origin'] = f"{self.base_url}"

        #post request data
        client_data = common_client
        
        client_data["originalUrl"] = f"{self.base_url}/"

        client_data["client"]["musicAppInfo"]["pwaInstallabilityStatus"]="PWA_INSTALLABILITY_STATUS_UNKNOWN"

        r=httpx.post(
            f"{self.base_url}/youtubei/v1/search?prettyPrint=false",
            json={
                "context" : client_data,
                "query" : f"{query} lyric",
                
            }
        )

        search_query_data =  re.findall(r'"text":"Songs".+?"videoId":"(.*?)".+?"Play (.*?)"',r.text)[0]

        video_id , song_name = search_query_data

        #audio_url = self.get_audio_url(video_id=video_id)

        data  = {
            'video_id' : video_id,
            'title' : song_name,
            'thumbnail' : f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
        }
        return data
    
    def get_audio_url(self,video_id:str)->str:
        """
        function to extract high quality music url 

        args:
            video_id:str -> youtube music video_id

        return:
            audio_url:str -> high quality audio url
        """

        random_num:int = random.randint(0,4)
        extra_up:int = 1 if random_num > 1 else 0

        android_user_agent:str = f"com.google.android.apps.youtube.music/{common_yt_variables['android_yt_ver']} (Linux; U; Android 1{random_num}) gzip"

        #post data
        audio_url_payload:dict = {
            "context":{
                "client":{
                    "clientName" : "ANDROID_MUSIC",
                    "clientVersion": common_yt_variables["android_yt_ver"],
                    "androidSdkVersion": f"{random_num+extra_up+29}",
                    "userAgent" : android_user_agent,
                    "hl":"en",
                    "timeZone": "UTC",
                    "utcOffsetMinutes":0
                }
            },

            "videoId" : video_id,
            "playbackContext":{
                "contentPlaybackContext" :{
                    "html5Preference" : "HTML5_PREF_WANTS"
                }
            },

            "contentCheckOk" :True,
            "racyCheckOk" : True
        }

        r = httpx.post(
            f"{self.base_url}/youtubei/v1/player?key=AIzaSyAOghZGza2MQSZkY_zfZ370N-PUdXEo8AI&prettyPrint=false",
            headers={
                'User-Agent' : android_user_agent,
                "Referer": self.base_url
            },
            json=audio_url_payload
        )
        audio_url:str = re.findall(r'"itag":140,"url":"(.*?)"',r.text)[0]

        return audio_url
    
    def get_lyrics(self,video_id:str)->str|None:
        """
        function to return lyrics of a song if possibe else None

        args:
            video_id:str -> video id
        
        return:
            lyrics:str | None -> lyrics
        """

        youtube_link:str = f"{self.base_url}/watch?v={video_id}"

        #lyrics headers
        lyric_headers:dict = common_headers
        lyric_headers['Referer'] = youtube_link
        lyric_headers['Origin'] = self.base_url

        #webid 
        web_id_payload:dict = common_client
        web_id_payload['originalUrl'] = youtube_link

        r = httpx.post(
            f"{self.base_url}/youtubei/v1/next?prettyPrint=false",
            headers=lyric_headers,
            json={
                "enablePersistentPlaylistPanel":True,
                "tunerSettingValue":"AUTOMIX_SETTING_NORMAL",
                "videoId":video_id,
                "isAudioOnly":True,
                "responsiveSignals":{"videoInteraction":[]},
                "queueContextParams":"",
                "context":web_id_payload
            }
        )

        try:
            webid = re.findall(r'{"browseId":"(MPLYt_.*?)"',r.text)[0]
           
        except IndexError:
            raise IndexError("[-]Failed to get web id from request")
        
        #lyric data
        lyric_payload = common_client
        lyric_payload["client"]["musicAppInfo"]["pwaInstallabilityStatus"] = "PWA_INSTALLABILITY_STATUS_UNKNOWN"

        r = httpx.post(
            f"{self.base_url}/youtubei/v1/browse?prettyPrint=false",
            headers=lyric_headers,
            json={
                "context" : lyric_payload,
                "browseId" : webid
            }
        )

        try:
            lyrics = re.findall(r'\"musicDescriptionShelfRenderer\".+?\"text\":\"([\s\S]*)\"}\]},',r.text)[0]

        except IndexError:
            lyrics= None
        
        return lyrics

    def next_song(self,video_id:str)->list:
        """
        function to return next 7 recommended song

        args:
            video_id:str -> video id
        
        return:
            next_songs:list -> [(song name,artist name,video id)]
        """
        yt_link:str = f"{self.base_url}/watch?v={video_id}"

        #next song headers
        next_headers:dict = common_headers
        next_headers["Referer"] = yt_link
        next_headers["Origin"] = self.base_url

        #next song payload
        next_song_paylaod = common_client
        next_song_paylaod["originalUrl"] = yt_link
        next_song_paylaod["client"]["musicAppInfo"]["pwaInstallabilityStatus"] = "PWA_INSTALLABILITY_STATUS_UNKNOWN"
        
        #generate 'params' for payload
        slug = b'\xc0\x01\x01\xf2\x01\x02x\x01\xea\x04\x0b'
        raw_param = slug + video_id.encode()
        raw_param = base64.b64encode(raw_param).decode()
        param = quote(raw_param)

        r=httpx.post(
            f"{self.base_url}/youtubei/v1/next?prettyPrint=false",
            headers=next_headers,
            json={
                "enablePersistentPlaylistPanel":True,
                "tunerSettingValue":"AUTOMIX_SETTING_NORMAL",
                "playlistId":f"RDAMVM{video_id}",
                "params" : param,
                "isAudioOnly":True,
                "responsiveSignals":{
                    "videoInteraction":[
                        {
                            "queueImpress":{},
                            "videoId":video_id,
                            "queueIndex":0
                        }
                    ]
                },
                "context" : next_song_paylaod
            }
        )

        next_songs = re.findall(r'playlistPanelVideoRenderer":.+?"text":"(.*?)".+?"text":"(.*?)".+?"videoId":"(.*?)"',r.text)

        if len(next_songs) <= 7:
            return next_songs
        else:
            return next_songs[:13]