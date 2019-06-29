# Toontown Offline
#
# This is the PRC configuration file for public releases of the game.
# It's rather similar to the dev PRC, but w/ some unneeded options removed.
#
# Last modified: 05/19/2018

# Client settings
window-title Toontown Offline
server-version ttoff-2.5.7
sync-video #f
want-dev #f
preload-avatars #t
texture-anisotropic-degree 16
audio-library-name null
video-library-name p3ffmpeg
smooth-lag 0.4
# Pretty sure you're gonna want membership...
want-membership #t
csmud-secret 4bdd8f51f1885282047b8c1b08e72c7bb6b4dc667cf4c814c3f81e0a06f7ce6d

# Notify
notify-level-tiff error
notify-level-dxgsg warning
notify-level-gobj warning
notify-level-loader warning
notify-level-chan fatal
notify-level-pgraph error
notify-level-collide error
notify-level-abs error
notify-level-Actor error
notify-level-DisplayOptions warning
notify-level-text warning
notify-level-audio warning
notify-level-pnmtext warning
notify-level-dna warning
default-directnotify-level info

# Resources settings
model-path /
model-cache-models #f
model-cache-textures #f
vfs-mount phase_3.mf /
vfs-mount phase_3.5.mf /
vfs-mount phase_4.mf /
vfs-mount phase_5.mf /
vfs-mount phase_5.5.mf /
vfs-mount phase_6.mf /
vfs-mount phase_7.mf /
vfs-mount phase_8.mf /
vfs-mount phase_9.mf /
vfs-mount phase_10.mf /
vfs-mount phase_11.mf /
vfs-mount phase_12.mf /
vfs-mount phase_13.mf /
vfs-mount phase_14.mf /
vfs-mount phase_14.5.mf /
default-model-extension .bam

# Needed for running a local server...
eventlog-host 127.0.0.1
default-access-level 307
accountdb-type local
accountdb-local-file astron/databases/accounts

# Game Features
want-estates #t
# They work fine.
want-clarabelle-voice #t
# Enables Clarabelle's voice from TTR.
want-pets #t
# They seem to work fine.
want-news-tab #f
want-news-page #f
# These work fine, but I dont know if they would be very useful
want-accessories #t
# Seems to work fine.
want-parties #t
# Needs a bit more work, but stable.
want-gardening #t
# Gardens work.
want-gifting #f
# Not needed.
want-cogdominiums #t
# These also work!
want-boarding-groups #t
# Works. Of course, offline won't need these.
want-cheesy-expirations #t
# Seems to work when you take into consideration that cheesy effects use seconds past the UNIX epoch, not just seconds
want-toontorial #t
# Leave this on true, as you can just skip on Make-A-Toon anyways. Works perfect.
want-code-redemption #t
# Works great!
want-new-toonhall #t
# Toon Hall w/ Silly Meter.
want-doomsday #f
# TTR's Toon Council Presidential Election Event
want-picnic-games #f
# Picnic table games. They work but the placement is broken for the tables.
want-prologue #t
# Toontown Offline Prologue Event
want-episodes #t
# Toontown Offline Episodes Menu
want-info-gui #t
# Toontown Offline Info Button
want-event-manager #f
# Event Manager, primarily for Operation: Duck Hunt Event
want-skip-button #t
# Skip button that TTR disabled by default.
auto-start-local-server #t
# Starts local server automatically when enabled.
want-toonfest-specials #f
# ToonFest Quiz Stand & Duck Tank

# Playgrounds
want-playgrounds #t
want-toontown-central #t
want-donalds-dock #t
want-daisy-gardens #t
want-minnies-melodyland #t
want-the-brrrgh #t
want-donalds-dreamland #t
want-goofy-speedway #t
want-acorn-acres #t
want-minigolf #t
want-toonfest #t
want-scrooge-bank #t
want-old-daisy-gardens #t

# Cog HQs
want-cog-headquarters #t
want-sellbot-hq #t
want-cashbot-hq #t
want-lawbot-hq #t
want-bossbot-hq #t
want-cnc #f

# Classic Characters
want-classic-chars #t
want-mickey #t
want-donald-dock #t
want-daisy #t
want-minnie #t
want-pluto #t
want-donald-dreamland #t
want-goofy #t
want-chip-and-dale #t
want-odg-goofy #t

# Misc. Modifications
estate-day-night #t
want-instant-parties #t
show-total-population #f
# Not interpolate-frames -- this is handled by the game code
interpolate-animations #t
# Toons fall asleep after 5 minutes instead of 2
sleep-timeout 300
# Always use the highest LOD.
always-max-lod #f
# Use 24 bit color depth, which fixes issues on Intel graphics chips
depth-bits 24
want-name-restrictions #f

# Chat Features
want-whitelist #f
want-blacklist #f
want-blacklist-sequence #f
force-avatar-understandable #t
force-player-understandable #t
parent-password-set #t
allow-secret-chat #t

# Localization
check-language #f
language english

# Holiday Manager
force-holiday-decorations 6
active-holidays 10, 15, 64, 65, 66
want-arg-manager #f
want-mega-invasions #f
mega-invasion-cog-type tm
