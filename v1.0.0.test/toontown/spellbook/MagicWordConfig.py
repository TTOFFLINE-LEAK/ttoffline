INCOMING_CHAT_MESSAGE_NAME = 'magicWord'
PREFIX_DEFAULT = '~'
PREFIX_ALLOWED = ['~', '?', '/', '<', ':', ';']
if not config.GetBool('exec-chat', 0):
    PREFIX_ALLOWED.append('>')
WIZARD_DEFAULT = 'Sorcerer Mickey'
MAGIC_WORD_SUCCESS_PHRASES = ['Alakazam!', 'Voila!', 'Ta-da!', 'Presto!', 'Abracadabra!']
MAGIC_WORD_RESPONSES = {'SuccessNoResp': 'response will be randomly selected from MAGIC_WORD_SUCCESS_PHRASES', 
   'Success': 'response will be provided by magic word', 
   'Teleporting': "Yikes! Don't use Magic words while switching zones!", 
   'OtherTeleporting': 'Your target is currently switching zones!', 
   'BadWord': "Uh-oh! This Magic Word doesn't exist!", 
   'NoEffect': "This word doesn't affect anybody!", 
   'BadTarget': 'Invalid target specified!', 
   'NoAccessToTarget': "You don't have a high enough access level to target them!", 
   'NoTarget': 'Unable to find a target!', 
   'NoAccess': 'Your Toon does not have enough power to use this Magic Word!', 
   'NotEnoughArgs': 'This command takes at least {}!', 
   'TooManyArgs': 'This command takes at most {}!', 
   'BadArgs': 'These arguments are of the wrong type!', 
   'CannotTarget': 'You cannot target other players with this Magic Word!', 
   'Locked': 'You are temporarily locked down and cannot use Magic Words.', 
   'RestrictionOther': 'You may only target one other player with this Magic Word!'}
HAS_EXTRA_MESSAGE_DATA = [
 'NotEnoughArgs', 'TooManyArgs']
AFFECT_TYPES = [
 'singular', 'zone', 'server', 'rank']
AFFECT_TYPES_NAMES = ['Everyone in this zone', 'The entire server', 'Everyone with an access level of']
AFFECT_NONE = -1
AFFECT_SINGLE = 0
AFFECT_OTHER = 1
AFFECT_BOTH = 2
AFFECT_SINGULAR = 0
AFFECT_ZONE = 1
AFFECT_SERVER = 2
AFFECT_RANK = 3
GROUP_AFFECTS = [AFFECT_ZONE, AFFECT_SERVER, AFFECT_RANK]
EXEC_LOC_INVALID = -1
EXEC_LOC_CLIENT = 0
EXEC_LOC_SERVER = 1
ARGUMENT_NAME = 0
ARGUMENT_TYPE = 1
ARGUMENT_REQUIRED = 2
ARGUMENT_DEFAULT = 3