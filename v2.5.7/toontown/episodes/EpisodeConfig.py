import collections
from toontown.toonbase import TTLocalizer, ToontownGlobals
episodes = collections.OrderedDict()
episodes['gyro_tale'] = {'name': TTLocalizer.EpisodeGyroPt1, 
   'desc': TTLocalizer.EpisodeGyroPt1Desc, 
   'defaultZoneId': ToontownGlobals.ToontownCentral, 
   'thumbnail': 'gyro_episode_thumbnail.jpg', 
   'toon': {'name': 'Gyro Gearloose', 
            'dna': ('iss', 'ls', 'l', 'm', 0, 0, 0, 0, 209, 27, 192, 27, 90, 27)}}
episodes['prologue'] = {'name': TTLocalizer.EpisodePrologue, 
   'desc': TTLocalizer.EpisodePrologueDesc, 
   'defaultZoneId': ToontownGlobals.ScroogeBank, 
   'thumbnail': 'prologue_thumbnail.jpg', 
   'toon': {'name': 'Scrooge McDuck', 
            'dna': ('oll', 'ls', 's', 'm', 0, 0, 9, 0, 165, 27, 152, 27, 68, 27)}}
episodes['squirting_flower'] = {'name': TTLocalizer.EpisodeSquirtingFlower, 
   'desc': TTLocalizer.EpisodeSquirtingFlowerDesc, 
   'defaultZoneId': ToontownGlobals.OldDaisyGardens, 
   'thumbnail': 'squirting_flower_thumbnail.jpg', 
   'toon': {'name': 'Coach Zucchini', 
            'dna': ('fls', 'ls', 'm', 'm', 10, 0, 10, 10, 0, 12, 0, 12, 1, 1)}}
episodes['short_work'] = {'name': TTLocalizer.EpisodeCogHighrise, 
   'desc': TTLocalizer.EpisodeCogHighriseDesc, 
   'defaultZoneId': ToontownGlobals.CashbotHQ, 
   'thumbnail': 'cog_highrise_thumbnail.jpg', 
   'toon': {'name': 'Short Change', 
            'dna': ('dss', 'ms', 'm', 'm', 0, 0, 0, 0, 0, 27, 0, 27, 0, 27)}}