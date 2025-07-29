import collections

class LauncherFlavour:
    UNKNOWN = 0
    WG = 1
    CHINA_360 = 2
    STEAM = 3
    LESTA = 4
    STANDALONE = 5
    DEFAULT = WG

_LauncherMetadata = collections.namedtuple('LauncherMetadata', ('flavour', 'path', 'pointer', 'executable'))

LAUNCHERS_METADATA = (
    _LauncherMetadata(LauncherFlavour.WG, 'Wargaming.net\\GameCenter', 'data\\wgc_path.dat', 'wgc.exe'),
    _LauncherMetadata(LauncherFlavour.CHINA_360, '360 Wargaming\\GameCenter', 'data\\wgc_path.dat', 'wgc.exe'),
    _LauncherMetadata(LauncherFlavour.STEAM, 'Wargaming.net\\GameCenter for Steam', 'data\\wgc_path.dat', 'wgc.exe'),
    _LauncherMetadata(LauncherFlavour.LESTA, 'Lesta\\GameCenter', 'data\\lgc_path.dat', 'lgc.exe'),
    _LauncherMetadata(LauncherFlavour.STANDALONE, '', '', '')
)

class ClientBranch:
    UNKNOWN = 0
    RELEASE = 1
    COMMON_TEST = 2
    SUPERTEST = 3
    SANDBOX = 4


class ClientExecutableName:
    WG = 'WorldOfTanks.exe'
    LESTA = 'Tanki.exe'
    DEFAULT = WG


class ClientReplayName:
    WG = 'wotreplay'
    LESTA = 'mtreplay'
    DEFAULT = WG


class ClientType:
    UNKNOWN = 0
    SD = 1
    HD = 2


class ClientRealm:
    EU = 'EU'
    NA = 'NA'
    ASIA = 'ASIA'
    CT = 'CT'
    CN = 'CN'
    RU = 'RU'
    RPT = 'RPT'

CLIENT_REALM_TO_LAUNCHER_FLAVOUR = {
    ClientRealm.EU: LauncherFlavour.WG,
    ClientRealm.NA: LauncherFlavour.WG,
    ClientRealm.ASIA: LauncherFlavour.WG,
    ClientRealm.CT: LauncherFlavour.WG,
    ClientRealm.CN: LauncherFlavour.CHINA_360,
    ClientRealm.RU: LauncherFlavour.LESTA,
    ClientRealm.RPT: LauncherFlavour.LESTA,
}
