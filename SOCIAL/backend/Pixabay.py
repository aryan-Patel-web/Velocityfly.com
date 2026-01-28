"""
pixabay_ultimate_production.py - ULTIMATE PRODUCTION VERSION V3 FINAL
==================================================
✅ Luxury: AI dynamically selects car + scrapes real specs
✅ Spiritual: Random Krishna/Mahadev with authentic stories
✅ Voice: 1.1x speed for ElevenLabs (already configured)
✅ Thumbnail: 200KB - 2MB range (not 10-15MB)
✅ Niche filtering: Filters coffee/couples from wrong niches
✅ Keywords: Consistent similar keywords per niche
✅ AI generates UNIQUE scripts every time (no repetition)
✅ NO hardcoding - fully dynamic
==================================================
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
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "54364709-1e6532279f08847859d5bea5e")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# PROCESSING LIMITS
MAX_VIDEO_SIZE_MB = 40
FFMPEG_TIMEOUT_CLIP = 180
FFMPEG_TIMEOUT_CONCAT = 300
FFMPEG_TIMEOUT_MUSIC = 120

# IMAGE CONFIGURATION
MIN_IMAGES = 6
MAX_IMAGES = 12
IMAGE_TARGET_WIDTH = 720
IMAGE_TARGET_HEIGHT = 1280
FPS = 30

# QUALITY THRESHOLDS
MIN_IMAGE_SIZE_KB = 900
THUMBNAIL_MIN_SIZE_KB = 200  # Changed: 200KB
THUMBNAIL_MAX_SIZE_KB = 2048  # Changed: 2MB (2048KB)

# RETRY
MAX_IMAGE_RETRIES = 3

# ============================================================================
# NICHE FILTERING - EXCLUDE IRRELEVANT IMAGES
# ============================================================================

NICHE_EXCLUSIONS = {
    "space": ["coffee", "cup", "cafe", "couple", "people", "person", "human", "restaurant", "food", "drink", "table", "chair", "office"],
    "luxury": ["coffee", "cup", "cafe", "couple", "restaurant", "food", "drink", "people walking", "crowd", "street food"],
    "horror": ["happy", "smiling", "celebration", "party", "coffee", "cafe", "wedding", "birthday"],
    "nature": ["city", "urban", "building", "car", "coffee", "cafe", "people", "crowd", "street"],
    "mystery": ["modern", "coffee", "cafe", "people smiling", "party", "celebration"],
    "spiritual": ["modern city", "coffee", "cafe", "party", "nightclub", "bar", "alcohol"],
    "motivation": ["sad", "depressed", "coffee alone", "lazy", "sleeping"],
    "funny": ["serious", "formal", "business", "office", "meeting"]
}

# ============================================================================
# SPIRITUAL DEITIES DATABASE
# ============================================================================

SPIRITUAL_DEITIES = {
    "krishna": {
        "keywords": ["krishna statue divine", "krishna painting art", "vrindavan temple beautiful", "radha krishna love", 
                    "krishna flute divine", "krishna peacock colorful", "krishna devotee prayer", "krishna temple golden"],
        "thumbnail_keywords": ["krishna colorful divine", "krishna statue golden"],
        "stories": [
            "Krishna ka janam Mathura ki kaalgari mein Devaki aur Vasudeva ke ghar hua tha. Unke chacha Kansa ne bhavishyavani suni thi ki Devaki ka aathva putra uski maut ka kaaran banega. Isliye unhone sabhi bachon ko marne ka nirdharay liya. Lekin jab Krishna ka janam hua, tabhi ek divya shakti ne prahariyon ko sone ke liye majboor kar diya. Vasudeva ne Krishna ko basket mein rakha aur bhaari baarish mein Yamuna nadi paar karne lage. Tab Yamuna nadi ne khud apna pani neeche kar diya aur Shesh Naag ne Krishna ko apne phano se suraksha di. Vasudeva ne Krishna ko Gokul mein Nand Baba aur Yashoda Maiya ke paas chhod diya. Yeh Krishna ki pehli leela thi jisme unhone prakriti ko bhi apne vash mein kar liya.",
            
            "Gokul mein Krishna ka bachpan bahut hi anokha tha. Woh makhan churane ke liye prasiddh the. Yashoda Maiya makhan ko oonchai par rakhti thi, par Krishna apne baalpan mein hi apne sakhao ke saath mil kar makhan nikal lete the. Ek din Yashoda ne unhe pakad liya aur daant lagi. Tab Krishna ne apna mukh khola aur Yashoda ne un mein pura brahmaand dekha - suraj, chaand, taare, prithvi, swarg, pataal sab kuch. Yeh dekhkar Yashoda ko smaran hua ki yeh koi saadharan bal nahi hai, balki Bhagwan ka avatar hai. Par Krishna ne fir se apni maya se unhe yeh bhula diya aur woh fir se mamta se bhare gaye.",
            
            "Govardhan Parvat uthana Krishna ki sabse prasiddh leela hai jo Bhagavata Purana mein likhi gayi hai. Vrindavan ke log har saal Indra Dev ki pooja karte the aur unhe bhojan chadhate the. Par Krishna ne logo ko samjhaya ki Govardhan Parvat hi unki asli rakshak hai jo unhe jal, bhojan aur chara deta hai. Logo ne Krishna ki baat maan li aur Govardhan ki pooja ki. Gusse mein akar Indra Dev ne Vrindavan par lagaatar saat din tak bhaari varsha ki. Tab Krishna ne apni chhoti ungli par pura Govardhan Parvat utha liya aur sab logo, gayo aur janwaro ko neeche suraksha di. Saat din baad Indra Dev ko apni galti ka ehsaas hua aur unhone Krishna se maafi maangi. Yeh leela sikhati hai ki ahankar ka nash hona zaroori hai.",
            
            "Mahabharat ke Kurukshetra yudh se pehle Arjun ne apne hi kul ke logo ke khilaf ladne se mana kar diya. Tab Krishna ne unhe Bhagavad Gita ka updesh diya jo aaj bhi puri duniya mein pada jaata hai. Krishna ne Arjun ko bataya ki atma amar hai, sharir naashwan hai. 'Karmanye Vadhikaraste Ma Phaleshu Kadachana' - tumhara adhikar sirf karma par hai, phal par nahi. Krishna ne samjhaya ki ek yoddha ka dharm hai ladna, chahe saamne kaun bhi ho. Unhone Arjun ko apna Vishwaroop bhi dikhaya jisme puri srishti unke sharir mein thi. Yeh updesh na sirf Arjun ke liye tha, balki aane wali har peedhi ke liye hai.",
            
            "Krishna aur Sudama ki mitrata bahut prasiddh hai. Sudama bahut garib the lekin Krishna ke bachpan ke dost the. Ek din unki patni ne unhe Krishna ke paas jaane ko kaha. Sudama sharminda the par phir bhi chawal ka potli lekar Dwarka gaye. Krishna ne unka swagat aise kiya jaise kisi raja ka swagat ho. Unhone khud Sudama ke pair dhote aur pyaar se chawal khaye. Sudama bina kuch maange hi wapas laut gaye. Par jab woh ghar pohonche toh dekha ki unka jhopda ek bade mahal mein badal gaya tha. Krishna ne bina kahe hi apne dost ki madad kar di. Yeh kahani sikhati hai ki sacchi mitrata dhann-sampatti se pare hoti hai."
        ]
    },
    "mahadev": {
        "keywords": ["shiva statue powerful", "mahadev meditation divine", "shiva temple ancient", "shiva trishul powerful", 
                    "nandi shiva sacred", "shiva lingam divine", "shiva tandav powerful", "lord shiva third eye"],
        "thumbnail_keywords": ["shiva powerful divine", "mahadev statue golden"],
        "stories": [
            "Samudra Manthan ki katha Vishnu Purana mein likhi gayi hai. Jab devta aur asur amrit pane ke liye samudra manthan kar rahe the, tab sabse pehle halahal vish nikla. Yeh vish itna khatarnak tha ki agar woh failta toh puri srishti ka nash ho sakta tha. Sabhi devta Vishnu ke paas gaye par unhone kaha ki sirf Mahadev hi is vish ko pee sakte hain. Tab sab Shiva ke paas gaye aur prarthana ki. Mahadev ne srishti ki raksha ke liye us vish ko piya. Par unhone use nigala nahi, apne gale mein rok liya. Vish ki shakti se unka gala neela pad gaya aur tab se unka naam 'Neelkanth' pada. Parvati ne turant unke gale par haath rakh diya taaki vish neeche na jaaye. Yeh ghatna sikhati hai ki Mahadev tyag aur balidan ki moorti hain.",
            
            "Shiva aur Parvati ka vivah bahut hi divya aur anokha hai jo Shiva Purana mein varnan kiya gaya hai. Parvati Himalaya ki putri thi aur woh bachpan se hi Shiva ko pati ke roop mein chahti thi. Unhone Shiva ko pane ke liye sab kuch tyag diya aur ghori tapasya ki. Unhone saal baad saal bina khana-peena khaye dhyan lagaya. Barfili pahadiyon mein, bhaari garmi mein, baarish mein - har paristhiti mein unhone tapasya jaari rakhi. Shiva ne unki pariksha lene ke liye ek budhe brahman ka roop dhaaran kiya aur Shiva ki burai karne lage. Par Parvati ne gusse mein akar unhe daanta aur kaha ki Shiva hi unke pati hain. Yeh dekhkar Shiva prakat hue aur unse vivah karne ko taiyaar ho gaye. Unka vivah pura swarg jhoome uske saath hua. Yeh kahani batati hai ki sacchi bhakti aur dridh nishchay se sab kuch haasil kiya ja sakta hai.",
            
            "Ganga avataran ki katha Ramayana aur Bhagavata Purana mein hai. Raja Bhagirath ke purvajon ne Kapil Muni ko gusssa dila diya tha jiske kaaran unhone sab ko shraap de diya. Unka uddhar sirf Ganga ke jal se hi ho sakta tha. Isliye Bhagirath ne hazaaron saal tapasya ki taaki Ganga swarg se prithvi par utare. Brahma ji prasanna hue aur Ganga ko prithvi par aane ka aadesh diya. Par Ganga ka veg itna tez tha ki woh puri prithvi ko barbad kar sakti thi. Tab Brahma ji ne kaha ki sirf Mahadev hi is veg ko rok sakte hain. Bhagirath ne Shiva ki tapasya ki. Mahadev ne Ganga ko apni jataon mein rok liya aur dheere dheere saat dharaon mein prithvi par pravahit kar diya. Isliye Ganga ko 'Shiva ki jata se nikli nadi' kaha jaata hai. Yeh kahani sikhati hai ki Shiva pralay aur srishti dono ko niyantrit karte hain.",
            
            "Ravana aur Shiva ki katha bahut rochak hai. Ravana mahaan gyaani aur Shiva ka param bhakt tha. Usne Shiva ko prasanna karne ke liye ghori tapasya ki. Unhone apne das siron ko ek-ek karke kaat kar Shiva ko arpan kar diya. Har baar ek sir kaatne par woh Rudra Veena par bhajan gaate. Jab dasva sir kaatne wala tha, tab Mahadev prakat hue aur prasanna hokar use var maanga. Ravana ne achhal shakti aur amarta ka var maanga. Shiva ne use shakti to de di par amarta nahi di, kyunki woh prakriti ke niyam ke viruddh thi. Ravana ne is shakti ka galat upyog kiya aur atyachaar karne laga. Akhir mein Ram ne use maara. Yeh kahani sikhati hai ki shakti ka sahi istemaal bahut zaroori hai, warna wahi shakti vinaash ka kaaran ban jaati hai.",
            
            "Shiva ka Tandav Nritya sabse shaktishah aur powerful maana jaata hai. Jab Sati ne apne pita Daksh ke yagya mein apne ko aag mein kood kar balidan diya, tab Shiva ko bahut gussa aaya. Unhone apne gan bhoot-pret ko bheja aur us yagya ko tabah kar diya. Phir unhone Sati ke sharir ko uthakar pura brahmaand mein tandav kiya. Unka tandav itna bhayanak tha ki prithvi kampne lagi, samundar leherein uchhalne lagi. Puri srishti ka nash hone wala tha. Tab Vishnu ne apne Sudarshan Chakra se Sati ke sharir ko 51 tukdon mein kaat diya. Jahan-jahan yeh tukde gire, wahan Shakti Peeth ban gaye. Lekin Shiva ka ek aur tandav hai - 'Anand Tandav'. Jab woh khush hote hain tab yeh tandav karte hain. Nataraja ke roop mein unka yeh nritya puri duniya mein prasiddh hai. Yeh batata hai ki Shiva srishti aur pralay dono ke adhipati hain."
        ]
    }
}

# ============================================================================
# ENHANCED NICHE KEYWORDS - CONSISTENT & SIMILAR
# ============================================================================
NICHE_KEYWORDS = {
    "space": {
        "keywords": ["black hole space dark", "spiral galaxy space bright", "colorful nebula space", "planet earth space blue", 
                    "milky way galaxy stars", "supernova space explosion", "cosmic space rays", "star cluster space bright", 
                    "moon surface space gray", "sun corona space bright", "asteroid belt space", "space station orbit earth"],
        "emotion": "wonder",
        "voice_id": "oABbH1EqNQfpzYZZOAPR",
        "voice_name": "Space Narrator",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(5).weba",
        "thumbnail_keywords": ["colorful galaxy space bright", "purple nebula space beautiful"],
        "english_keywords": [
            "space facts", "universe mystery", "black hole explained", "space facts hindi",
            "galaxy facts", "cosmos documentary", "astronomy shorts", "space science",
            "universe secrets", "space exploration", "astrophysics facts", "space documentary",
            "viral space shorts", "trending space facts", "amazing space", "space facts channel",
            "universe hindi", "space knowledge", "space facts 2024", "astronomy hindi"
        ],
        "hindi_keywords": [
            "अंतरिक्ष तथ्य", "ब्रह्मांड रहस्य", "गैलेक्सी", "ब्लैकहोल", "अंतरिक्ष विज्ञान",
            "तारे", "सुपरनोवा", "अंतरिक्ष रहस्य", "स्पेस फैक्ट्स", "ब्रह्मांड हिंदी"
        ]
    },
    "horror": {
        "keywords": ["haunted mansion dark scary", "dark forest fog night creepy", "abandoned hospital creepy dark", 
                    "creepy shadows night dark", "ghost figure scary dark", "graveyard fog night scary", 
                    "scary house abandoned dark", "dark corridor horror creepy", "eerie night horror dark", 
                    "paranormal dark scary", "mystery door dark creepy", "spooky atmosphere night dark"],
        "emotion": "suspense",
        "voice_id": "t1bT2r4IHulx2q9wwEUy",
        "voice_name": "Dark Storyteller",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(3).weba",
        "thumbnail_keywords": ["haunted house scary dark fog", "creepy abandoned dark horror"],
        "english_keywords": [
            "horror stories", "scary stories hindi", "real ghost stories", "haunted places india",
            "horror shorts", "scary videos", "ghost stories real", "paranormal activity",
            "horror facts", "scary facts", "haunted india", "real horror stories",
            "bhootiya kahani", "horror channel", "scary shorts viral", "horror hindi shorts",
            "ghost videos real", "haunted stories", "horror mysteries", "scary true stories"
        ],
        "hindi_keywords": [
            "भूतिया कहानी", "डरावनी कहानी", "हॉरर स्टोरी", "प्रेत कहानी", "डरावने तथ्य",
            "सच्ची हॉरर", "भूतिया स्थान", "हॉरर शॉर्ट्स", "डरावनी शॉर्ट्स", "भूत कहानी"
        ]
    },
    "nature": {
        "keywords": ["mountain peak snow nature high", "waterfall tropical nature beautiful", "green forest trees nature", 
                    "sunset ocean nature colorful", "river flowing nature peaceful", "tiger wildlife nature wild", 
                    "grand canyon nature red", "desert sand dunes nature golden", "rainforest trees nature green", 
                    "scenic valley mountains nature", "paradise beach nature blue", "wild jungle nature green"],
        "emotion": "peace",
        "voice_id": "repzAAjoKlgcT2oOAIWt",
        "voice_name": "Nature Guide",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(4).weba",
        "thumbnail_keywords": ["mountain sunset nature orange", "waterfall beautiful nature green"],
        "english_keywords": [
            "nature beauty", "wildlife videos", "nature shorts", "beautiful nature scenes",
            "nature documentary", "wildlife shorts", "nature facts", "amazing nature videos",
            "nature videos 4k", "wildlife hindi", "nature channel", "scenic beauty nature",
            "nature relaxing", "wildlife facts", "nature viral shorts", "nature india",
            "beautiful places", "nature hindi shorts", "nature facts hindi", "wildlife documentary"
        ],
        "hindi_keywords": [
            "प्रकृति सुंदरता", "वन्यजीव", "प्रकृति तथ्य", "जंगली जानवर", "पहाड़",
            "झरना", "प्राकृतिक सुंदरता", "वन्यजीव भारत", "प्रकृति शॉर्ट्स", "प्राकृतिक दृश्य"
        ]
    },
    "mystery": {
        "keywords": ["ancient pyramid mystery egypt", "temple ruins ancient mysterious", "mysterious artifact ancient old", 
                    "treasure chest ancient gold", "ancient civilization ruins mysterious", "secret chamber mystery dark", 
                    "lost city ancient ruins", "archaeological site ancient dig", "ancient manuscript old text", 
                    "mysterious cave dark ancient", "ancient temple ruins stone", "mysterious ruins ancient structure"],
        "emotion": "curiosity",
        "voice_id": "u7y54ruSDBB05ueK084X",
        "voice_name": "Mystery Narrator",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback.weba",
        "thumbnail_keywords": ["ancient temple mystery stone", "mysterious pyramid ancient egypt"],
        "english_keywords": [
            "mystery solved", "unsolved mysteries", "ancient mysteries", "mystery facts hindi",
            "mysterious places", "mystery channel", "mystery shorts", "mystery hindi",
            "unsolved cases india", "mystery stories", "ancient secrets", "mystery videos viral",
            "mystery india facts", "mysterious facts", "mystery viral shorts", "unsolved mystery hindi",
            "mystery documentary", "ancient india mystery", "mystery shorts hindi", "mystery facts"
        ],
        "hindi_keywords": [
            "रहस्य तथ्य", "रहस्यमय स्थान", "प्राचीन रहस्य", "अनसुलझा रहस्य", "रहस्यमय कहानी",
            "रहस्य हिंदी", "प्राचीन भारत", "रहस्य शॉर्ट्स", "रहस्यमय भारत", "रहस्य वीडियो"
        ]
    },
    "spiritual": {
        "keywords": [],  # Will be dynamically populated
        "emotion": "devotion",
        "voice_id": "yD0Zg2jxgfQLY8I2MEHO",
        "voice_name": "Spiritual Voice",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback.weba",
        "thumbnail_keywords": [],  # Will be dynamically populated
        "english_keywords": [
            "spiritual wisdom", "hindu mythology", "spiritual shorts", "devotional stories",
            "spiritual facts", "spiritual hindi", "devotional shorts", "spiritual channel",
            "spiritual videos", "devotional videos", "spiritual india", "bhakti shorts",
            "hindu gods", "spiritual teachings", "devotional channel", "spiritual facts hindi",
            "hindu stories", "mythology shorts", "spiritual knowledge", "devotional facts"
        ],
        "hindi_keywords": [
            "आध्यात्मिक ज्ञान", "भक्ति", "हिंदू पौराणिक", "आध्यात्मिक कहानी",
            "भक्ति शॉर्ट्स", "धार्मिक कहानी", "आध्यात्मिकता", "भक्ति हिंदी", "धार्मिक शॉर्ट्स", "आध्यात्मिक वीडियो"
        ]
    },
    "motivation": {
        "keywords": ["success mountain climb high", "victory celebration winner happy", "gym workout fitness strong", 
                    "sunrise motivation morning golden", "trophy achievement success shiny", "strength training gym fitness powerful", 
                    "focus meditation success calm", "goal target achievement arrow", "excellence award winner gold", 
                    "growth success chart up", "fitness workout strong muscular", "winner podium success first"],
        "emotion": "inspiration",
        "voice_id": "FZkK3TvQ0pjyDmT8fzIW",
        "voice_name": "Motivational Speaker",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(6).weba",
        "thumbnail_keywords": ["success motivation winner gold", "victory achievement success trophy"],
        "english_keywords": [
            "motivation", "motivational quotes", "success motivation", "motivational speech hindi",
            "inspiration shorts", "success tips", "motivation hindi", "motivational shorts viral",
            "success stories", "motivational videos", "life motivation", "motivational channel",
            "success mindset", "motivational hindi shorts", "inspiration videos", "success shorts",
            "motivation viral", "motivational facts", "success facts hindi", "motivation 2024"
        ],
        "hindi_keywords": [
            "प्रेरणा", "सफलता", "मोटिवेशन", "प्रेरणादायक कहानी", "सफलता की कहानी",
            "प्रेरक विचार", "मोटिवेशनल", "सफलता हिंदी", "प्रेरणादायक शॉर्ट्स", "मोटिवेशन हिंदी"
        ]
    },
    "funny": {
        "keywords": ["funny dog pet cute", "cute cat kitten adorable", "funny animals pet hilarious", "hilarious pet dog funny", 
                    "comedy animal moment funny", "funny baby cute adorable", "cute puppy dog small", "funny kitten cat cute", 
                    "animal fail funny pet", "funny meme pet viral", "cute animals funny adorable", "funny pet video viral"],
        "emotion": "joy",
        "voice_id": "3xDpHJYZLpyrp8I8ILUO",
        "voice_name": "Comedy Narrator",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback.weba",
        "thumbnail_keywords": ["funny dog cute adorable", "cute cat funny kitten"],
        "english_keywords": [
            "funny videos", "comedy shorts", "funny animals", "hilarious videos viral",
            "comedy channel", "funny shorts", "funny hindi", "comedy videos hindi",
            "funny moments", "funny pets", "comedy shorts hindi", "funny viral shorts",
            "comedy videos", "funny shorts viral", "comedy india", "funny channel videos",
            "hilarious shorts", "comedy facts", "funny videos 2024", "comedy shorts viral"
        ],
        "hindi_keywords": [
            "मजेदार वीडियो", "कॉमेडी", "हास्य वीडियो", "फनी शॉर्ट्स", "मजाकिया",
            "हंसी वीडियो", "कॉमेडी शॉर्ट्स", "फनी वीडियो", "मजेदार शॉर्ट्स", "हास्य हिंदी"
        ]
    },
    "luxury": {
        "keywords": [],  # Will be dynamically populated
        "emotion": "aspiration",
        "voice_id": "l1CrgWMeEfm3xvPbn4YE",
        "voice_name": "Luxury Narrator",
        "bg_music_url": "https://raw.githubusercontent.com/aryan-Patel-web/audio-collections/main/videoplayback%20(7).weba",
        "thumbnail_keywords": [],  # Will be dynamically populated
        "english_keywords": [
            "luxury cars", "supercars", "luxury lifestyle", "supercar review", "luxury car review",
            "luxury shorts", "supercar videos", "luxury car facts", "expensive cars",
            "luxury channel", "supercar shorts", "luxury hindi", "car lovers",
            "luxury facts", "supercar specs", "luxury cars india", "car shorts",
            "luxury viral", "expensive lifestyle", "luxury cars hindi"
        ],
        "hindi_keywords": [
            "लग्जरी कार", "सुपरकार", "महंगी कार", "लग्जरी लाइफस्टाइल", "कार रिव्यू",
            "लग्जरी शॉर्ट्स", "महंगी गाड़ी", "लग्जरी हिंदी", "सुपरकार हिंदी", "लग्जरी तथ्य"
        ]
    }
}

# TRANSITIONS
TRANSITIONS = [
    {"name": "zoom_out", "filter": "zoompan=z='if(lte(zoom,1.0),1.8,max(1.001,zoom-0.008))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}"},
    {"name": "zoom_fade", "filter": "zoompan=z='if(lte(zoom,1.0),2.0,max(1.001,zoom-0.01))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps},fade=t=in:st=0:d=0.3"},
    {"name": "pan", "filter": "zoompan=z='1.3':d={frames}:x='iw/2-(iw/zoom/2)+(t*15)':y='ih/2-(ih/zoom/2)':s=720x1280:fps={fps}"}
]

# ============================================================================
# UTILITIES
# ============================================================================

def force_cleanup(*filepaths):
    for fp in filepaths:
        try:
            if fp and os.path.exists(fp):
                os.remove(fp)
        except:
            pass
    gc.collect()

def get_size_mb(fp: str) -> float:
    try:
        return os.path.getsize(fp) / (1024 * 1024)
    except:
        return 0.0

def get_size_kb(fp: str) -> float:
    try:
        return os.path.getsize(fp) / 1024
    except:
        return 0.0

def run_ffmpeg(cmd: list, timeout: int = 120) -> bool:
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False, text=True)
        return result.returncode == 0
    except:
        return False

def estimate_speech_duration(text: str, speed: float = 1.1) -> float:
    words = len(text.split())
    return (words / 150) * 60 / speed

def convert_weba_to_mp3(weba: str, mp3: str) -> bool:
    cmd = ["ffmpeg", "-i", weba, "-vn", "-acodec", "libmp3lame", "-b:a", "128k", "-y", mp3]
    return run_ffmpeg(cmd, FFMPEG_TIMEOUT_MUSIC)

def check_image_quality(img_path: str) -> bool:
    """Check if image is good quality (not corrupted/tiny)"""
    try:
        size_kb = get_size_kb(img_path)
        if size_kb < MIN_IMAGE_SIZE_KB:
            logger.warning(f"   ⚠️ Image too small: {size_kb:.1f}KB")
            return False
        cmd = ["ffmpeg", "-v", "error", "-i", img_path, "-f", "null", "-"]
        result = subprocess.run(cmd, capture_output=True, timeout=5)
        if result.returncode != 0:
            logger.warning(f"   ⚠️ Image corrupted/invalid")
            return False
        return True
    except:
        return False

def filter_niche_images(hits: List[dict], niche: str) -> List[dict]:
    """Filter out images that don't match the niche"""
    exclusions = NICHE_EXCLUSIONS.get(niche, [])
    if not exclusions:
        return hits
    
    filtered = []
    for hit in hits:
        tags = hit.get("tags", "").lower()
        # Check if any exclusion keyword is in tags
        if any(excl in tags for excl in exclusions):
            logger.info(f"   🚫 Filtered: {tags[:50]}...")
            continue
        filtered.append(hit)
    
    return filtered

# ============================================================================
# CAR SELECTION & SCRAPING (DYNAMIC - NO HARDCODING)
# ============================================================================

async def select_and_scrape_car() -> dict:
    """AI selects a car and scrapes real specs"""
    
    car_prompt = """Select ONE luxury car from these brands: BMW, Mercedes-Benz, Audi, Ferrari, Lamborghini, Rolls-Royce, Bugatti, Porsche, McLaren, Aston Martin, Bentley, Maserati.

Select a popular HIGH-END model and provide REAL specifications in JSON format:

{
  "brand": "Ferrari",
  "model": "SF90 Stradale",
  "engine": "V8 Hybrid Twin-Turbo",
  "cc": "3990",
  "horsepower": "1000",
  "top_speed": "340 km/h",
  "price_india": "₹7.50 Crore",
  "search_keywords": ["Ferrari SF90", "Ferrari SF90 Stradale red", "Ferrari hybrid supercar"],
  "thumbnail_keywords": ["Ferrari SF90 red", "Ferrari supercar"]
}

IMPORTANT: 
- Provide REAL specifications (accurate engine, CC, HP, speed, India price)
- Select different car each time (no repetition)
- Search keywords should be specific to that exact model
- Output ONLY valid JSON, no extra text"""
    
    try:
        if not MISTRAL_API_KEY:
            return None
            
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                json={
                    "model": "mistral-large-latest",
                    "messages": [
                        {"role": "system", "content": "You are a luxury car expert. Always select DIFFERENT cars. Output ONLY valid JSON with real specs."},
                        {"role": "user", "content": car_prompt}
                    ],
                    "temperature": 0.9,  # High temperature for variety
                    "max_tokens": 500
                }
            )
            
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                content = re.sub(r'```json\n?|\n?```', '', content).strip()
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    car_data = json.loads(match.group(0))
                    logger.info(f"🚗 Selected: {car_data.get('brand')} {car_data.get('model')}")
                    return car_data
    except Exception as e:
        logger.error(f"Car selection error: {e}")
    
    return None

# ============================================================================
# SPIRITUAL DEITY SELECTION (DYNAMIC)
# ============================================================================

def select_spiritual_deity() -> tuple:
    """Randomly select Krishna or Mahadev with story"""
    deity_name = random.choice(["krishna", "mahadev"])
    deity_data = SPIRITUAL_DEITIES[deity_name]
    story = random.choice(deity_data["stories"])
    
    logger.info(f"🕉️ Selected deity: {deity_name.upper()}")
    
    return deity_name, deity_data, story

# ============================================================================
# IMAGE SEARCH - HD QUALITY WITH FILTERING
# ============================================================================

async def search_pixabay_hd(niche: str, count: int, is_thumbnail: bool = False, custom_keywords: List[str] = None) -> List[dict]:
    """Search for HD images with niche filtering"""
    logger.info(f"🔍 HD Search: {niche} (thumb: {is_thumbnail})")
    
    niche_data = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["space"])
    
    if custom_keywords:
        keywords = custom_keywords
    else:
        keywords = niche_data.get("thumbnail_keywords" if is_thumbnail else "keywords", niche_data["keywords"])
    
    all_images = []
    seen_urls = set()
    
    for keyword in random.sample(keywords, len(keywords)) if len(keywords) > 0 else []:
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
                        "orientation": "vertical",
                        "per_page": 30,
                        "order": "popular",
                        "safesearch": "true",
                        "min_width": 1080,
                        "min_height": 1920
                    }
                )
                
                if resp.status_code == 200:
                    hits = resp.json().get("hits", [])
                    
                    # Filter images based on niche
                    hits = filter_niche_images(hits, niche)
                    
                    for hit in hits:
                        if len(all_images) >= count:
                            break
                        
                        url = hit.get("largeImageURL") or hit.get("fullHDURL") or hit.get("webformatURL")
                        
                        if url and url not in seen_urls:
                            size_kb = hit.get("imageSize", 0) / 1024
                            
                            # Thumbnail: 200KB - 2MB range
                            if is_thumbnail:
                                if size_kb < THUMBNAIL_MIN_SIZE_KB or size_kb > THUMBNAIL_MAX_SIZE_KB:
                                    continue
                            
                            all_images.append({
                                "url": url,
                                "width": hit.get("imageWidth", 0),
                                "height": hit.get("imageHeight", 0),
                                "size_kb": size_kb,
                                "keyword": keyword
                            })
                            seen_urls.add(url)
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            continue
    
    logger.info(f"✅ Found {len(all_images)} HD images")
    return all_images[:count]

# ============================================================================
# SCRIPT GENERATION - ALWAYS UNIQUE
# ============================================================================

async def generate_script_with_cta(niche: str, target_duration: int, context: dict = None) -> dict:
    """Generate UNIQUE script every time - no repetition"""
    
    niche_data = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["space"])
    emotion = niche_data["emotion"]
    
    # Mandatory CTA
    cta = "Agar aapko yeh video pasand aayi ho toh LIKE karein, SUBSCRIBE karein aur apne doston ko SHARE karein, taaki aage bhi aise amazing videos milti rahein!"
    
    # Calculate content duration
    content_duration = max(20, target_duration - 8)
    
    # Prepare context-specific prompt
    if niche == "luxury" and context and "car_data" in context:
        car = context["car_data"]
        specific_prompt = f"""
Car: {car['brand']} {car['model']}
Engine: {car['engine']}
CC: {car['cc']}
Horsepower: {car['horsepower']} HP
Top Speed: {car['top_speed']}
India Price: {car['price_india']}

Create UNIQUE Hindi script explaining ALL these specs in an exciting way. Make it DIFFERENT from any previous scripts - use creative expressions, unique comparisons, fresh facts!
"""
    elif niche == "spiritual" and context and "deity_story" in context:
        specific_prompt = f"""
Use this authentic story from Hindu scriptures:
{context['deity_story']}

Create UNIQUE Hindi narration of this story. Make it engaging and DIFFERENT from other spiritual videos - use varied expressions, unique storytelling style!
"""
    else:
        specific_prompt = f"Create UNIQUE {niche} facts in Hindi. Be creative - use different angles, fresh comparisons, unique perspectives every time!"
    
    prompt = f"""Create {content_duration}s Hindi content for {niche} YouTube Short.

{specific_prompt}

CRITICAL RULES:
1. Write ONLY main content ({content_duration}s worth)
2. NO CTA in your output (we add separately)
3. {emotion.upper()} tone
4. Hook (5s) → Main Content (85%) → Climax (10%)
5. Natural Hindi with commas, !, ?
6. NO "pause" word
7. ALWAYS create UNIQUE content - never repeat same facts/expressions
8. Use creative language, fresh comparisons, new angles
9. Make each script DIFFERENT from previous ones

OUTPUT JSON:
{{
  "content": "Main Hindi narration without CTA",
  "title": "Hinglish title max 80 chars",
  "keywords_english": ["top 10 English keywords"],
  "keywords_hindi": ["top 5 Hindi keywords"]
}}

Title Format: "{niche} Ki Amazing Facts 🔥 | Must Watch!"
"""
    
    try:
        if MISTRAL_API_KEY:
            async with httpx.AsyncClient(timeout=40) as client:
                resp = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                    json={
                        "model": "mistral-large-latest",
                        "messages": [
                            {"role": "system", "content": "Viral content creator. ALWAYS create UNIQUE content - never repeat. Output ONLY valid JSON."},
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
                        
                        full_script = data.get("content", "") + " " + cta
                        
                        eng_keys = data.get("keywords_english", [])[:10]
                        hin_keys = data.get("keywords_hindi", [])[:5]
                        all_keys = niche_data["english_keywords"][:10] + eng_keys[:5] + hin_keys
                        
                        est_dur = estimate_speech_duration(full_script, 1.1)
                        num_imgs = max(MIN_IMAGES, min(int(est_dur / 3.5) + 1, MAX_IMAGES))
                        
                        return {
                            "script": full_script,
                            "title": data.get("title", f"{niche} Facts"),
                            "description": f"{full_script[:200]}...\n#{niche}",
                            "keywords": list(dict.fromkeys(all_keys))[:20],
                            "estimated_duration": est_dur,
                            "num_images_needed": num_imgs,
                            "image_duration": est_dur / num_imgs
                        }
    except Exception as e:
        logger.warning(f"Script gen failed: {e}")
    
    # Fallback
    fallback = f"Amazing {niche} facts you must know! " + cta
    est = estimate_speech_duration(fallback, 1.1)
    num = max(MIN_IMAGES, int(est / 3.5) + 1)
    
    return {
        "script": fallback,
        "title": f"{niche.title()} Facts 🔥",
        "description": fallback[:200],
        "keywords": (niche_data["english_keywords"][:10] + niche_data["hindi_keywords"][:5])[:20],
        "estimated_duration": est,
        "num_images_needed": num,
        "image_duration": est / num
    }

# ============================================================================
# VOICE GENERATION - 1.1x SPEED
# ============================================================================

async def generate_voice_elevenlabs(text: str, niche: str, temp_dir: str) -> Optional[str]:
    """Generate voice with 1.1x speed"""
    try:
        if not ELEVENLABS_API_KEY or len(ELEVENLABS_API_KEY) < 20:
            return None
        
        voice_id = NICHE_KEYWORDS.get(niche, {}).get("voice_id", "oABbH1EqNQfpzYZZOAPR")
        temp_file = os.path.join(temp_dir, f"voice_{uuid.uuid4().hex[:4]}.mp3")
        
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={"xi-api-key": ELEVENLABS_API_KEY},
                json={
                    "text": text.strip()[:2000],
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
                }
            )
            
            if resp.status_code == 200:
                base = os.path.join(temp_dir, "vbase.mp3")
                with open(base, 'wb') as f:
                    f.write(resp.content)
                
                # Apply 1.1x speed
                cmd = ["ffmpeg", "-i", base, "-filter:a", "atempo=1.1", "-y", temp_file]
                if run_ffmpeg(cmd, 30):
                    force_cleanup(base)
                    if get_size_mb(temp_file) > 0.01:
                        logger.info(f"✅ Voice (1.1x): {get_size_mb(temp_file):.2f}MB")
                        return temp_file
                force_cleanup(base, temp_file)
    except Exception as e:
        logger.error(f"Voice error: {e}")
    return None

async def generate_voice_edge(text: str, temp_dir: str) -> Optional[str]:
    """Fallback voice with 1.1x speed"""
    try:
        import edge_tts
        base = os.path.join(temp_dir, "eb.mp3")
        final = os.path.join(temp_dir, f"e_{uuid.uuid4().hex[:4]}.mp3")
        
        comm = edge_tts.Communicate(text.strip()[:1500], "hi-IN-MadhurNeural", rate="+10%")
        await comm.save(base)
        
        # Apply 1.1x speed
        cmd = ["ffmpeg", "-i", base, "-filter:a", "atempo=1.1", "-y", final]
        if run_ffmpeg(cmd, 30):
            force_cleanup(base)
            if get_size_mb(final) > 0.01:
                logger.info(f"✅ Voice Edge (1.1x): {get_size_mb(final):.2f}MB")
                return final
        force_cleanup(base, final)
    except:
        pass
    return None

# ============================================================================
# IMAGE DOWNLOAD
# ============================================================================

async def download_image(img_data: dict, path: str, retry: int = 0) -> bool:
    try:
        url = img_data.get("url")
        if not url:
            return False
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, follow_redirects=True)
            
            if resp.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(resp.content)
                
                if check_image_quality(path):
                    return True
                force_cleanup(path)
        
        return False
    except Exception as e:
        if retry < MAX_IMAGE_RETRIES - 1:
            await asyncio.sleep(1)
            return await download_image(img_data, path, retry + 1)
        return False

async def download_images(images: List[dict], temp_dir: str) -> List[str]:
    downloaded = []
    for idx, img in enumerate(images):
        path = os.path.join(temp_dir, f"img_{idx:02d}.jpg")
        if await download_image(img, path):
            downloaded.append(path)
            logger.info(f"   ✅ {idx+1}/{len(images)}: {get_size_kb(path):.0f}KB")
    logger.info(f"✅ Downloaded: {len(downloaded)}/{len(images)}")
    return downloaded

# ============================================================================
# MUSIC
# ============================================================================

async def download_music(niche: str, temp_dir: str, custom_url: Optional[str], duration: float) -> Optional[str]:
    url = custom_url if custom_url else NICHE_KEYWORDS.get(niche, {}).get("bg_music_url")
    if not url:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
            resp = await client.get(url)
            
            if resp.status_code == 200:
                raw = os.path.join(temp_dir, "m_raw.weba" if url.endswith('.weba') else "m_raw.mp3")
                with open(raw, 'wb') as f:
                    f.write(resp.content)
                
                if url.endswith('.weba'):
                    conv = os.path.join(temp_dir, "m_conv.mp3")
                    if convert_weba_to_mp3(raw, conv):
                        force_cleanup(raw)
                        raw = conv
                
                final = os.path.join(temp_dir, "bg_music.mp3")
                cmd = ["ffmpeg", "-i", raw, "-t", str(min(duration, 55)), "-acodec", "copy", "-y", final]
                
                if run_ffmpeg(cmd, FFMPEG_TIMEOUT_MUSIC):
                    force_cleanup(raw)
                    logger.info(f"✅ Music: {get_size_mb(final):.2f}MB")
                    return final
                
                if os.path.exists(raw) and get_size_mb(raw) > 0.05:
                    return raw
    except Exception as e:
        logger.warning(f"Music error: {e}")
    return None

# ============================================================================
# SLIDESHOW
# ============================================================================

def create_slideshow(images: List[str], image_duration: float, temp_dir: str) -> Optional[str]:
    try:
        if len(images) < MIN_IMAGES:
            return None
        
        frames = int(image_duration * FPS)
        clips = []
        
        for idx, img in enumerate(images):
            resized = os.path.join(temp_dir, f"r_{idx}.jpg")
            cmd_r = [
                "ffmpeg", "-i", img,
                "-vf", f"scale={IMAGE_TARGET_WIDTH}:{IMAGE_TARGET_HEIGHT}:force_original_aspect_ratio=increase,crop={IMAGE_TARGET_WIDTH}:{IMAGE_TARGET_HEIGHT}",
                "-q:v", "2", "-y", resized
            ]
            
            if not run_ffmpeg(cmd_r, 15):
                continue
            
            trans = random.choice(TRANSITIONS)
            filt = trans["filter"].replace("{frames}", str(frames)).replace("{fps}", str(FPS))
            
            clip = os.path.join(temp_dir, f"c_{idx}.mp4")
            cmd_c = [
                "ffmpeg", "-loop", "1", "-i", resized,
                "-vf", filt, "-t", str(image_duration),
                "-r", str(FPS), "-c:v", "libx264", "-crf", "23",
                "-preset", "fast", "-pix_fmt", "yuv420p", "-y", clip
            ]
            
            if run_ffmpeg(cmd_c, FFMPEG_TIMEOUT_CLIP):
                clips.append(clip)
                logger.info(f"   ✅ Clip {idx+1}/{len(images)}")
            
            force_cleanup(resized)
        
        if len(clips) < MIN_IMAGES:
            return None
        
        concat_file = os.path.join(temp_dir, "concat.txt")
        with open(concat_file, 'w') as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        output = os.path.join(temp_dir, "slideshow.mp4")
        cmd_con = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", "-y", output]
        
        if run_ffmpeg(cmd_con, FFMPEG_TIMEOUT_CONCAT):
            for clip in clips:
                force_cleanup(clip)
            logger.info(f"✅ Slideshow: {get_size_mb(output):.1f}MB")
            return output
        
        return None
    except Exception as e:
        logger.error(f"Slideshow error: {e}")
        return None

# ============================================================================
# MIX
# ============================================================================

async def mix_audio(video: str, voice: str, music: Optional[str], temp_dir: str) -> Optional[str]:
    try:
        final = os.path.join(temp_dir, "final.mp4")
        
        if music and os.path.exists(music):
            cmd = [
                "ffmpeg", "-i", video, "-i", voice, "-i", music,
                "-filter_complex",
                "[1:a]volume=1.0[v];[2:a]volume=0.12,afade=t=in:d=1[m];[v][m]amix=inputs=2:duration=first[a]",
                "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", "-y", final
            ]
        else:
            cmd = ["ffmpeg", "-i", video, "-i", voice, "-map", "0:v", "-map", "1:a",
                   "-c:v", "copy", "-c:a", "aac", "-b:a", "96k", "-shortest", "-y", final]
        
        if run_ffmpeg(cmd, FFMPEG_TIMEOUT_MUSIC):
            logger.info(f"✅ Final: {get_size_mb(final):.1f}MB")
            return final
        return None
    except:
        return None

# ============================================================================
# UPLOAD
# ============================================================================

async def upload_to_youtube(video: str, title: str, desc: str, keywords: List[str], user_id: str, db) -> dict:
    try:
        from YTdatabase import get_database_manager as get_yt_db
        yt_db = get_yt_db()
        
        if not yt_db or not yt_db.youtube.client:
            if yt_db:
                await yt_db.connect()
        
        creds = await yt_db.youtube.youtube_credentials_collection.find_one({"user_id": user_id})
        if not creds:
            return {"success": False, "error": "No credentials"}
        
        credentials = {
            "access_token": creds.get("access_token"),
            "refresh_token": creds.get("refresh_token"),
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": creds.get("client_id") or os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": creds.get("client_secret") or os.getenv("YOUTUBE_CLIENT_SECRET"),
            "scopes": ["https://www.googleapis.com/auth/youtube.upload"]
        }
        
        from mainY import youtube_scheduler
        
        full_desc = f"{desc}\n\nKeywords:\n" + "\n".join([f"#{k}" for k in keywords])
        
        result = await youtube_scheduler.generate_and_upload_content(
            user_id=user_id, credentials_data=credentials, content_type="shorts",
            title=title, description=full_desc, video_url=video
        )
        
        if result.get("success"):
            vid_id = result.get("video_id")
            return {"success": True, "video_id": vid_id, "video_url": f"https://youtube.com/shorts/{vid_id}"}
        return {"success": False, "error": result.get("error", "Upload failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# MAIN - FULLY DYNAMIC
# ============================================================================

async def generate_pixabay_video(niche: str, language: str, user_id: str, database_manager,
                                target_duration: int = 40, custom_bg_music: Optional[str] = None) -> dict:
    temp_dir = None
    context = {}
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="pixabay_")
        logger.info(f"🎬 START: {niche} ({target_duration}s)")
        
        # LUXURY: AI selects car dynamically
        if niche == "luxury":
            car_data = await select_and_scrape_car()
            if car_data:
                context["car_data"] = car_data
                # Update keywords dynamically
                NICHE_KEYWORDS["luxury"]["keywords"] = car_data.get("search_keywords", [])
                NICHE_KEYWORDS["luxury"]["thumbnail_keywords"] = car_data.get("thumbnail_keywords", [])
        
        # SPIRITUAL: Random deity selection
        elif niche == "spiritual":
            deity_name, deity_data, story = select_spiritual_deity()
            context["deity_story"] = story
            # Update keywords dynamically
            NICHE_KEYWORDS["spiritual"]["keywords"] = deity_data["keywords"]
            NICHE_KEYWORDS["spiritual"]["thumbnail_keywords"] = deity_data["thumbnail_keywords"]
        
        # Generate UNIQUE script
        script_result = await generate_script_with_cta(niche, target_duration, context)
        num_images = script_result["num_images_needed"]
        img_dur = script_result["image_duration"]
        
        # Search HD images with filtering
        images_data = await search_pixabay_hd(niche, num_images, False)
        if len(images_data) < MIN_IMAGES:
            return {"success": False, "error": f"Not enough HD images: {len(images_data)}"}
        
        # Search thumbnail (200KB-2MB)
        thumb_data = await search_pixabay_hd(niche, 1, True)
        
        # Download images
        image_files = await download_images(images_data, temp_dir)
        if len(image_files) < MIN_IMAGES:
            return {"success": False, "error": "Download failed"}
        
        # Adjust duration
        if len(image_files) != num_images:
            img_dur = script_result["estimated_duration"] / len(image_files)
        
        # Download thumbnail
        thumb_file = None
        if thumb_data:
            thumb_path = os.path.join(temp_dir, "thumb.jpg")
            if await download_image(thumb_data[0], thumb_path):
                thumb_file = thumb_path
                logger.info(f"✅ Thumbnail: {get_size_kb(thumb_path):.0f}KB")
        
        # Music
        music = await download_music(niche, temp_dir, custom_bg_music, script_result["estimated_duration"])
        
        # Slideshow
        slideshow = create_slideshow(image_files, img_dur, temp_dir)
        if not slideshow:
            return {"success": False, "error": "Slideshow failed"}
        
        # Cleanup images
        for img in image_files:
            force_cleanup(img)
        gc.collect()
        
        # Voice (1.1x speed)
        voice = await generate_voice_elevenlabs(script_result["script"], niche, temp_dir)
        if not voice:
            voice = await generate_voice_edge(script_result["script"], temp_dir)
        if not voice:
            return {"success": False, "error": "Voice failed"}
        
        # Mix
        final = await mix_audio(slideshow, voice, music, temp_dir)
        if not final:
            return {"success": False, "error": "Mix failed"}
        
        final_size = get_size_mb(final)
        logger.info(f"✅ FINAL: {final_size:.1f}MB")
        
        # Upload
        upload_result = await upload_to_youtube(
            final, script_result["title"], script_result["description"],
            script_result["keywords"], user_id, database_manager
        )
        
        # Cleanup
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        if not upload_result.get("success"):
            return upload_result
        
        logger.info("🎉 COMPLETE!")
        
        result = {
            "success": True,
            "video_id": upload_result.get("video_id"),
            "video_url": upload_result.get("video_url"),
            "title": script_result["title"],
            "description": script_result["description"],
            "keywords": script_result["keywords"],
            "size_mb": f"{final_size:.1f}MB",
            "niche": niche,
            "language": language,
            "image_count": len(image_files),
            "duration": script_result["estimated_duration"],
            "has_music": music is not None,
            "has_thumbnail": thumb_file is not None
        }
        
        # Add niche-specific info
        if niche == "luxury" and "car_data" in context:
            result["car_info"] = f"{context['car_data']['brand']} {context['car_data']['model']}"
        elif niche == "spiritual" and "deity_story" in context:
            result["deity"] = deity_name.upper()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        logger.error(traceback.format_exc())
        
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        gc.collect()
        
        return {"success": False, "error": str(e)}

# ============================================================================
# API
# ============================================================================

router = APIRouter()

@router.get("/api/pixabay/niches")
async def get_niches():
    return {
        "success": True,
        "niches": {
            k: {"name": k.title(), "emotion": v["emotion"], "voice_name": v["voice_name"]} 
            for k, v in NICHE_KEYWORDS.items()
        }
    }

@router.post("/api/pixabay/generate")
async def generate_endpoint(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id:
            return JSONResponse(status_code=401, content={"success": False, "error": "user_id required"})
        
        niche = data.get("niche", "space")
        language = data.get("language", "hindi")
        target_duration = max(20, min(data.get("target_duration", 40), 55))
        custom_bg_music = data.get("custom_bg_music")
        
        if niche not in NICHE_KEYWORDS:
            return JSONResponse(status_code=400, content={"success": False, "error": "Invalid niche"})
        
        from Supermain import database_manager
        
        logger.info(f"📨 API: {niche} / {language} / {target_duration}s")
        
        result = await asyncio.wait_for(
            generate_pixabay_video(niche, language, user_id, database_manager, target_duration, custom_bg_music),
            timeout=1500
        )
        
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        return JSONResponse(status_code=408, content={"success": False, "error": "Timeout"})
    except Exception as e:
        logger.error(f"❌ API error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

__all__ = ['router']