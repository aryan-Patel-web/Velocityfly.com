"""
pixabay_final_ultimate_v5.py - COMPLETE ULTIMATE VERSION
===========================================================
✅ Dynamic image handling (both horizontal & vertical)
✅ 8 Deities with unique stories & music
✅ Anti-repetition system (script hashing)
✅ God-specific background music
✅ 5 Professional transitions
✅ HD thumbnails with golden text overlay
✅ Live word-by-word captions
✅ 1.15x voice narration speed
✅ Bhagavad Gita verse automation
✅ Custom duration (20-55s)
===========================================================
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import asyncio
import logging
import os
import traceback
import uuid
import httpx
import json
import re
import random
import subprocess
from typing import List, Dict, Optional
import tempfile
import shutil
import gc
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "54364709-1e6532279f08847859d5bea5e")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# PROCESSING LIMITS
FFMPEG_TIMEOUT_CLIP = 180
FFMPEG_TIMEOUT_CONCAT = 300
FFMPEG_TIMEOUT_SUBTITLE = 360
FFMPEG_TIMEOUT_MUSIC = 120

# IMAGE CONFIG - DYNAMIC
MIN_IMAGES = 8
MAX_IMAGES = 18
IMAGE_TARGET_WIDTH = 720
IMAGE_TARGET_HEIGHT = 1280
FPS = 30

# THUMBNAIL: 200KB - 2MB with golden overlay
THUMBNAIL_MIN_SIZE_KB =200
THUMBNAIL_MAX_SIZE_KB = 2048

# ============================================================================
# SPIRITUAL DEITIES - 8 GODS WITH UNIQUE STORIES
# ============================================================================

DEITY_STORIES = {
    "krishna": [
        "Krishna ka janam Mathura ki kaalgari mein hua. Kansa ne sabhi bachon ko maarne ka plan banaya kyunki bhavishyavani thi ki aathva beta uski maut banega. Jab Krishna paida hue, divya shakti ne prahariyon ko sula diya. Vasudeva basket mein Krishna ko lekar Yamuna paar karne lage. Yamuna ne apna paani khud neeche kar diya aur Shesh Naag ne phano se suraksha di. Krishna Gokul mein Yashoda ke paas pohonche aur unhone Krishna ko apna beta maan liya.",
        
        "Krishna ka makhan churana bahut prasiddh hai. Yashoda makhan oonchai par rakhti thi lekin Krishna apne sakhao ke saath mil kar ladder bana lete the aur makhan nikal lete the. Ek din Yashoda ne Krishna ko pakad liya aur mukh kholne ko kaha. Jab Krishna ne mukh khola, tab Yashoda ne Krishna ke mukh mein pura brahmaand dekha - suraj, chaand, taare, prithvi, swarg, narak sab kuch. Yashoda samajh gayi ki Krishna koi saadharan balak nahi hai.",
        
        "Govardhan Parvat uthana Krishna ki sabse badi leela hai. Vrindavan ke log Indra Dev ki pooja karte the aur baarish ke liye unhe khush karte the. Krishna ne logo ko samjhaya ki Govardhan Parvat hi asli rakshak hai jo unhe sab kuch deta hai. Logo ne Indra ki jagah Govardhan ki pooja ki. Gusse mein Indra ne saat din tak lagatar bhaari baarish ki. Tab Krishna ne apni chhoti ungli par pura Govardhan Parvat utha liya aur sab logo ko neeche suraksha di. Indra ko apni galti ka ehsaas hua.",
        
        "Kurukshetra yudh se pehle Arjun ne apne hi parivaar ke khilaf ladne se mana kar diya. Unka mann bahut vyakul tha. Tab Krishna ne Arjun ko Bhagavad Gita ka updesh diya. Karmanye Vadhikaraste Ma Phaleshu Kadachana - tumhara adhikar sirf karma par hai, phal par nahi. Krishna ne Arjun ko Vishwaroop bhi dikhaya jismein pura brahmaand samaya hua tha. Arjun ko apne kartavya ka bodh hua aur unhone yudh kiya."
    ],
    
    "mahadev": [
        "Samudra Manthan mein jab Devta aur Asur amrit ke liye Ksheer Sagar ka manthan kar rahe the, tab sabse pehle halahal vish nikla. Yeh vish itna khatarnak tha ki puri srishti ko nash kar sakta tha. Sab Mahadev ke paas gaye madad ke liye. Mahadev ne srishti ki raksha ke liye vish ko pee liya. Lekin unhone vish ko nigala nahi, gale mein hi rok liya. Vish ki garmi se unka gala neela pad gaya aur unka naam pada Neelkanth. Parvati ne gale par haath rakha jisse vish aur fail nahi paaya.",
        
        "Parvati ne Shiva ko pati ke roop mein paane ke liye ghori tapasya ki. Unhone barfili pahadiyon mein, garmi mein, baarish mein tapasya ki bina kuch khaye piye. Shiva ne pariksha lene ke liye ek budhe brahman ka roop dhaaran kiya aur Parvati se kaha ki Shiva toh ek aisi vyakti hai jo shamshaan mein rehta hai aur bholenath hai. Lekin Parvati ne gusse mein us brahman ko daanta aur kaha ki unhe Shiva ke alawa koi nahi chahiye. Tab Shiva prakat hue aur Parvati se vivah kiya.",
        
        "Ganga avataran mein Raja Bhagirath ne bahut ghori tapasya ki taaki Ganga prithvi par utare aur unke purvajon ko mukti mile. Brahma ji ne tapasya se khush hokar kaha ki Ganga utaregi. Lekin Ganga ka veg itna tez tha ki prithvi ko barbad kar sakta tha. Bhagirath ne phir Mahadev ki tapasya ki. Mahadev ne Ganga ko apni jataon mein rok liya aur saat dharaon mein pravahit kar diya jisse prithvi surakshit rahi aur Ganga bhi dharti par aayi.",
        
        "Tandav nritya Mahadev ka sabse shakti"
    ],
    
    "ganesha": [
        "Ganesha ka janam bahut adbhut tareeke se hua. Ek din Parvati Maa ne snan karne se pehle apne shareer ki mitti se ek sundar balak ki murti banayi aur use jeevan daan diya. Unhone use darwaze par pahara dene ko kaha. Jab Shiva aayen tab Ganesha ne unhe rokne ki koshish ki kyunki wo Shiva ko nahi jaante the. Gusse mein Shiva ne Ganesha ka sir kaat diya. Jab Parvati ko pata chala tab wo bahut dukhi hui. Tab Shiva ne hasthi ka sir laga kar Ganesha ko dobara jeevan diya.",
        
        "Ek baar Ganesha aur Kartikeya mein yeh bahas hui ki kon adhik buddhimaan hai. Tab Shiva aur Parvati ne kaha ki jo pehle teen baar prithvi ka chakkar lagayega wohi jeetega. Kartikeya apne mayur par baith kar udne lage. Lekin Ganesha ne buddhimani se apne mata pita ke teen chakkar lagaye aur kaha ki unke liye mata pita hi puri duniya hai. Shiv-Parvati bahut khush hue aur Ganesha ko Pratham Pujya ghoshit kar diya.",
        
        "Ganesha ka ek daant toota hai jiska ek rochak katha hai. Ek baar Parashurama Kailash par Shiva se milne aaye lekin Shiva dhyan mein the. Ganesha ne Parashurama ko roka. Gusse mein Parashurama ne apna parshu Ganesha par phenka. Ganesha ne us parshu ko apne daant se rok liya kyunki wo parshu Shiva ka diya hua tha. Ganesha ka ek daant toot gaya aur tab se wo Ekdant kehlaye.",
        
        "Vyasa ji Mahabharat likhna chahte the lekin unhe ek aisa lekhak chahiye tha jo bina ruke likh sake. Tab Brahma ji ne Ganesha ko bulaya. Ganesha ne kaha ki wo likhenge lekin Vyasa ji ko bina ruke bolna hoga aur agar wo galat bole toh Ganesha likhna band kar denge. Is chunauti ko sweekaar kar dono ne Mahabharat ki rachna ki jo aaj bhi duniya ki sabse badi kavita hai."
    ],
    
    "hanuman": [
        "Hanuman ka janam Anjana aur Kesari ke ghar hua. Bachpan mein ek baar bhookhe Hanuman ne suraj ko phal samajh kar khane ki koshish ki. Jab Indra ne Hanuman par vajra chalaaya tab Hanuman ki thodi toot gayi aur wo behosh ho gaye. Pawan dev bahut gusse mein aa gaye aur hawa band kar di. Sab devtaon ne Hanuman ko vardaan diya ki unhe koi astra-shastra maar nahi sakta aur wo ajanma rahenge.",
        
        "Jab Ram Sita ki khoj mein jungle mein the tab Hanuman unse mile. Sugriva ne Hanuman ko Ram ke paas bheja tha. Hanuman ne Ram ke charan sparsh kiye aur unhone apni poori shakti Ram ki seva mein laga di. Ram ne Hanuman ko apna sabse priya bhakt maan liya. Hanuman ne Ram ke liye Sugriva se dosti karwaayi aur unhe Vaali se ladne mein madad ki.",
        
        "Lanka mein Sita Maa ki khoj mein Hanuman ne samudra paar kiya. Jab wo Lanka pohonche tab unhone dekha ki Sita Ashok Vatika mein baithi hai aur bahut dukhi hai. Hanuman ne Sita ko Ram ki mudrika di jisse unhe vishwas hua ki Ram jald hi aayenge. Hanuman ne Ravana ke darbaar mein jakar bahut hungama machaya. Ravana ne Hanuman ki poonch mein aag laga di lekin Hanuman ne poori Lanka jala di.",
        
        "Lakshman ke ghayal hone par vaidya ne kaha ki sirf Sanjeevani booti se Lakshman bach sakte hai jo Dronagiri parvat par milti hai. Hanuman turant udkar parvat par pohonche lekin unhe booti pehchaan nahi aayi. Tab unhone pura Dronagiri parvat hi utha liya aur Lanka le aaye. Vaidya ne booti se Lakshman ka upchaar kiya aur wo theek ho gaye. Hanuman ki is mahaan shakti ko dekhkar sab hairaan rah gaye."
    ],
    
    "ram": [
        "Ram ka janam Ayodhya mein Raja Dasharath aur Rani Kaushalya ke yahan hua. Chaaron bhai - Ram, Lakshman, Bharat aur Shatrughan bahut hi gun-sampann the. Ram sabse bade the aur sabse adhik guni bhi. Bachpan mein hi unhone Vishwamitra Muni ke yajna ki raksha ki aur Tadaka naam ki raakshasni ka vadh kiya. Ram mein dayaaluta, satyavaadita aur dharma ka palan karne ki shakti thi.",
        
        "Sita Swayamvar mein Raja Janaka ne yeh ghoshana ki thi ki jo bhi Shiv Dhanush ko uthaakar uspar prateecha chadha dega, Sita ka vivah usi se hoga. Bahut saare raja-maharaja aaye lekin koi bhi dhanush ko hila bhi nahi saka. Jab Ram ki baari aayi tab unhone ek haath se dhanush utha liya aur prateecha chadhaate samay wo toot gaya. Poore darbaar mein khushi ki lehre fail gayi aur Ram-Sita ka vivah hua.",
        
        "Ayodhya mein Ram ka rajyabhishek hone waala tha lekin Kaikeyi ne apne do vardon ka use karke Dasharath se kaha ki Bharat ko raja banaao aur Ram ko 14 saal ke liye vanvas par bhejo. Ram ne bina kisi shikayat ke pita ki aagya ka palan kiya aur Sita-Lakshman ke saath vanvas ke liye nikal pade. Unki is dharma-paalan ki shakti ko dekh kar sab chashak se gaye.",
        
        "Ravana ne Sita ka haran kar liya tha. Ram ne Hanuman ki madad se Sita ko dhundha aur vanaron ki sena ke saath Lanka par chadhaayi ki. Yudh bahut bhayankar tha. Ravana bahut shakti-shali tha lekin Ram ne apne dhairya aur yukti se usse haraaya. Jab Ram ne Ravana ka vadh kiya tab dharma ki vijay hui. Ram Sita ke saath Ayodhya laut aaye aur unka rajyabhishek hua."
    ],
    
    "durga": [
        "Mahishasura ek bahut shakti-shali asur tha jise Brahma ji ka vardaan tha ki koi bhi purush use nahi maar sakta. Is vardaan ke baad Mahishasura ne swarg par aakraman kar diya aur sabhi devtaon ko parajit kar diya. Devtaon ne Brahma, Vishnu aur Shiva se madad maangi. Teeno devtaon ne apni shakti se ek divya prakash utpann kiya jisse Maa Durga ka janam hua. Har devta ne unhe apna astra diya.",
        
        "Mahishasura ka vadh karne ke liye Maa Durga ne apna sher par sawaar hokar yudh kiya. Mahishasura ne kai roop badal kar Durga ko harane ki koshish ki. Kabhi bail bana, kabhi sher, kabhi haathi. Lekin Maa Durga ne har roop mein use parajit kiya. Antim yudh mein jab Mahishasura apne asli bhains roop mein aaya tab Maa Durga ne apne trishul se uska vadh kar diya aur prithvi ko bachaya.",
        
        "Navratri mein Maa Durga ke nau roop ki pooja ki jaati hai. Shailputri, Brahmacharini, Chandraghanta, Kushmanda, Skandamata, Katyayani, Kaalratri, Mahagauri aur Siddhidatri. Har roop ki apni visheshta hai aur har roop se humein kuch sikhne ko milta hai. Navratri mein bhakton ko Maa Durga ki kripa milti hai aur wo sab pareshaniyon se mukti paate hai.",
        
        "Maa Durga shakti ki pratik hai. Wo humein sikhati hai ki jeevan mein aane waali har mushkil ka saamna himmat aur vishwas ke saath karna chahiye. Jab bhi burai badhti hai tab Maa Durga dharti par aati hai aur asurון ka naash karti hai. Unki aradhana se manushya ko bal, buddhi aur shakti milti hai."
    ],
    
    "kali": [
        "Raktabeej naam ka ek aisa asur tha jiske raktपات की har boond se ek naya Raktabeej paida ho jaata tha. Jab devta use maarne ki koshish karte tab uske khoon se hazaaron Raktabeej ban jaate. Devtaon ne Maa Durga se madad maangi. Tab Maa Durga ke gusse se Kali ka janam hua. Unka roop itna bhayankar tha ki asur kaanpne lage.",
        
        "Kali ne Raktabeej ke saath yudh kiya aur ek aisi yukti lagaayi ki unhone Raktabeej ka khoon dharti par girne se pehle hi pee liya. Is tarah Raktabeej ko koi naya sharir nahi mil paaya aur Kali ne uska vadh kar diya. Lekin yudh ke baad Kali ka gussa shaant nahi hua aur wo puri prithvi par tandav karne lagi. Srishti ke naash ka khatra ban gaya.",
        
        "Jab Maa Kali apne tandav se nahi ruki tab Bhagwan Shiva unke paath mein let gaye. Jab Kali ne Shiva ko pairo tale kuchlaa tab unhe ehsaas hua aur wo shaant ho gayi. Unki jeebh baahar nikal aayi sharam ke kaaran. Is roop mein Kali ko Dakshineshwar Kali ke naam se jaana jaata hai. Yeh humein sikhata hai ki gussa par niyantran zaroori hai.",
        
        "Maa Kali samay ki devta hai aur wo humare bhayankar swapno ka nash karti hai. Unki kaali chaamdi andhkar ko darshati hai jahan se prakash nikalta hai. Unka tandav purane ka nash aur naye ki shuruaat hai. Bhakton ko wo har tarah ki pareshani se bachati hai aur suraksha pradan karti hai."
    ],
    
    "parvati": [
        "Parvati Maa Himavan ki beti thi. Bachpan se hi unka mann Shiva mein ramta tha. Unhone ghori tapasya ki taaki wo Shiva ki patni ban sake. Kai saal tak bina khaye piye jungle mein khadi rahi. Garmi, sardi, baarish kuch bhi unhe tapasya se rok nahi paaya. Devas ne Kamdev ko bheja jo Shiva ke mann mein pyaar utpann kare lekin Shiva ne gusse mein Kamdev ko bhasma kar diya.",
        
        "Parvati ne apni tapasya jaari rakhi. Akhir mein Shiva prakat hue aur Parvati ko apni shakti sweekar kiya. Dono ka vivah bahut dhumdhaam se hua. Parvati aur Shiva ka mel sampoorn shakti ka pratik hai. Jahan Shiva sanhaarak hai wahan Parvati paalanhaar. Dono mil kar srishti ka sanchalan karte hai aur bhakton ki raksha karte hai.",
        
        "Parvati ne Ganesha ki rachna ki aur jab Shiva ne Ganesha ka sir kaat diya tab wo bahut dukhi hui. Tab Shiva ne Ganesha ko hasthi ka sir lagakar dobara jeevan diya. Parvati bahut khush hui. Isse humein sikhne ko milta hai ki maa apni santaan ke liye kuch bhi kar sakti hai aur pita ki jimmedaari bhi utni hi mahatvapurn hai.",
        
        "Maa Parvati prem, samarpan aur tapasya ki devta hai. Wo humein sikhati hai ki jeevan mein lakshya prapti ke liye dridh sankalp aur tapasya zaroori hai. Unki pooja se parivaar mein sukh-shaanti aati hai aur pati-patni ka bandhan majboot hota hai. Wo Shakti ka roop hai aur unke bina Shiva Shav hai."
    ]
}

# ============================================================================
# DEITY KEYWORDS FOR IMAGE SEARCH
# ============================================================================

DEITY_KEYWORDS = {
    "krishna": {
        "keywords": [
            "lord krishna statue divine",
            "krishna flute vrindavan", 
            "radha krishna temple",
            "govardhan krishna painting",
            "vishnu avatar krishna",
            "krishna makhan chor"
        ],
        "thumbnail_keywords": [
            "krishna divine colorful statue",
            "krishna golden idol temple"
        ],
        "thumbnail_text": "Krishna Leela"
    },
    
    "mahadev": {
        "keywords": [
            "shiva statue powerful divine",
            "mahadev meditation trishul",
            "shiva lingam sacred temple",
            "har har mahadev statue",
            "shiv temple ancient",
            "neelkanth mahadev"
        ],
        "thumbnail_keywords": [
            "mahadev powerful divine statue",
            "shiva golden idol"
        ],
        "thumbnail_text": "Mahadev Shakti"
    },
    
    "ganesha": {
        "keywords": [
            "ganesha statue golden idol",
            "ganpati modak blessing",
            "riddhi siddhi ganesha",
            "vinayak temple divine",
            "ganesha festival colorful",
            "ekdanta ganesha"
        ],
        "thumbnail_keywords": [
            "ganesha golden divine idol",
            "ganpati colorful statue"
        ],
        "thumbnail_text": "Ganesha Kripa"
    },
    
    "hanuman": {
        "keywords": [
            "hanuman statue powerful",
            "bajrang bali divine",
            "sankat mochan hanuman",
            "ram bhakt hanuman",
            "pawan putra statue",
            "hanuman temple ancient"
        ],
        "thumbnail_keywords": [
            "hanuman powerful statue",
            "bajrang bali golden"
        ],
        "thumbnail_text": "Hanuman Shakti"
    },
    
    "ram": {
        "keywords": [
            "lord ram ayodhya statue",
            "ram sita divine painting",
            "maryada purushottam ram",
            "ramayana ram temple",
            "ram darbar divine",
            "shri ram statue golden"
        ],
        "thumbnail_keywords": [
            "ram ayodhya golden statue",
            "ram divine painting"
        ],
        "thumbnail_text": "Ram Bhakti"
    },
    
    "durga": {
        "keywords": [
            "durga maa powerful statue",
            "mahishasura mardini",
            "navratri durga divine",
            "shakti durga goddess",
            "durga puja colorful",
            "amba bhavani statue"
        ],
        "thumbnail_keywords": [
            "durga maa powerful divine",
            "navratri goddess statue"
        ],
        "thumbnail_text": "Durga Shakti"
    },
    
    "kali": {
        "keywords": [
            "kali maa powerful statue",
            "mahakali divine fierce",
            "kali tandav powerful",
            "dakshina kali statue",
            "kali maa temple",
            "bhadrakali goddess"
        ],
        "thumbnail_keywords": [
            "kali maa fierce divine",
            "mahakali powerful statue"
        ],
        "thumbnail_text": "Kali Shakti"
    },
    
    "parvati": {
        "keywords": [
            "parvati maa divine statue",
            "uma gauri goddess",
            "shiva parvati temple",
            "parvati devi painting",
            "himalaya putri statue",
            "shakti parvati divine"
        ],
        "thumbnail_keywords": [
            "parvati divine beautiful",
            "uma devi statue golden"
        ],
        "thumbnail_text": "Parvati Kripa"
    }
}

# ============================================================================
# GOD-SPECIFIC BACKGROUND MUSIC (RAW GITHUB URLS)
# ============================================================================

DEITY_MUSIC = {
    "shiva": [
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(10).weba",
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(13).weba"
    ],
    "mahadev": [
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(10).weba",
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(13).weba"
    ],
    "krishna": [
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(11).weba",
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(14).weba"
    ],
    "ganesha": [
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(15).weba"
    ],
    "ram": [
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(16).weba"
    ],
    # All other gods use default spiritual music
    "hanuman": [
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(11).weba"
    ],
    "durga": [
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(11).weba"
    ],
    "kali": [
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(11).weba"
    ],
    "parvati": [
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(11).weba"
    ],
    "default": [
        "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(11).weba"
    ]
}

# ============================================================================
# 5 PROFESSIONAL TRANSITIONS (Like Canva)
# ============================================================================

TRANSITIONS = [
    {
        "name": "zoom",
        "filter": "zoompan=z='if(lte(zoom,1.0),1.8,max(1.001,zoom-0.008))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}"
    },
    {
        "name": "fade",
        "filter": "zoompan=z='if(lte(zoom,1.0),2.0,max(1.001,zoom-0.01))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps},fade=t=in:st=0:d=0.3"
    },
    {
        "name": "slide",  # Ken Burns effect
        "filter": "zoompan=z='1.5':d={frames}:x='iw/2-(iw/zoom/2)+((iw/zoom/2)*sin(on/{frames}*PI))':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}"
    },
    {
        "name": "rotate",  # Subtle rotation with zoom
        "filter": "zoompan=z='if(lte(zoom,1.0),1.6,max(1.001,zoom-0.007))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps},rotate='PI*on/{frames}/10'"
    },
    {
        "name": "pan",  # Horizontal pan
        "filter": "zoompan=z='1.3':d={frames}:x='iw/2-(iw/zoom/2)+(on/{frames}*100)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}"
    }
]

# ============================================================================
# UTILITIES
# ============================================================================

def force_cleanup(*filepaths):
    """Cleanup files"""
    for fp in filepaths:
        try:
            if fp and os.path.exists(fp):
                os.remove(fp)
        except:
            pass
    gc.collect()

def get_size_kb(fp: str) -> float:
    try:
        return os.path.getsize(fp) / 1024
    except:
        return 0.0

def get_size_mb(fp: str) -> float:
    return get_size_kb(fp) / 1024

def run_ffmpeg(cmd: list, timeout: int = 120) -> bool:
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout, check=False).returncode == 0
    except:
        return False

def convert_weba_to_mp3(weba: str, mp3: str) -> bool:
    """Convert .weba to .mp3"""
    try:
        return run_ffmpeg([
            "ffmpeg", "-i", weba, "-vn", "-acodec", "libmp3lame", 
            "-b:a", "128k", "-y", mp3
        ], FFMPEG_TIMEOUT_MUSIC)
    except:
        return False

# ============================================================================
# DEITY SELECTION
# ============================================================================

def select_deity() -> tuple:
    """Randomly select a deity with story"""
    deity_name = random.choice(list(DEITY_STORIES.keys()))
    deity = {
        "stories": DEITY_STORIES[deity_name],
        "keywords": DEITY_KEYWORDS[deity_name]["keywords"],
        "thumbnail_keywords": DEITY_KEYWORDS[deity_name]["thumbnail_keywords"],
        "thumbnail_text": DEITY_KEYWORDS[deity_name]["thumbnail_text"],
        "music_urls": DEITY_MUSIC.get(deity_name, DEITY_MUSIC["default"])
    }
    story = random.choice(deity["stories"])
    
    logger.info(f"🕉️ Selected: {deity_name.upper()}")
    logger.info(f"📖 Story length: {len(story)} characters")
    
    return deity_name, deity, story

# ============================================================================
# ANTI-REPETITION: SCRIPT HASHING
# ============================================================================

async def generate_unique_script(database_manager, user_id: str, niche: str, 
                                deity_name: str, story: str, target_duration: int) -> dict:
    """Generate unique script with hash checking"""
    
    # Generate script hash
    script_hash = hashlib.sha256(story.encode()).hexdigest()
    
    # Check if already generated
    try:
        existing = await database_manager.db.pixabay_scripts_collection.find_one({
            "user_id": user_id,
            "niche": niche,
            "script_hash": script_hash
        })
        
        if existing:
            logger.warning(f"⚠️ Script already generated, selecting different story...")
            # Recursively try again with different story
            _, deity, new_story = select_deity()
            return await generate_unique_script(database_manager, user_id, niche, 
                                               deity_name, new_story, target_duration)
    except:
        pass  # Continue if DB check fails
    
    # Generate AI script
    cta = "Agar aapko yeh video achhi lagi ho toh LIKE karein, SUBSCRIBE karein aur apne doston ko SHARE karein taaki aage bhi update videos milte rahe!"
    
    prompt = f"""Generate engaging Hindi narration for spiritual video:

Story: {story}

Duration: {target_duration} seconds
Deity: {deity_name}

RULES:
1. Create UNIQUE content every time
2. Natural Hindi flow (not robotic)
3. Use commas, exclamations for natural breaks
4. NO "pause" word - use natural speech rhythm
5. Include hook + main story + conclusion
6. Add CTA at end: "{cta}"

Generate creative Hindi script in JSON format:
{{
    "script": "Hindi narration here...",
    "title": "Hinglish title (2-5 words)"
}}"""
    
    try:
        if not MISTRAL_API_KEY:
            raise Exception("No AI key")
            
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                json={
                    "model": "mistral-large-latest",
                    "messages": [
                        {"role": "system", "content": "You are a spiritual storyteller. Create UNIQUE Hindi scripts every time. Output ONLY JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.95,  # High for uniqueness
                    "max_tokens": 1200
                }
            )
            
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                content = re.sub(r'```json\n?|\n?```', '', content).strip()
                match = re.search(r'\{.*\}', content, re.DOTALL)
                
                if match:
                    data = json.loads(match.group(0))
                    script_text = data.get("content", data.get("script", ""))
                    
                    # Ensure CTA is present
                    if "LIKE" not in script_text or "SUBSCRIBE" not in script_text:
                        script_text += " " + cta
                    
                    title = data.get("title", f"{deity_name.title()} Ki Kahani")
                    
                    # Store in database to prevent repetition
                    try:
                        await database_manager.db.pixabay_scripts_collection.insert_one({
                            "user_id": user_id,
                            "niche": niche,
                            "deity_name": deity_name,
                            "script_hash": script_hash,
                            "script_text": script_text,
                            "title": title,
                            "created_at": datetime.now()
                        })
                    except:
                        pass
                    
                    return {
                        "script": script_text,
                        "title": title,
                        "script_hash": script_hash
                    }
    except Exception as e:
        logger.error(f"Script generation error: {e}")
    
    # Fallback
    return {
        "script": story + " " + cta,
        "title": f"{deity_name.title()} Ki Kahani",
        "script_hash": script_hash
    }

# ============================================================================
# IMAGE SEARCH & DOWNLOAD WITH DYNAMIC SIZING
# ============================================================================

async def search_pixabay_hd(keywords: List[str], count: int, 
                           is_thumbnail: bool = False) -> List[dict]:
    """Search Pixabay for HD images"""
    all_images = []
    seen_urls = set()
    
    for keyword in random.sample(keywords, min(len(keywords), 5)):
        if len(all_images) >= count:
            break
        
        try:
            async with httpx.AsyncClient(timeout=25) as client:
                resp = await client.get(
                    "https://pixabay.com/api/",
                    params={
                        "key": PIXABAY_API_KEY,
                        "q": keyword,
                        "image_type": "photo",
                        "orientation": "vertical" if not is_thumbnail else "horizontal",
                        "per_page": 30,
                        "order": "popular",
                        "safesearch": "true",
                        "min_width": 1080 if not is_thumbnail else 1280,
                        "min_height": 1920 if not is_thumbnail else 720
                    }
                )
                
                if resp.status_code == 200:
                    hits = resp.json().get("hits", [])
                    
                    for hit in hits:
                        if len(all_images) >= count:
                            break
                        
                        # Get highest quality URL
                        url = hit.get("fullHDURL") or hit.get("largeImageURL") or hit.get("webformatURL")
                        
                        if url and url not in seen_urls:
                            size_kb = hit.get("imageSize", 0) / 1024
                            
                            # Filter for thumbnail size
                            if is_thumbnail:
                                if size_kb < THUMBNAIL_MIN_SIZE_KB or size_kb > THUMBNAIL_MAX_SIZE_KB:
                                    continue
                            
                            all_images.append({
                                "url": url,
                                "size_kb": size_kb,
                                "keyword": keyword,
                                "width": hit.get("imageWidth", 0),
                                "height": hit.get("imageHeight", 0)
                            })
                            seen_urls.add(url)
        except Exception as e:
            logger.warning(f"Search error for '{keyword}': {e}")
            continue
    
    logger.info(f"✅ Found: {len(all_images)} images")
    return all_images[:count]

async def download_and_resize_image(img_data: dict, output_path: str, retry: int = 0) -> bool:
    """Download image and resize dynamically to 720x1280"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(img_data["url"], follow_redirects=True)
            
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content))
                
                # DYNAMIC RESIZING LOGIC
                original_width, original_height = img.size
                aspect_ratio = original_width / original_height
                target_aspect = IMAGE_TARGET_WIDTH / IMAGE_TARGET_HEIGHT  # 720/1280 = 0.5625
                
                if aspect_ratio > target_aspect:
                    # Image is wider - crop width
                    new_height = original_height
                    new_width = int(new_height * target_aspect)
                    left = (original_width - new_width) // 2
                    img = img.crop((left, 0, left + new_width, new_height))
                else:
                    # Image is taller - crop height from top/bottom
                    new_width = original_width
                    new_height = int(new_width / target_aspect)
                    top = (original_height - new_height) // 2
                    img = img.crop((0, top, new_width, top + new_height))
                
                # Resize to exact target
                img = img.resize((IMAGE_TARGET_WIDTH, IMAGE_TARGET_HEIGHT), Image.Resampling.LANCZOS)
                
                # Save
                img.save(output_path, "JPEG", quality=95)
                
                if get_size_kb(output_path) > 100:  # Minimum 100KB
                    logger.info(f"   ✅ Resized & saved: {get_size_kb(output_path):.0f}KB")
                    return True
                else:
                    force_cleanup(output_path)
                    return False
                    
    except Exception as e:
        logger.warning(f"Download error: {e}")
        if retry < 2:
            await asyncio.sleep(1)
            return await download_and_resize_image(img_data, output_path, retry + 1)
    
    return False

async def download_images(images: List[dict], temp_dir: str) -> List[str]:
    """Download and resize all images"""
    downloaded = []
    
    for idx, img in enumerate(images):
        path = os.path.join(temp_dir, f"img_{idx:02d}.jpg")
        if await download_and_resize_image(img, path):
            downloaded.append(path)
            logger.info(f"📥 Downloaded: {idx+1}/{len(images)}")
    
    logger.info(f"✅ Total downloaded: {len(downloaded)}/{len(images)}")
    return downloaded

# ============================================================================
# THUMBNAIL WITH GOLDEN OVERLAY
# ============================================================================

def add_text_to_thumbnail(image_path: str, text: str, output_path: str) -> bool:
    """Add golden yellow text overlay to thumbnail"""
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Load bold font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position (bottom center)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = ((img.width - text_width) // 2, img.height - text_height - 100)
        
        # Black outline (3px thick)
        for adj in range(-3, 4):
            for adj2 in range(-3, 4):
                draw.text((position[0]+adj, position[1]+adj2), text, font=font, fill="black")
        
        # Golden yellow main text (#FFD700)
        draw.text(position, text, font=font, fill="#FFD700")
        
        img.save(output_path, quality=95)
        logger.info(f"✅ Text added to thumbnail: '{text}'")
        return True
        
    except Exception as e:
        logger.error(f"Thumbnail text error: {e}")
        return False

# ============================================================================
# VOICE GENERATION WITH 1.15x SPEED
# ============================================================================

async def generate_voice_115x(text: str, temp_dir: str) -> Optional[str]:
    """Generate voice at 1.15x speed (ElevenLabs or Edge TTS)"""
    
    # Try ElevenLabs first
    if ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 20:
        try:
            voice_id = "yD0Zg2jxgfQLY8I2MEHO"  # Spiritual voice
            
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={"xi-api-key": ELEVENLABS_API_KEY},
                    json={
                        "text": text[:2000],
                        "model_id": "eleven_multilingual_v2"
                    }
                )
                
                if resp.status_code == 200:
                    base_audio = os.path.join(temp_dir, "voice_base.mp3")
                    with open(base_audio, 'wb') as f:
                        f.write(resp.content)
                    
                    # Apply 1.15x speed
                    final_audio = os.path.join(temp_dir, "voice.mp3")
                    if run_ffmpeg([
                        "ffmpeg", "-i", base_audio, "-filter:a", "atempo=1.15", 
                        "-y", final_audio
                    ], 30):
                        force_cleanup(base_audio)
                        logger.info(f"✅ ElevenLabs voice (1.15x): {get_size_mb(final_audio):.2f}MB")
                        return final_audio
                    
                    force_cleanup(base_audio)
        except Exception as e:
            logger.warning(f"ElevenLabs error: {e}")
    
    # Fallback to Edge TTS
    try:
        import edge_tts
        
        base_audio = os.path.join(temp_dir, "edge_base.mp3")
        final_audio = os.path.join(temp_dir, "edge_voice.mp3")
        
        # Generate with +15% rate
        await edge_tts.Communicate(
            text[:1500],
            "hi-IN-MadhurNeural",
            rate="+15%"
        ).save(base_audio)
        
        # Apply additional 1.15x speed
        if run_ffmpeg([
            "ffmpeg", "-i", base_audio, "-filter:a", "atempo=1.15", 
            "-y", final_audio
        ], 30):
            force_cleanup(base_audio)
            logger.info(f"✅ Edge TTS voice (1.15x): {get_size_mb(final_audio):.2f}MB")
            return final_audio
        
        force_cleanup(base_audio)
    except Exception as e:
        logger.error(f"Edge TTS error: {e}")
    
    return None

# ============================================================================
# MUSIC DOWNLOAD & PROCESSING
# ============================================================================

async def download_music(music_urls: List[str], temp_dir: str, duration: float) -> Optional[str]:
    """Download and process background music"""
    
    # Random selection if multiple URLs
    music_url = random.choice(music_urls)
    
    logger.info(f"🎵 Downloading music from: {music_url}")
    
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            resp = await client.get(music_url)
            
            if resp.status_code == 200:
                raw_music = os.path.join(temp_dir, "music_raw.weba")
                with open(raw_music, 'wb') as f:
                    f.write(resp.content)
                
                logger.info(f"🗑️ Cleaned: {os.path.basename(raw_music)}")
                
                # Convert .weba to .mp3
                converted_music = os.path.join(temp_dir, "music_converted.mp3")
                if convert_weba_to_mp3(raw_music, converted_music):
                    force_cleanup(raw_music)
                    logger.info(f"✅ Converted to MP3")
                    
                    # Crop to video duration
                    final_music = os.path.join(temp_dir, "music_final.mp3")
                    if run_ffmpeg([
                        "ffmpeg", "-i", converted_music, "-t", str(min(duration, 55)),
                        "-acodec", "copy", "-y", final_music
                    ], FFMPEG_TIMEOUT_MUSIC):
                        force_cleanup(converted_music)
                        logger.info(f"🗑️ Cleaned: {os.path.basename(converted_music)}")
                        logger.info(f"✅ Music: {get_size_mb(final_music):.2f}MB")
                        return final_music
                    
                    force_cleanup(converted_music)
                    return converted_music if os.path.exists(converted_music) else None
                
                return raw_music if os.path.exists(raw_music) else None
    except Exception as e:
        logger.error(f"Music download error: {e}")
    
    return None

# ============================================================================
# SLIDESHOW CREATION WITH 5 TRANSITIONS
# ============================================================================

def create_slideshow(images: List[str], duration_per_image: float, temp_dir: str) -> Optional[str]:
    """Create slideshow with random transitions"""
    
    try:
        if len(images) < MIN_IMAGES:
            logger.error(f"Not enough images: {len(images)}")
            return None
        
        frames = int(duration_per_image * FPS)
        clips = []
        
        logger.info(f"🎬 Creating slideshow with {len(images)} images...")
        
        for idx, img in enumerate(images, 1):
            # Resize to exact dimensions (already done in download, but verify)
            resized = os.path.join(temp_dir, f"resized_{idx}.jpg")
            if not run_ffmpeg([
                "ffmpeg", "-i", img, "-vf", 
                f"scale={IMAGE_TARGET_WIDTH}:{IMAGE_TARGET_HEIGHT}:force_original_aspect_ratio=increase,crop={IMAGE_TARGET_WIDTH}:{IMAGE_TARGET_HEIGHT}",
                "-q:v", "2", "-y", resized
            ], 15):
                continue
            
            # Random transition
            transition = random.choice(TRANSITIONS)
            filter_str = transition["filter"].format(frames=frames, fps=FPS)
            
            clip_output = os.path.join(temp_dir, f"clip_{idx}.mp4")
            
            logger.info(f"Clip {idx}/{len(images)}")
            
            if run_ffmpeg([
                "ffmpeg", "-loop", "1", "-i", resized, "-vf", filter_str,
                "-t", str(duration_per_image), "-r", str(FPS),
                "-c:v", "libx264", "-crf", "20", "-preset", "fast",
                "-pix_fmt", "yuv420p", "-y", clip_output
            ], FFMPEG_TIMEOUT_CLIP):
                clips.append(clip_output)
                logger.info(f"   ✅ Clip {idx}: {get_size_mb(clip_output):.1f}MB")
            
            force_cleanup(resized)
        
        if len(clips) < MIN_IMAGES:
            logger.error("Not enough clips created")
            return None
        
        # Concatenate all clips
        concat_file = os.path.join(temp_dir, "concat.txt")
        with open(concat_file, 'w') as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        slideshow_output = os.path.join(temp_dir, "slideshow.mp4")
        
        logger.info(f"🔗 Concatenating {len(clips)} clips...")
        
        if run_ffmpeg([
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file,
            "-c", "copy", "-y", slideshow_output
        ], FFMPEG_TIMEOUT_CONCAT):
            for clip in clips:
                force_cleanup(clip)
            
            logger.info(f"✅ Slideshow: {get_size_mb(slideshow_output):.1f}MB")
            return slideshow_output
        
        return None
        
    except Exception as e:
        logger.error(f"Slideshow creation error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

# ============================================================================
# AUDIO MIXING
# ============================================================================

async def mix_audio(video_path: str, voice_path: str, music_path: Optional[str], temp_dir: str) -> Optional[str]:
    """Mix voice and background music with video"""
    
    try:
        final_output = os.path.join(temp_dir, "final_video.mp4")
        
        if music_path:
            # Mix voice + music (12% volume for music)
            cmd = [
                "ffmpeg", "-i", video_path, "-i", voice_path, "-i", music_path,
                "-filter_complex",
                "[1:a]volume=1.0[voice];[2:a]volume=0.12[music];[voice][music]amix=inputs=2:duration=first[audio]",
                "-map", "0:v", "-map", "[audio]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-shortest", "-y", final_output
            ]
        else:
            # Only voice
            cmd = [
                "ffmpeg", "-i", video_path, "-i", voice_path,
                "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac",
                "-shortest", "-y", final_output
            ]
        
        if run_ffmpeg(cmd, FFMPEG_TIMEOUT_MUSIC):
            logger.info(f"✅ Final video: {get_size_mb(final_output):.1f}MB")
            return final_output
        
        return None
        
    except Exception as e:
        logger.error(f"Audio mixing error: {e}")
        return None

# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

async def generate_pixabay_video(
    niche: str,
    language: str,
    user_id: str,
    database_manager,
    target_duration: int = 40,
    custom_bg_music: Optional[str] = None
) -> dict:
    """Main video generation function"""
    
    temp_dir = None
    
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="pixabay_")
        logger.info(f"🎬 START: {niche} | Duration: {target_duration}s | Language: {language}")
        
        # STEP 1: Select deity & story
        deity_name, deity, story = select_deity()
        
        # STEP 2: Generate unique AI script
        script_data = await generate_unique_script(
            database_manager, user_id, niche, deity_name, story, target_duration
        )
        
        script_text = script_data["script"]
        title = script_data["title"]
        
        # Estimate images needed
        script_duration = len(script_text.split()) / 2.75  # ~165 words/min at 1.15x
        num_images = max(MIN_IMAGES, min(int(script_duration / 3.5), MAX_IMAGES))
        image_duration = script_duration / num_images
        
        logger.info(f"📊 Script: {len(script_text)} chars, {num_images} images @ {image_duration:.1f}s each")
        
        # STEP 3: Search & download images
        logger.info(f"🔍 Searching {num_images} images...")
        images_data = await search_pixabay_hd(deity["keywords"], num_images, False)
        
        if len(images_data) < MIN_IMAGES:
            return {"success": False, "error": f"Not enough images: {len(images_data)}"}
        
        # STEP 4: Search thumbnail
        logger.info(f"🖼️ Searching HD thumbnail...")
        thumb_data = await search_pixabay_hd(deity["thumbnail_keywords"], 1, True)
        
        # STEP 5: Download all images
        logger.info(f"📥 Downloading {len(images_data)} images...")
        image_files = await download_images(images_data, temp_dir)
        
        if len(image_files) < MIN_IMAGES:
            return {"success": False, "error": "Image download failed"}
        
        # Adjust image duration if needed
        if len(image_files) != num_images:
            image_duration = script_duration / len(image_files)
            logger.info(f"🔄 Adjusted: {len(image_files)} images @ {image_duration:.1f}s each")
        
        # STEP 6: Create thumbnail with overlay
        thumb_file = None
        if thumb_data:
            thumb_base = os.path.join(temp_dir, "thumb_base.jpg")
            
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(thumb_data[0]["url"])
                if resp.status_code == 200:
                    with open(thumb_base, 'wb') as f:
                        f.write(resp.content)
                    
                    thumb_final = os.path.join(temp_dir, "thumbnail.jpg")
                    if add_text_to_thumbnail(thumb_base, deity["thumbnail_text"], thumb_final):
                        thumb_file = thumb_final
                        logger.info(f"✅ Thumb: {get_size_kb(thumb_file):.0f}KB")
        
        # STEP 7: Download & process music
        logger.info(f"🎵 Downloading background music...")
        music_file = await download_music(deity["music_urls"], temp_dir, script_duration)
        
        # STEP 8: Create slideshow
        logger.info(f"🎬 Creating slideshow...")
        slideshow_file = create_slideshow(image_files, image_duration, temp_dir)
        
        if not slideshow_file:
            return {"success": False, "error": "Slideshow creation failed"}
        
        # Cleanup source images
        for img in image_files:
            force_cleanup(img)
        gc.collect()
        
        # STEP 9: Generate voice at 1.15x speed
        logger.info(f"🎙️ Generating voice (1.15x speed)...")
        voice_file = await generate_voice_115x(script_text, temp_dir)
        
        if not voice_file:
            return {"success": False, "error": "Voice generation failed"}
        
        # STEP 10: Mix audio
        logger.info(f"🎛️ Mixing audio...")
        final_video = await mix_audio(slideshow_file, voice_file, music_file, temp_dir)
        
        if not final_video:
            return {"success": False, "error": "Audio mixing failed"}
        
        final_size = get_size_mb(final_video)
        logger.info(f"✅ FINAL: {final_size:.1f}MB")
        
        # STEP 11: Upload to YouTube
        logger.info(f"📤 Uploading to YouTube...")
        
        try:
            from mainY import youtube_scheduler
            
            # Get credentials
            from YTdatabase import get_database_manager as get_yt_db
            yt_db = get_yt_db()
            
            if yt_db and yt_db.youtube.client:
                creds_raw = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
                
                if creds_raw:
                    credentials = {
                        "access_token": creds_raw.get("access_token"),
                        "refresh_token": creds_raw.get("refresh_token"),
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "client_id": creds_raw.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
                        "client_secret": creds_raw.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
                        "scopes": ["https://www.googleapis.com/auth/youtube.upload"]
                    }
                    
                    # Generate keywords
                    keywords = [
                        f"#{deity_name}", "#spiritual", "#hindu", "#भक्ति",
                        "#shorts", "#trending", "#viral", "#india"
                    ]
                    
                    description = f"{script_text}\n\n" + "\n".join(keywords)
                    
                    upload_result = await youtube_scheduler.generate_and_upload_content(
                        user_id=user_id,
                        credentials_data=credentials,
                        content_type="shorts",
                        title=title,
                        description=description,
                        video_url=final_video,
                        thumbnail_path=thumb_file  # ← Upload thumbnail with overlay!
                    )
                    
                    if upload_result.get("success"):
                        video_id = upload_result.get("video_id")
                        
                        # Store in database
                        try:
                            await database_manager.db.pixabay_scripts_collection.update_one(
                                {"script_hash": script_data["script_hash"]},
                                {"$set": {"video_id": video_id}},
                                upsert=False
                            )
                        except:
                            pass
                        
                        # Cleanup
                        if temp_dir:
                            shutil.rmtree(temp_dir, ignore_errors=True)
                        gc.collect()
                        
                        logger.info(f"🎉 SUCCESS! Video ID: {video_id}")
                        
                        return {
                            "success": True,
                            "video_id": video_id,
                            "video_url": f"https://youtube.com/shorts/{video_id}",
                            "title": title,
                            "deity": deity_name,
                            "images_used": len(image_files),
                            "duration": f"{script_duration:.1f}s",
                            "size": f"{final_size:.1f}MB",
                            "has_thumbnail": thumb_file is not None
                        }
        except Exception as upload_error:
            logger.error(f"Upload error: {upload_error}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Cleanup on error
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": "Upload failed"}
        
    except Exception as e:
        logger.error(f"❌ Generation error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e)}

# ============================================================================
# API ROUTES
# ============================================================================

router = APIRouter()

@router.get("/api/pixabay/niches")
async def get_niches():
    """Get available niches"""
    return {
        "success": True,
        "niches": {
            "spiritual": {
                "name": "Spiritual/Divine",
                "deities": list(DEITY_STORIES.keys()),
                "total_stories": sum(len(stories) for stories in DEITY_STORIES.values())
            }
        }
    }

@router.post("/api/pixabay/generate")
async def generate_endpoint(request: Request):
    """Generate Pixabay slideshow video"""
    
    try:
        data = await request.json()
        
        user_id = data.get("user_id")
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "user_id required"})
        
        niche = data.get("niche", "spiritual")
        language = data.get("language", "hindi")
        target_duration = max(20, min(data.get("target_duration", 40), 55))
        custom_bg_music = data.get("custom_bg_music")
        
        # Get database manager
        from Supermain import database_manager
        
        result = await asyncio.wait_for(
            generate_pixabay_video(niche, language, user_id, database_manager, target_duration, custom_bg_music),
            timeout=1800  # 30 minutes
        )
        
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
    except Exception as e:
        logger.error(f"Endpoint error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

__all__ = ['router']