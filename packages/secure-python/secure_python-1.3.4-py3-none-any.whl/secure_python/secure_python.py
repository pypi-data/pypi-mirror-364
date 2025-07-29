#v.1.3.4
#yes the code in this file is VERY bad for reading it's very bad code writing but this is on purpose

import json
import random
import sys
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import os

DEBUG = False
# ts needs to be before the main code is loaded for it to work!
# it will just give some more information
def debug(password):
    global DEBUG
    if password == "1234":
        print("Debug Mode activated")
        DEBUG = not DEBUG
        return DEBUG







#zeichen
alphabet = (
    [chr(i) for i in range(32, 217)]  # Maximum of 2970 possible (use at your own risk!)
# If desired, a minimum of 217 characters is also possible... though it really doesn't make a difference

    + ['\n', '\t', 'ü', 'ä', 'ö', 'ß']
)

# charset
encryption_chars = list("𒀀𒀁𒀂𒀃𒀄𒀅𒀆𒀇𒀈𒀉𒀊𒀋𒀌𒀍𒀎𒀏𒀐𒀑𒀒𒀓𒀔𒀕𒀖𒀗𒀘𒀙𒀚𒀛𒀜𒀝𒀞𒀟𒀠𒀡𒀢𒀣𒀤𒀥𒀦𒀧𒀨𒀩𒀪𒀫𒀬𒀭𒀮𒀯𒀰𒀱𒀲𒀳𒀴𒀵𒀶𒀷𒀸𒀹𒀺𒀻𒀼𒀽𒀾𒀿𒁀𒁁𒁂𒁃𒁄𒁅𒁆𒁇𒁈𒁉𒁊𒁋𒁌𒁍𒁎𒁏𒁐𒁑𒁒𒁓𒁔𒁕𒁖𒁗𒁘𒁙𒁚𒁛𒁜𒁝𒁞𒁟𒁠𒁡𒁢𒁣𒁤𒁥𒁦𒁧𒁨𒁩𒁪𒁫𒁬𒁭𒁮𒁯𒁰𒁱𒁲𒁳𒁴𒁵𒁶𒁷𒁸𒁹𒁺𒁻𒁼𒁽𒁾𒁿𒂀𒂁𒂂𒂃𒂄𒂅𒂆𒂇𒂈𒂉𒂊𒂋𒂌𒂍𒂎𒂏𒂐𒂑𒂒𒂓𒂔𒂕𒂖𒂗𒂘𒂙𒂚𒂛𒂜𒂝𒂞𒂟𒂠𒂡𒂢𒂣𒂤𒂥𒂦𒂧𒂨𒂩𒂪𒂫𒂬𒂭𒂮𒂯𒂰𒂱𒂲𒂳𒂴𒂵𒂶𒂷𒂸𒂹𒂺𒂻𒂼𒂽𒂾𒂿𒃀𒃁𒃂𒃃𒃄𒃅𒃆𒃇𒃈𒃉𒃊𒃋𒃌𒃍𒃎𒃏𒃐𒃑𒃒𒃓𒃔𒃕𒃖𒃗𒃘𒃙𒃚𒃛𒃜𒃝𒃞𒃟𒃠𒃡𒃢𒃣𒃤𒃥𒃦𒃧𒃨𒃩𒃪𒃫𒃬𒃭𒃮𒃯𒃰𒃱𒃲𒃳𒃴𒃵𒃶𒃷𒃸𒃹𒃺𒃻𒃼𒃽𒃾𒃿𒄀𒄁𒄂𒄃𒄄𒄅𒄆𒄇𒄈𒄉𒄊𒄋𒄌𒄍𒄎𒄏𒄐𒄑𒄒𒄓𒄔𒄕𒄖𒄗𒄘𒄙𒄚𒄛𒄜𒄝𒄞𒄟𒄠𒄡𒄢𒄣𒄤𒄥𒄦𒄧𒄨𒄩𒄪𒄫𒄬𒄭𒄮𒄯𒄰𒄱𒄲𒄳𒄴𒄵𒄶𒄷𒄸𒄹𒄺𒄻𒄼𒄽𒄾𒄿𒅀𒅁𒅂𒅃𒅄𒅅𒅆𒅇𒅈𒅉𒅊𒅋𒅌𒅍𒅎𒅏𒅐𒅑𒅒𒅓𒅔𒅕𒅖𒅗𒅘𒅙𒅚𒅛𒅜𒅝𒅞𒅟𒅠𒅡𒅢𒅣𒅤𒅥𒅦𒅧𒅨𒅩𒅪𒅫𒅬𒅭𒅮𒅯𒅰𒅱𒅲𒅳𒅴𒅵𒅶𒅷𒅸𒅹𒅺𒅻𒅼𒅽𒅾𒅿𒆀𒆁𒆂𒆃𒆄𒆅𒆆𒆇𒆈𒆉𒆊𒆋𒆌𒆍𒆎𒆏𒆐𒆑𒆒𒆓𒆔𒆕𒆖𒆗𒆘𒆙𒆚𒆛𒆜𒆝𒆞𒆟𒆠𒆡𒆢𒆣𒆤𒆥𒆦𒆧𒆨𒆩𒆪𒆫𒆬𒆭𒆮𒆯𒆰𒆱𒆲𒆳𒆴𒆵𒆶𒆷𒆸𒆹𒆺𒆻𒆼𒆽𒆾𒆿𒇀𒇁𒇂𒇃𒇄𒇅𒇆𒇇𒇈𒇉𒇊𒇋𒇌𒇍𒇎𒇏𒇐𒇑𒇒𒇓𒇔𒇕𒇖𒇗𒇘𒇙𒇚𒇛𒇜𒇝𒇞𒇟𒇠𒇡𒇢𒇣𒇤𒇥𒇦𒇧𒇨𒇩𒇪𒇫𒇬𒇭𒇮𒇯𒇰𒇱𒇲𒇳𒇴𒇵𒇶𒇷𒇸𒇹𒇺𒇻𒇼𒇽𒇾𒇿𒈀𒈁𒈂𒈃𒈄𒈅𒈆𒈇𒈈𒈉𒈊𒈋𒈌𒈍𒈎𒈏𒈐𒈑𒈒𒈓𒈔𒈕𒈖𒈗𒈘𒈙𒈚𒈛𒈜𒈝𒈞𒈟𒈠𒈡𒈢𒈣𒈤𒈥𒈦𒈧𒈨𒈩𒈪𒈫𒈬𒈭𒈮𒈯𒈰𒈱𒈲𒈳𒈴𒈵𒈶𒈷𒈸𒈹𒈺𒈻𒈼𒈽𒈾𒈿𒉀𒉁𒉂𒉃𒉄𒉅𒉆𒉇𒉈𒉉𒉊𒉋𒉌𒉍𒉎𒉏𒉐𒉑𒉒𒉓𒉔𒉕𒉖𒉗𒉘𒉙𒉚𒉛𒉜𒉝𒉞𒉟𒉠𒉡𒉢𒉣𒉤𒉥𒉦𒉧𒉨𒉩𒉪𒉫𒉬𒉭𒉮𒉯𒉰𒉱𒉲𒉳𒉴𒉵𒉶𒉷𒉸𒉹𒉺𒉻𒉼𒉽𒉾𒉿𒊀𒊁𒊂𒊃𒊄𒊅𒊆𒊇𒊈𒊉𒊊𒊋𒊌𒊍𒊎𒊏𒊐𒊑𒊒𒊓𒊔𒊕𒊖𒊗𒊘𒊙𒊚𒊛𒊜𒊝𒊞𒊟𒊠𒊡𒊢𒊣𒊤𒊥𒊦𒊧𒊨𒊩𒊪𒊫𒊬𒊭𒊮𒊯𒊰𒊱𒊲𒊳𒊴𒊵𒊶𒊷𒊸𒊹𒊺𒊻𒊼𒊽𒊾𒊿𒋀𒋁𒋂𒋃𒋄𒋅𒋆𒋇𒋈𒋉𒋊𒋋𒋌𒋍𒋎𒋏𒋐𒋑𒋒𒋓𒋔𒋕𒋖𒋗𒋘𒋙𒋚𒋛𒋜𒋝𒋞𒋟𒋠𒋡𒋢𒋣𒋤𒋥𒋦𒋧𒋨𒋩𒋪𒋫𒋬𒋭𒋮𒋯𒋰𒋱𒋲𒋳𒋴𒋵𒋶𒋷𒋸𒋹𒋺𒋻𒋼𒋽𒋾𒋿𒌀𒌁𒌂𒌃𒌄𒌅𒌆𒌇𒌈𒌉𒌊𒌋𒌌𒌍𒌎𒌏𒌐𒌑𒌒𒌓𒌔𒌕𒌖𒌗𒌘𒌙𒌚𒌛𒌜𒌝𒌞𒌟𒌠𒌡𒌢𒌣𒌤𒌥𒌦𒌧𒌨𒌩𒌪𒌫𒌬𒌭𒌮𒌯𒌰𒌱𒌲𒌳𒌴𒌵𒌶𒌷𒌸𒌹𒌺𒌻𒌼𒌽𒌾𒌿𒍀𒍁𒍂𒍃𒍄𒍅𒍆𒍇𒍈𒍉𒍊𒍋𒍌𒍍𒍎𒍏𒍐𒍑𒍒𒍓𒍔𒍕𒍖𒍗𒍘𒍙𒍚𒍛𒍜𒍝𒍞𒍟𒍠𒍡𒍢𒍣𒍤𒍥𒍦𒍧𒍨𒍩𒍪𒍫𒍬𒍭𒍮𒍯𒍰𒍱𒍲𒍳𒍴𒍵𒍶𒍷𒍸𒍹𒍺𒍻𒍼𒍽𒍾𒍿𒎀𒎁𒎂𒎃𒎄𒎅𒎆𒎇𒎈𒎉𒎊𒎋𒎌𒎍𒎎𒎏𒎐𒎑𒎒𒎓𒎔𒎕𒎖𒎗𒎘𒎙𐂀𐂁𐂂𐂃𐂄𐂅𐂆𐂇𐂈𐂉𐂊𐂋𐂌𐂍𐂎𐂏𐂐𐂑𐂒𐂓𐂔𐂕𐂖𐂗𐂘𐂙𐂚𐂛𐂜𐂝𐂞𐂟𐂠𐂡𐂢𐂣𐂤𐂥𐂦𐂧𐂨𐂩𐂪𐂫𐂬𐂭𐂮𐂯𐂰𐂱𐂲𐂳𐂴𐂵𐂶𐂷𐂸𐂹𐂺𐂻𐂼𐂽𐂾𐂿𐃀𐃁𐃂𐃃𐃄𐃅𐃆𐃇𐃈𐃉𐃊𐃋𐃌𐃍𐃎𐃏𐃐𐃑𐃒𐃓𐃔𐃕𐃖𐃗𐃘𐃙𐃚𐃛𐃜𐃝𐃞𐃟𐃠𐃡𐃢𐃣𐃤𐃥𐃦𐃧𐃨𐃩𐃪𐃫𐃬𐃭𐃮𐃯𐃰𐃱𐃲𐃳𐃴𐃵𐃶𐃷𐃸𐃹𐃺𐤀𐤁𐤂𐤃𐤄𐤅𐤆𐤇𐤈𐤉𐤊𐤋𐤌𐤍𐤎𐤏𐤐𐤑𐤒𐤓𐤖𐤗𐤘𐤙𐤚𐤛𐤟𐠀𐠁𐠂𐠃𐠄𐠅𐠈𐠊𐠋𐠌𐠍𐠎𐠏𐠐𐠑𐠒𐠓𐠔𐠕𐠖𐠗𐠘𐠙𐠚𐠛𐠜𐠝𐠞𐠟𐠠𐠡𐠢𐠣𐠤𐠥𐠦𐠧𐠨𐠩𐠪𐠫𐠬𐠭𐠮𐠯𐠰𐠱𐠲𐠳𐠴𐠵𐠷𐠸𐠼𐠿𓀀𓀁𓀂𓀃𓀄𓀅𓀆𓀇𓀈𓀉𓀊𓀋𓀌𓀍𓀎𓀏𓀐𓀑𓀒𓀓𓀔𓀕𓀖𓀗𓀘𓀙𓀚𓀛𓀜𓀝𓀞𓀟𓀠𓀡𓀢𓀣𓀤𓀥𓀦𓀧𓀨𓀩𓀪𓀫𓀬𓀭𓀮𓀯𓀰𓀱𓀲𓀳𓀴𓀵𓀶𓀷𓀸𓀹𓀺𓀻𓀼𓀽𓀾𓀿𓁀𓁁𓁂𓁃𓁄𓁅𓁆𓁇𓁈𓁉𓁊𓁋𓁌𓁍𓁎𓁏𓁐𓁑𓁒𓁓𓁔𓁕𓁖𓁗𓁘𓁙𓁚𓁛𓁜𓁝𓁞𓁟𓁠𓁡𓁢𓁣𓁤𓁥𓁦𓁧𓁨𓁩𓁪𓁫𓁬𓁭𓁮𓁯𓁰𓁱𓁲𓁳𓁴𓁵𓁶𓁷𓁸𓁹𓁺𓁻𓁼𓁽𓁾𓁿𓂀𓂁𓂂𓂃𓂄𓂅𓂆𓂇𓂈𓂉𓂊𓂋𓂌𓂍𓂎𓂏𓂐𓂑𓂒𓂓𓂔𓂕𓂖𓂗𓂘𓂙𓂚𓂛𓂜𓂝𓂞𓂟𓂠𓂡𓂢𓂣𓂤𓂥𓂦𓂧𓂨𓂩𓂪𓂫𓂬𓂭𓂮𓂯𓂰𓂱𓂲𓂳𓂴𓂵𓂶𓂷𓂸𓂺𓂻𓂼𓂽𓂾𓂿𓃀𓃁𓃂𓃃𓃄𓃅𓃆𓃇𓃈𓃉𓃊𓃋𓃌𓃍𓃎𓃏𓃐𓃑𓃒𓃓𓃔𓃕𓃖𓃗𓃘𓃙𓃚𓃛𓃜𓃝𓃞𓃟𓃠𓃡𓃢𓃣𓃤𓃥𓃦𓃧𓃨𓃩𓃪𓃫𓃬𓃭𓃮𓃯𓃰𓃱𓃲𓃳𓃴𓃵𓃶𓃷𓃸𓃹𓃺𓃻𓃼𓃽𓃾𓃿𓄀𓄁𓄂𓄃𓄄𓄅𓄆𓄇𓄈𓄉𓄊𓄋𓄌𓄍𓄎𓄏𓄐𓄑𓄒𓄓𓄔𓄕𓄖𓄗𓄘𓄙𓄚𓄛𓄜𓄝𓄞𓄟𓄠𓄡𓄢𓄣𓄤𓄥𓄦𓄧𓄨𓄩𓄪𓄫𓄬𓄭𓄮𓄯𓄰𓄱𓄲𓄳𓄴𓄵𓄶𓄷𓄸𓄹𓄺𓄻𓄼𓄽𓄾𓄿𓅀𓅁𓅂𓅃𓅄𓅅𓅆𓅇𓅈𓅉𓅊𓅋𓅌𓅍𓅎𓅏𓅐𓅑𓅒𓅓𓅔𓅕𓅖𓅗𓅘𓅙𓅚𓅛𓅜𓅝𓅞𓅟𓅠𓅡𓅢𓅣𓅤𓅥𓅦𓅧𓅨𓅩𓅪𓅫𓅬𓅭𓅮𓅯𓅰𓅱𓅲𓅳𓅴𓅵𓅶𓅷𓅸𓅹𓅺𓅻𓅼𓅽𓅾𓅿𓆀𓆁𓆂𓆃𓆄𓆅𓆆𓆇𓆈𓆉𓆊𓆋𓆌𓆍𓆎𓆏𓆐𓆑𓆒𓆓𓆔𓆕𓆖𓆗𓆘𓆙𓆚𓆛𓆜𓆝𓆞𓆟𓆠𓆡𓆢𓆣𓆤𓆥𓆦𓆧𓆨𓆩𓆪𓆫𓆬𓆭𓆮𓆯𓆰𓆱𓆲𓆳𓆴𓆵𓆶𓆷𓆸𓆹𓆺𓆻𓆼𓆽𓆾𓆿𓇀𓇁𓇂𓇃𓇄𓇅𓇆𓇇𓇈𓇉𓇊𓇋𓇌𓇍𓇎𓇏𓇐𓇑𓇒𓇓𓇔𓇕𓇖𓇗𓇘𓇙𓇚𓇛𓇜𓇝𓇞𓇟𓇠𓇡𓇢𓇣𓇤𓇥𓇦𓇧𓇨𓇩𓇪𓇫𓇬𓇭𓇮𓇯𓇰𓇱𓇲𓇳𓇴𓇵𓇶𓇷𓇸𓇹𓇺𓇻𓇼𓇽𓇾𓇿𓈀𓈁𓈂𓈃𓈄𓈅𓈆𓈇𓈈𓈉𓈊𓈋𓈌𓈍𓈎𓈏𓈐𓈑𓈒𓈓𓈔𓈕𓈖𓈗𓈘𓈙𓈚𓈛𓈜𓈝𓈞𓈟𓈠𓈡𓈢𓈣𓈤𓈥𓈦𓈧𓈨𓈩𓈪𓈫𓈬𓈭𓈮𓈯𓈰𓈱𓈲𓈳𓈴𓈵𓈶U𓈷𓈸𓈹𓈺𓈻𓈼𓈽𓈾𓈿𓉀𓉁𓉂𓉃𓉄𓉅𓉆𓉇𓉈𓉉𓉊𓉋𓉌𓉍𓉎𓉏𓉐𓉑𓉒𓉓𓉔𓉕𓉖𓉗𓉘𓉙𓉚𓉛𓉜𓉝𓉞𓉟𓉠𓉡𓉢𓉣𓉤𓉥𓉦𓉧𓉨𓉩𓉪𓉫𓉬𓉭𓉮𓉯𓉰𓉱𓉲𓉳𓉴𓉵𓉶𓉷𓉸𓉹𓉺𓉻𓉼𓉽𓉾𓉿𓊀𓊁𓊂𓊃𓊄𓊅𓊆𓊇𓊈𓊉𓊊𓊋𓊌𓊍𓊎𓊏𓊐𓊑𓊒𓊓𓊔𓊕𓊖𓊗𓊘𓊙𓊚𓊛𓊜𓊝𓊞𓊟𓊠𓊡𓊢𓊣𓊤𓊥𓊦𓊧𓊨𓊩𓊪𓊫𓊬𓊭𓊮𓊯𓊰𓊱𓊲𓊳𓊴𓊵𓊶𓊷𓊸𓊹𓊺𓊻𓊼𓊽𓊾𓊿𓋀𓋁𓋂𓋃𓋄𓋅𓋆𓋇𓋈𓋉𓋊𓋋𓋌𓋍𓋎𓋏𓋐𓋑𓋒𓋓𓋔𓋕𓋖𓋗𓋘𓋙𓋚𓋛𓋜𓋝𓋞𓋟𓋠𓋡𓋢𓋣𓋤𓋥𓋦𓋧𓋨𓋩𓋪𓋫𓋬𓋭𓋮𓋯𓋰𓋱𓋲𓋳𓋴𓋵𓋶𓋷𓋸𓋹𓋺𓋻𓋼𓋽𓋾𓋿𓌀𓌁𓌂𓌃𓌄𓌅𓌆𓌇𓌈𓌉𓌊𓌋𓌌𓌍𓌎𓌏𓌐𓌑𓌒𓌓𓌔𓌕𓌖𓌗𓌘𓌙𓌚𓌛𓌜𓌝𓌞𓌟𓌠𓌡𓌢𓌣𓌤𓌥𓌦𓌧𓌨𓌩𓌪𓌫𓌬𓌭𓌮𓌯𓌰𓌱𓌲𓌳𓌴𓌵𓌶𓌷𓌸𓌹𓌺𓌻𓌼𓌽𓌾𓌿𓍀𓍁𓍂𓍃𓍄𓍅𓍆𓍇𓍈𓍉𓍊𓍋𓍌𓍍𓍎𓍏𓍐𓍑𓍒𓍓𓍔𓍕𓍖𓍗𓍘𓍙𓍚𓍛𓍜𓍝𓍞𓍟𓍠𓍡𓍢𓍣𓍤𓍥𓍦𓍧𓍨𓍩𓍪𓍫𓍬𓍭𓍮𓍯𓍰𓍱𓍲𓍳𓍴𓍵𓍶𓍷𓍸𓍹𓍺𓍻𓍼𓍽𓍾𓍿𓎀𓎁𓎂𓎃𓎄𓎅𓎆𓎇𓎈𓎉𓎊𓎋𓎌𓎍𓎎𓎏𓎐𓎑𓎒𓎓𓎔𓎕𓎖𓎗𓎘𓎙𓎚𓎛𓎜𓎝𓎞𓎟𓎠𓎡𓎢𓎣𓎤𓎥𓎦𓎧𓎨𓎩𓎪𓎫𓎬𓎭𓎮𓎯𓎰𓎱𓎲𓎳𓎴𓎵𓎶𓎷𓎸𓎹𓎺𓎻𓎼𓎽𓎾𓎿𓏀𓏁𓏂𓏃𓏄𓏅𓏆𓏇𓏈𓏉𓏊𓏋𓏌𓏍𓏎𓏏𓏐𓏑𓏒𓏓𓏔𓏕𓏖𓏗𓏘𓏙𓏚𓏛𓏜Y𓏝𓏞𓏟𓏠𓏡𓏢𓏣𓏤𓏥𓏦𓏧𓏨𓏩𓏪𓏫𓏬𓏭𓏮𓏯𓏰𓏱𓏲𓏳𓏴𓏵𓏶𓏷𓏸𓏹𓏺𓏻𓏽𓏾𓏿𓐀𓐁𓐂𓐃𓐄𓐅𓐆𓐇𓐈𓐉𓐊𓐋𓐌𓐍𓐎𓐏𓐐𓐑𓐒𓐓𓐔𓐕𓐖𓐗𓐘𓐙𓐚𓐛𓐜𓐝𓐞𓐟𓐠𓐡𓐢𓐣𓐤𓐥𓐦𓐧𓐨𓐩𓐪𓐫𓐬𓐭𓐮🜀🜁🜂🜃🜄🜅🜆🜇🜈🜉🜊🜋🜌🜍🜎🜏🜐🜑🜒🜓🜔🜕🜖🜗🜘🜙🜚🜛🜜🜝🜞🜟🜠🜡🜢🜣🜤🜥🜦🜧🜨🜩🜪🜫🜬🜭🜮🜯🜰🜱🜲🜳🜴🜵🜶🜷🜸🜹🜺🜻🜼🜽🜾🜿🝀🝁🝂🝃🝄🝅🝆🝇🝈🝉🝊🝋🝍🝎🝏🝐🝑🝒🝓🝔🝕🝖🝗🝘🝙🝚🝛🝜🝝🝞🝟🝠🝡🝢🝣🝤🝥🝦🝧🝩🝪🝫🝬🝭🝮🝯🝰🝱🝲🝳🙪🙫🙬🙭🙮🙯🙰🙱🙲🙳🙴🙵🙶🙷🙸🙹🙺🙻🙼🙽🙾🙿𖠀𖠁𖠂𖠃𖠄𖠅𖠆𖠇𖠈𖠉𖠊𖠋𖠌𖠍𖠎𖠏𖠐𖠑𖠒Q𖠓𖠔𖠕𖠖𖠗𖠘𖠙𖠚𖠛𖠜𖠝𖠞𖠟𖠠𖠡𖠢𖠣𖠤𖠥𖠦𖠧𖠨𖠩𖠪𖠫𖠬𖠭𖠮𖠯𖠰𖠱𖠲𖠳𖠴𖠵𖠶𖠷𖠸𖠹𖠺𖠻𖠼𖠽𖠾𖠿𖡀𖡁𖡂𖡃𖡄𖡅𖡆𖡇𖡈𖡉𖡊𖡋𖡌𖡍𖡎𖡏𖡐𖡑𖡒𖡓𖡔𖡕𖡖𖡗𖡘𖡙𖡚𖡛𖡜𖡝𖡞𖡟𖡠𖡡𖡢𖡣𖡤𖡥𖡦𖡧𖡨𖡩𖡪𖡫𖡬𖡭𖡮𖡯𖡰𖡱𖡲𖡳𖡴𖡵𖡶𖡷𖡸𖡹𖡺𖡻𖡼𖡽𖡾𖡿𖢀𖢁𖢂𖢃𖢄𖢅𖢆𖢇𖢈𖢉𖢊𖢋𖢌𖢍𖢎𖢏𖢐𖢑𖢒𖢓𖢔𖢕𖢖𖢗𖢘𖢙𖢚𖢛𖢜𖢝𖢞𖢟𖢠𖢡𖢢𖢣𖢤𖢥𖢦𖢧𖢨𖢩𖢪𖢫𖢬𖢭𖢮𖢯𖢰𖢱𖢲𖢳𖢴𖢵𖢶𖢷𖢸𖢹𖢺𖢻𖢼𖢽𖢾𖢿𖣀𖣁𖣂𖣃𖣄𖣅𖣆𖣇𖣈𖣉𖣊𖣋𖣌𖣍𖣎𖣏𖣐𖣑𖣒𖣓𖣔𖣕𖣖𖣗𖣘𖣙𖣚𖣛𖣜𖣝𖣞𖣟𖣠𖣡𖣢𖣣𖣤𖣥𖣦𖣧𖣨𖣩𖣪𖣫𖣬𖣭𖣮𖣯𖣰𖣱𖣲𖣳𖣴𖣵𖣶𖣷𖣸𖣹𖣺𖣻𖣼𖣽𖣾𖣿𖤀𖤁𖤂𖤃𖤄𖤅𖤆𖤇𖤈𖤉𖤊𖤋𖤌𖤍𖤎𖤏𖤐𖤑𖤒𖤓𖤔𖤕𖤖𖤗𖤘𖤙𖤚𖤛𖤜𖤝𖤞𖤟𖤠𖤡𖤢𖤣𖤤𖤥𖤦𖤧𖤨𖤩𖤪𖤫𖤬𖤭𖤮𖤯𖤰𖤱𖤲𖤳𖤴𖤵𖤶𖤷𖤸𖤹𖤺𖤻𖤼𖤽𖤾𖤿𖥀𖥁𖥂𖥃𖥄𖥅𖥆𖥇𖥈𖥉𖥊𖥋𖥌𖥍𖥎𖥏𖥐𖥑𖥒𖥓𖥔𖥕𖥖𖥗𖥘𖥙𖥚𖥛𖥜𖥝𖥞𖥟𖥠𖥡𖥢𖥣𖥤𖥥𖥦𖥧𖥨𖥩𖥪𖥫𖥬𖥭𖥮𖥯𖥰𖥱𖥲𖥳𖥴𖥵𖥶𖥷𖥸𖥹𖥺𖥻𖥼𖥽𖥾𖥿𖦀𖦁𖦂𖦃𖦄𖦅𖦆𖦇𖦈𖦉𖦊𖦋𖦌𖦍𖦎𖦏𖦐𖦑𖦒𖦓𖦔𖦕𖦖𖦗𖦘𖦙𖦚𖦛𖦜𖦝𖦞𖦟𖦠𖦡𖦢𖦣𖦤𖦥𖦦𖦧𖦨𖦩𖦪𖦫𖦬𖦭𖦮𖦯𖦰𖦱𖦲𖦳𖦴𖦵𖦶𖦷𖦸𖦹𖦺𖦻𖦼𖦽𖦾𖦿𖧀𖧁𖧂𖧃𖧄𖧅𖧆𖧇𖧈𖧉𖧊𖧋𖧌𖧍𖧎𖧏𖧐𖧑𖧒𖧓𖧔𖧕𖧖𖧗𖧘𖧙𖧚𖧛𖧜𖧝𖧞𖧟𖧠𖧡𖧢𖧣𖧤𖧥𖧦𖧧𖧨𖧩𖧪𖧫𖧬𖧭𖧮𖧯𖧰𖧱𖧲𖧳𖧴𖧵𖧶𖧷𖧸𖧹𖧺𖧻𖧼𖧽𖧾𖧿𖨀𖨁𖨂𖨃𖨄𖨅𖨆𖨇𖨈𖨉𖨊𖨋𖨌𖨍𖨎𖨏𖨐𖨑𖨒𖨓𖨔𖨕𖨖𖨗𖨘𖨙𖨚𖨛𖨜𖨝𖨞𖨟𖨠𖨡𖨢𖨣𖨤𖨥𖨦𖨧𖨨𖨩𖨪𖨫𖨬𖨭𖨮𖨯𖨰𖨱𖨲𖨳𖨴𖨵𖨶𖨷𖨸🂠🂡🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂬🂭🂮🂱🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂼🂽🂾🂿🃁🃂🃃🃄🃅🃆🃇🃈🃉🃊🃋🃌🃍🃎🃑🃒🃓🃔🃕🃖🃗🃘🃙🃚🃛🃜🃝🃞🃟🃠🃡🃢🃣🃤🃥🃦🃧🃨🃩🃫🃪🃬🃭🃮🃯🃰🃱🃲🃳🃴🃵")




#test commands
def list_length(): 
    print(f"The list contains {len(encryption_chars)} characters.")

def does_it_work():
    print("it works!")


def secure_path():
    base = None
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        base = sys.prefix
    elif 'VIRTUAL_ENV' in os.environ:
        base = os.environ['VIRTUAL_ENV']
    else:
        base = os.getcwd() 

    pfad = os.path.join(base, "Lib", "site-packages", "secure_python", "secure")
    CHECK_FILE_EXISTENSE(pfad)
    
    if DEBUG == True:
        print(pfad)
        
    return pfad + os.sep
    #example: C:\Users\USER\Projects\secure_python\.venv\Lib\site-packages\secure_python\secure


# alphabet to charset
def alphabet_2_charset(secure: str):
    result = []
    for charackters in secure:
        if charackters in alphabet:
            index = alphabet.index(charackters)
            if index < len(encryption_chars):
                result.append(encryption_chars[index])
            else:
                result.append('?') # corrupt mapping
        else:
            result.append('[UNKOWN]') # unkown symbol
    return ''.join(result)



# charset to alphabet
def charset_2_alphabet(secure: str):
    result = []
    for charackters in secure:
        if charackters in encryption_chars:
            index = encryption_chars.index(charackters)
            if index < len(alphabet):
                result.append(alphabet[index])
            else:
                result.append('?') # corrupt mapping
        else:
            result.append('[UNKOWN]') # unkown symbol
    return ''.join(result)


# Create random mapping
def CREATE_RANDOM_MAPPING():  

    shuffled_chars = encryption_chars[:]
    random.shuffle(shuffled_chars)

    mapping = {}
    for i in range(len(alphabet)):
        original_char = alphabet[i]
        mapped_char = shuffled_chars[i]
        mapping[original_char] = mapped_char

    return mapping


#check file existense
def CHECK_FILE_EXISTENSE(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Die Datei {filepath} wurde nicht gefunden.")


# Save mapping
def SAVE_MAPPING(mapping, file):  
    obfuscated_mapping = {alphabet_2_charset(enc_char): value for enc_char, value in mapping.items()}

    file_path = secure_path() + file.removesuffix(".py") + ".json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(obfuscated_mapping, f, ensure_ascii=False)

    print("Mapping saved successfully")




# Load mapping
def LOAD_MAPPING(file):  
    file_path = secure_path() + file.removesuffix(".py") + ".json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "r", encoding="utf-8") as f:
        obfuscated_mapping = json.load(f)

    mapping = {charset_2_alphabet(enc_char): value for enc_char, value in obfuscated_mapping.items()}

    return mapping



# Encode text
def ENCODE_TEXT(text, mapping):  
    return ''.join(mapping.get(charackters, '[UNKNOWN]') for charackters in text)

# Decode text
def DECODE_TEXT(text, mapping):  
    reverse = {v: encryption_chars for encryption_chars, v in mapping.items()}
    return ''.join(reverse.get(charackters, '[UNKNOWN]') for charackters in text)

#encode file
def ENCODE_FILE(file, mapping): 
    with open(file, "r", encoding="utf-8") as f:
        code = f.read()
    encoded = ENCODE_TEXT(code, mapping)
    out_file = secure_path() + "data\\" + file.removesuffix(".py") + ".lpyip"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(encoded)
    print(f"Datei erfolgreich verschlüsselt")

#open encoded file
def OPEN_ENCODED_FILE(file): 
    file = secure_path() + "data\\" + file.removesuffix(".py") + ".lpyip"
    with open(file, "r", encoding="utf-8") as f:
        encoded_code = f.read()
    return encoded_code



p = "passwort" 


def ENCODE_MAIN_SAFE(filename: str):

    MAPPING_JSON_PATH = secure_path() + filename.removesuffix(".py") + ".json"
    MAPPING_ENC_PATH = MAPPING_JSON_PATH.removesuffix(".json") + ".enc"

    mapping = CREATE_RANDOM_MAPPING()              
    SAVE_MAPPING(mapping, filename)

    with open(MAPPING_JSON_PATH, "rb") as file:
        json_data = file.read()

    salt = get_random_bytes(16)
    key = PBKDF2(p, salt, dkLen=32, count=100_000)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(json_data)

    with open(MAPPING_ENC_PATH, "wb") as out_file:
        out_file.write(salt + cipher.nonce + tag + ciphertext)

    os.remove(MAPPING_JSON_PATH)

    ENCODE_FILE(filename, mapping)




def ENCODE_MAIN_DELETE(filename: str):

    MAPPING_JSON_PATH = secure_path() + filename.removesuffix(".py") + ".json"
    MAPPING_ENC_PATH = MAPPING_JSON_PATH.removesuffix(".json") + ".enc"

    mapping = CREATE_RANDOM_MAPPING()   
    SAVE_MAPPING(mapping, filename)

    with open(MAPPING_JSON_PATH, "rb") as file:
        json_data = file.read()

    salt = get_random_bytes(16)
    key = PBKDF2(p, salt, dkLen=32, count=100_000)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(json_data)

    with open(MAPPING_ENC_PATH, "wb") as out_file:
        out_file.write(salt + cipher.nonce + tag + ciphertext)

    os.remove(MAPPING_JSON_PATH)         
    ENCODE_FILE(filename, mapping)       
    os.remove(filename)         



def dme(filename: str, namespace=globals()):

    try:
        MAPPING_ENC_PATH = secure_path() + filename.removesuffix(".py") + ".enc"
        code_path = secure_path() + "data/" + filename.removesuffix(".py") + ".lpyip"

        with open(MAPPING_ENC_PATH, "rb") as enc_file:
            data = enc_file.read()

        salt = data[:16]
        nonce = data[16:32]
        tag = data[32:48]
        ciphertext = data[48:]

        key = PBKDF2(p, salt, dkLen=32, count=100_000)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        raw_mapping = json.loads(plaintext.decode("utf-8"))
        mapping = {charset_2_alphabet(encryption_chars): v for encryption_chars, v in raw_mapping.items()}
        reverse_mapping = {v: k for k, v in mapping.items()}

        with open(code_path, "r", encoding="utf-8") as code_file:
            encoded_code = code_file.read()
        decoded_code = ''.join(reverse_mapping.get(charackters, '?') for charackters in encoded_code)

        exec(decoded_code, namespace)

    except Exception as e:
        print(f"Error while decrypting or executing '{filename}': {e}")




def dms(filename: str, file_path="" , marked=False ,cleanup=False, namespace=globals(),):

    MAPPING_ENC_PATH = secure_path() + filename.removesuffix(".py") + ".enc"
    with open(MAPPING_ENC_PATH, "rb") as file:
        data = file.read()

    salt = data[:16]
    nonce = data[16:32]
    tag = data[32:48]
    ciphertext = data[48:]

    key = PBKDF2(p, salt, dkLen=32, count=100_000)

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

    raw_mapping = json.loads(plaintext.decode("utf-8"))

    mapping = {charset_2_alphabet(encryption_chars): v for encryption_chars, v in raw_mapping.items()}
    reverse_mapping = {v: k for k, v in mapping.items()}
    if DEBUG == True:
        print(f"mapping is \n {mapping}")
        print(f"reverse mapping is \n {reverse_mapping}")

    code_path = secure_path() + "data/" + filename.removesuffix(".py") + ".lpyip"
    with open(code_path, "r", encoding="utf-8") as file:
        coded_text = file.read()
        if DEBUG == True:
            print(f"the coded_text is: \n {coded_text}")

    decoded_code = ''.join(reverse_mapping.get(charackters, '?') for charackters in coded_text)
    if DEBUG == True:
        print(f"the decoded_code is: \n {decoded_code}")

    try:
        CHECK_FILE_EXISTENSE(file_path)
    except FileNotFoundError:
        print("path was not found")
        print("path will be created\n\n")
        try:
            os.makedirs(file_path)
        except FileNotFoundError as e:
            if DEBUG == True:
                print(e)

    if marked == True:
        output_file = file_path + filename.removesuffix(".py") + "__encoded__.py"
        if DEBUG == True:
            print(f" the the path of the file is: {output_file}")

    elif marked == False:
        output_file = file_path + filename
        if DEBUG == True:
            print(f" the the path of the file is: {output_file}")

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(decoded_code)

    if cleanup == True:
        out_file = secure_path() + "\\data\\" + filename.removesuffix(".py") + ".lpyip"
        if DEBUG == True:
            print(MAPPING_ENC_PATH)
            print(out_file)

        os.remove(MAPPING_ENC_PATH)
        os.remove(out_file)
        print("cleanup complete")

