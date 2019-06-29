import struct
from otp.ai.passlib.utils import repeat_string
__all__ = [
 'BlowfishEngine']
BLOWFISH_P = BLOWFISH_S = None

def _init_constants():
    global BLOWFISH_P
    global BLOWFISH_S
    BLOWFISH_P = [
     608135816, 2242054355L, 320440878, 57701188,
     2752067618L, 698298832, 137296536, 3964562569L,
     1160258022, 953160567, 3193202383L, 887688300,
     3232508343L, 3380367581L, 1065670069, 3041331479L,
     2450970073L, 2306472731L]
    BLOWFISH_S = [
     [
      3509652390L, 2564797868L, 805139163, 3491422135L,
      3101798381L, 1780907670, 3128725573L, 4046225305L,
      614570311, 3012652279L, 134345442, 2240740374L,
      1667834072, 1901547113, 2757295779L, 4103290238L,
      227898511, 1921955416, 1904987480, 2182433518L,
      2069144605, 3260701109L, 2620446009L, 720527379,
      3318853667L, 677414384, 3393288472L, 3101374703L,
      2390351024L, 1614419982, 1822297739, 2954791486L,
      3608508353L, 3174124327L, 2024746970, 1432378464,
      3864339955L, 2857741204L, 1464375394, 1676153920,
      1439316330, 715854006, 3033291828L, 289532110,
      2706671279L, 2087905683, 3018724369L, 1668267050,
      732546397, 1947742710, 3462151702L, 2609353502L,
      2950085171L, 1814351708, 2050118529, 680887927,
      999245976, 1800124847, 3300911131L, 1713906067,
      1641548236, 4213287313L, 1216130144, 1575780402,
      4018429277L, 3917837745L, 3693486850L, 3949271944L,
      596196993, 3549867205L, 258830323, 2213823033L,
      772490370, 2760122372L, 1774776394, 2652871518L,
      566650946, 4142492826L, 1728879713, 2882767088L,
      1783734482, 3629395816L, 2517608232L, 2874225571L,
      1861159788, 326777828, 3124490320L, 2130389656,
      2716951837L, 967770486, 1724537150, 2185432712L,
      2364442137L, 1164943284, 2105845187, 998989502,
      3765401048L, 2244026483L, 1075463327, 1455516326,
      1322494562, 910128902, 469688178, 1117454909,
      936433444, 3490320968L, 3675253459L, 1240580251,
      122909385, 2157517691L, 634681816, 4142456567L,
      3825094682L, 3061402683L, 2540495037L, 79693498,
      3249098678L, 1084186820, 1583128258, 426386531,
      1761308591, 1047286709, 322548459, 995290223,
      1845252383, 2603652396L, 3431023940L, 2942221577L,
      3202600964L, 3727903485L, 1712269319, 422464435,
      3234572375L, 1170764815, 3523960633L, 3117677531L,
      1434042557, 442511882, 3600875718L, 1076654713,
      1738483198, 4213154764L, 2393238008L, 3677496056L,
      1014306527, 4251020053L, 793779912, 2902807211L,
      842905082, 4246964064L, 1395751752, 1040244610,
      2656851899L, 3396308128L, 445077038, 3742853595L,
      3577915638L, 679411651, 2892444358L, 2354009459L,
      1767581616, 3150600392L, 3791627101L, 3102740896L,
      284835224, 4246832056L, 1258075500, 768725851,
      2589189241L, 3069724005L, 3532540348L, 1274779536,
      3789419226L, 2764799539L, 1660621633, 3471099624L,
      4011903706L, 913787905, 3497959166L, 737222580,
      2514213453L, 2928710040L, 3937242737L, 1804850592,
      3499020752L, 2949064160L, 2386320175L, 2390070455L,
      2415321851L, 4061277028L, 2290661394L, 2416832540L,
      1336762016, 1754252060, 3520065937L, 3014181293L,
      791618072, 3188594551L, 3933548030L, 2332172193L,
      3852520463L, 3043980520L, 413987798, 3465142937L,
      3030929376L, 4245938359L, 2093235073, 3534596313L,
      375366246, 2157278981L, 2479649556L, 555357303,
      3870105701L, 2008414854, 3344188149L, 4221384143L,
      3956125452L, 2067696032, 3594591187L, 2921233993L,
      2428461, 544322398, 577241275, 1471733935,
      610547355, 4027169054L, 1432588573, 1507829418,
      2025931657, 3646575487L, 545086370, 48609733,
      2200306550L, 1653985193, 298326376, 1316178497,
      3007786442L, 2064951626, 458293330, 2589141269L,
      3591329599L, 3164325604L, 727753846, 2179363840L,
      146436021, 1461446943, 4069977195L, 705550613,
      3059967265L, 3887724982L, 4281599278L, 3313849956L,
      1404054877, 2845806497L, 146425753, 1854211946],
     [
      1266315497, 3048417604L, 3681880366L, 3289982499L,
      2909710000L, 1235738493, 2632868024L, 2414719590L,
      3970600049L, 1771706367, 1449415276, 3266420449L,
      422970021, 1963543593, 2690192192L, 3826793022L,
      1062508698, 1531092325, 1804592342, 2583117782L,
      2714934279L, 4024971509L, 1294809318, 4028980673L,
      1289560198, 2221992742L, 1669523910, 35572830,
      157838143, 1052438473, 1016535060, 1802137761,
      1753167236, 1386275462, 3080475397L, 2857371447L,
      1040679964, 2145300060, 2390574316L, 1461121720,
      2956646967L, 4031777805L, 4028374788L, 33600511,
      2920084762L, 1018524850, 629373528, 3691585981L,
      3515945977L, 2091462646, 2486323059L, 586499841,
      988145025, 935516892, 3367335476L, 2599673255L,
      2839830854L, 265290510, 3972581182L, 2759138881L,
      3795373465L, 1005194799, 847297441, 406762289,
      1314163512, 1332590856, 1866599683, 4127851711L,
      750260880, 613907577, 1450815602, 3165620655L,
      3734664991L, 3650291728L, 3012275730L, 3704569646L,
      1427272223, 778793252, 1343938022, 2676280711L,
      2052605720, 1946737175, 3164576444L, 3914038668L,
      3967478842L, 3682934266L, 1661551462, 3294938066L,
      4011595847L, 840292616, 3712170807L, 616741398,
      312560963, 711312465, 1351876610, 322626781,
      1910503582, 271666773, 2175563734L, 1594956187,
      70604529, 3617834859L, 1007753275, 1495573769,
      4069517037L, 2549218298L, 2663038764L, 504708206,
      2263041392L, 3941167025L, 2249088522L, 1514023603,
      1998579484, 1312622330, 694541497, 2582060303L,
      2151582166L, 1382467621, 776784248, 2618340202L,
      3323268794L, 2497899128L, 2784771155L, 503983604,
      4076293799L, 907881277, 423175695, 432175456,
      1378068232, 4145222326L, 3954048622L, 3938656102L,
      3820766613L, 2793130115L, 2977904593L, 26017576,
      3274890735L, 3194772133L, 1700274565, 1756076034,
      4006520079L, 3677328699L, 720338349, 1533947780,
      354530856, 688349552, 3973924725L, 1637815568,
      332179504, 3949051286L, 53804574, 2852348879L,
      3044236432L, 1282449977, 3583942155L, 3416972820L,
      4006381244L, 1617046695, 2628476075L, 3002303598L,
      1686838959, 431878346, 2686675385L, 1700445008,
      1080580658, 1009431731, 832498133, 3223435511L,
      2605976345L, 2271191193L, 2516031870L, 1648197032,
      4164389018L, 2548247927L, 300782431, 375919233,
      238389289, 3353747414L, 2531188641L, 2019080857,
      1475708069, 455242339, 2609103871L, 448939670,
      3451063019L, 1395535956, 2413381860L, 1841049896,
      1491858159, 885456874, 4264095073L, 4001119347L,
      1565136089, 3898914787L, 1108368660, 540939232,
      1173283510, 2745871338L, 3681308437L, 4207628240L,
      3343053890L, 4016749493L, 1699691293, 1103962373,
      3625875870L, 2256883143L, 3830138730L, 1031889488,
      3479347698L, 1535977030, 4236805024L, 3251091107L,
      2132092099, 1774941330, 1199868427, 1452454533,
      157007616, 2904115357L, 342012276, 595725824,
      1480756522, 206960106, 497939518, 591360097,
      863170706, 2375253569L, 3596610801L, 1814182875,
      2094937945, 3421402208L, 1082520231, 3463918190L,
      2785509508L, 435703966, 3908032597L, 1641649973,
      2842273706L, 3305899714L, 1510255612, 2148256476L,
      2655287854L, 3276092548L, 4258621189L, 236887753,
      3681803219L, 274041037, 1734335097, 3815195456L,
      3317970021L, 1899903192, 1026095262, 4050517792L,
      356393447, 2410691914L, 3873677099L, 3682840055L],
     [
      3913112168L, 2491498743L, 4132185628L, 2489919796L,
      1091903735, 1979897079, 3170134830L, 3567386728L,
      3557303409L, 857797738, 1136121015, 1342202287,
      507115054, 2535736646L, 337727348, 3213592640L,
      1301675037, 2528481711L, 1895095763, 1721773893,
      3216771564L, 62756741, 2142006736, 835421444,
      2531993523L, 1442658625, 3659876326L, 2882144922L,
      676362277, 1392781812, 170690266, 3921047035L,
      1759253602, 3611846912L, 1745797284, 664899054,
      1329594018, 3901205900L, 3045908486L, 2062866102,
      2865634940L, 3543621612L, 3464012697L, 1080764994,
      553557557, 3656615353L, 3996768171L, 991055499,
      499776247, 1265440854, 648242737, 3940784050L,
      980351604, 3713745714L, 1749149687, 3396870395L,
      4211799374L, 3640570775L, 1161844396, 3125318951L,
      1431517754, 545492359, 4268468663L, 3499529547L,
      1437099964, 2702547544L, 3433638243L, 2581715763L,
      2787789398L, 1060185593, 1593081372, 2418618748L,
      4260947970L, 69676912, 2159744348L, 86519011,
      2512459080L, 3838209314L, 1220612927, 3339683548L,
      133810670, 1090789135, 1078426020, 1569222167,
      845107691, 3583754449L, 4072456591L, 1091646820,
      628848692, 1613405280, 3757631651L, 526609435,
      236106946, 48312990, 2942717905L, 3402727701L,
      1797494240, 859738849, 992217954, 4005476642L,
      2243076622L, 3870952857L, 3732016268L, 765654824,
      3490871365L, 2511836413L, 1685915746, 3888969200L,
      1414112111, 2273134842L, 3281911079L, 4080962846L,
      172450625, 2569994100L, 980381355, 4109958455L,
      2819808352L, 2716589560L, 2568741196L, 3681446669L,
      3329971472L, 1835478071, 660984891, 3704678404L,
      4045999559L, 3422617507L, 3040415634L, 1762651403,
      1719377915, 3470491036L, 2693910283L, 3642056355L,
      3138596744L, 1364962596, 2073328063, 1983633131,
      926494387, 3423689081L, 2150032023L, 4096667949L,
      1749200295, 3328846651L, 309677260, 2016342300,
      1779581495, 3079819751L, 111262694, 1274766160,
      443224088, 298511866, 1025883608, 3806446537L,
      1145181785, 168956806, 3641502830L, 3584813610L,
      1689216846, 3666258015L, 3200248200L, 1692713982,
      2646376535L, 4042768518L, 1618508792, 1610833997,
      3523052358L, 4130873264L, 2001055236, 3610705100L,
      2202168115L, 4028541809L, 2961195399L, 1006657119,
      2006996926, 3186142756L, 1430667929, 3210227297L,
      1314452623, 4074634658L, 4101304120L, 2273951170L,
      1399257539, 3367210612L, 3027628629L, 1190975929,
      2062231137, 2333990788L, 2221543033L, 2438960610L,
      1181637006, 548689776, 2362791313L, 3372408396L,
      3104550113L, 3145860560L, 296247880, 1970579870,
      3078560182L, 3769228297L, 1714227617, 3291629107L,
      3898220290L, 166772364, 1251581989, 493813264,
      448347421, 195405023, 2709975567L, 677966185,
      3703036547L, 1463355134, 2715995803L, 1338867538,
      1343315457, 2802222074L, 2684532164L, 233230375,
      2599980071L, 2000651841, 3277868038L, 1638401717,
      4028070440L, 3237316320L, 6314154, 819756386,
      300326615, 590932579, 1405279636, 3267499572L,
      3150704214L, 2428286686L, 3959192993L, 3461946742L,
      1862657033, 1266418056, 963775037, 2089974820,
      2263052895L, 1917689273, 448879540, 3550394620L,
      3981727096L, 150775221, 3627908307L, 1303187396,
      508620638, 2975983352L, 2726630617L, 1817252668,
      1876281319, 1457606340, 908771278, 3720792119L,
      3617206836L, 2455994898L, 1729034894, 1080033504],
     [
      976866871, 3556439503L, 2881648439L, 1522871579,
      1555064734, 1336096578, 3548522304L, 2579274686L,
      3574697629L, 3205460757L, 3593280638L, 3338716283L,
      3079412587L, 564236357, 2993598910L, 1781952180,
      1464380207, 3163844217L, 3332601554L, 1699332808,
      1393555694, 1183702653, 3581086237L, 1288719814,
      691649499, 2847557200L, 2895455976L, 3193889540L,
      2717570544L, 1781354906, 1676643554, 2592534050L,
      3230253752L, 1126444790, 2770207658L, 2633158820L,
      2210423226L, 2615765581L, 2414155088L, 3127139286L,
      673620729, 2805611233L, 1269405062, 4015350505L,
      3341807571L, 4149409754L, 1057255273, 2012875353,
      2162469141L, 2276492801L, 2601117357L, 993977747,
      3918593370L, 2654263191L, 753973209, 36408145,
      2530585658L, 25011837, 3520020182L, 2088578344,
      530523599, 2918365339L, 1524020338, 1518925132,
      3760827505L, 3759777254L, 1202760957, 3985898139L,
      3906192525L, 674977740, 4174734889L, 2031300136,
      2019492241, 3983892565L, 4153806404L, 3822280332L,
      352677332, 2297720250L, 60907813, 90501309,
      3286998549L, 1016092578, 2535922412L, 2839152426L,
      457141659, 509813237, 4120667899L, 652014361,
      1966332200, 2975202805L, 55981186, 2327461051L,
      676427537, 3255491064L, 2882294119L, 3433927263L,
      1307055953, 942726286, 933058658, 2468411793L,
      3933900994L, 4215176142L, 1361170020, 2001714738,
      2830558078L, 3274259782L, 1222529897, 1679025792,
      2729314320L, 3714953764L, 1770335741, 151462246,
      3013232138L, 1682292957, 1483529935, 471910574,
      1539241949, 458788160, 3436315007L, 1807016891,
      3718408830L, 978976581, 1043663428, 3165965781L,
      1927990952, 4200891579L, 2372276910L, 3208408903L,
      3533431907L, 1412390302, 2931980059L, 4132332400L,
      1947078029, 3881505623L, 4168226417L, 2941484381L,
      1077988104, 1320477388, 886195818, 18198404,
      3786409000L, 2509781533L, 112762804, 3463356488L,
      1866414978, 891333506, 18488651, 661792760,
      1628790961, 3885187036L, 3141171499L, 876946877,
      2693282273L, 1372485963, 791857591, 2686433993L,
      3759982718L, 3167212022L, 3472953795L, 2716379847L,
      445679433, 3561995674L, 3504004811L, 3574258232L,
      54117162, 3331405415L, 2381918588L, 3769707343L,
      4154350007L, 1140177722, 4074052095L, 668550556,
      3214352940L, 367459370, 261225585, 2610173221L,
      4209349473L, 3468074219L, 3265815641L, 314222801,
      3066103646L, 3808782860L, 282218597, 3406013506L,
      3773591054L, 379116347, 1285071038, 846784868,
      2669647154L, 3771962079L, 3550491691L, 2305946142L,
      453669953, 1268987020, 3317592352L, 3279303384L,
      3744833421L, 2610507566L, 3859509063L, 266596637,
      3847019092L, 517658769, 3462560207L, 3443424879L,
      370717030, 4247526661L, 2224018117L, 4143653529L,
      4112773975L, 2788324899L, 2477274417L, 1456262402,
      2901442914L, 1517677493, 1846949527, 2295493580L,
      3734397586L, 2176403920L, 1280348187, 1908823572,
      3871786941L, 846861322, 1172426758, 3287448474L,
      3383383037L, 1655181056, 3139813346L, 901632758,
      1897031941, 2986607138L, 3066810236L, 3447102507L,
      1393639104, 373351379, 950779232, 625454576,
      3124240540L, 4148612726L, 2007998917, 544563296,
      2244738638L, 2330496472L, 2058025392, 1291430526,
      424198748, 50039436, 29584100, 3605783033L,
      2429876329L, 2791104160L, 1057563949, 3255363231L,
      3075367218L, 3463963227L, 1469046755, 985887462]]


class BlowfishEngine(object):

    def __init__(self):
        if BLOWFISH_P is None:
            _init_constants()
        self.P = list(BLOWFISH_P)
        self.S = [ list(box) for box in BLOWFISH_S ]
        return

    @staticmethod
    def key_to_words(data, size=18):
        dlen = len(data)
        if not dlen:
            return [
             0] * size
        data = repeat_string(data, size << 2)
        return struct.unpack('>%dI' % (size,), data)

    def encipher(self, l, r):
        P, S = self.P, self.S
        l ^= P[0]
        i = 1
        while i < 17:
            r = (S[0][(l >> 24)] + S[1][(l >> 16 & 255)] ^ S[2][(l >> 8 & 255)]) + S[3][(l & 255)] & 4294967295L ^ P[i] ^ r
            l, r = r, l
            i += 1

        return (r ^ P[17], l)

    def expand(self, key_words):
        P, S, encipher = self.P, self.S, self.encipher
        i = 0
        while i < 18:
            P[i] ^= key_words[i]
            i += 1

        i = l = r = 0
        while i < 18:
            P[i], P[i + 1] = l, r = encipher(l, r)
            i += 2

        for box in S:
            i = 0
            while i < 256:
                box[i], box[i + 1] = l, r = encipher(l, r)
                i += 2

    def eks_salted_expand(self, key_words, salt_words):
        salt_size = len(salt_words)
        P, S, encipher = self.P, self.S, self.encipher
        i = 0
        while i < 18:
            P[i] ^= key_words[i]
            i += 1

        s = i = l = r = 0
        while i < 18:
            l ^= salt_words[s]
            r ^= salt_words[(s + 1)]
            s += 2
            if s == salt_size:
                s = 0
            P[i], P[i + 1] = l, r = encipher(l, r)
            i += 2

        for box in S:
            i = 0
            while i < 256:
                l ^= salt_words[s]
                r ^= salt_words[(s + 1)]
                s += 2
                if s == salt_size:
                    s = 0
                box[i], box[i + 1] = l, r = encipher(l, r)
                i += 2

    def eks_repeated_expand(self, key_words, salt_words, rounds):
        expand = self.expand
        n = 0
        while n < rounds:
            expand(key_words)
            expand(salt_words)
            n += 1

    def repeat_encipher(self, l, r, count):
        encipher = self.encipher
        n = 0
        while n < count:
            l, r = encipher(l, r)
            n += 1

        return (l, r)