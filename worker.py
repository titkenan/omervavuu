# -*- coding: utf-8 -*-
"""
VxParser Worker — Headless (Cloudflare Workers / Sunucu icin)

Kullanim:
  python worker.py                 → API sunucusunu 192.198.178.20:8080'de baslatir
  python worker.py --port 9000     → Farkli port
  python worker.py --fill-db       → Kanallari tarar
  python worker.py --gen-m3u8      → M3U8 listeleri olusturur
  python worker.py --grab-epg      → EPG verisi cek
  python worker.py --get-vod       → VoD & Serien verisi cek
"""
import os, sys, time, argparse

# ── Proje kok dizinini ayarla ──
rp = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, rp)
sys.path.insert(0, os.path.join(rp, 'helper', 'resolveurl', 'lib'))
sys.path.insert(0, os.path.join(rp, 'helper', 'sites'))
sys.path.insert(0, os.path.join(rp, 'helper'))
sys.path.insert(0, os.path.join(rp, 'utils'))

import utils.common as com
from utils.common import Logger as Logger
com.check()

# ── Dongulu import cozumu: api modulunu gec import et ──
import uvicorn
from uvicorn import Server, Config
from multiprocessing import Process

# ── Headless service baslat (CLI'siz, init ayarlarini otomatik yap) ──
def init_headless():
    """init=1 olarak ayarla, CLI menusu atla"""
    if int(com.get_setting('init') or 0) == 0:
        com.set_setting('init', '1')
        Logger(0, '[INIT] Headless mod: init=1 ayarlandi', 'system', 'boot')

def start_api(host, port):
    init_headless()
    Logger(0, f'[API] Sunucu baslatiliyor: http://{host}:{port}', 'api', 'service')
    uvicorn.run('api:app', host=host, port=port, reload=False, log_level='info')

def fill_db():
    init_headless()
    import utils.vavoo as vavoo
    Logger(0, '[DB] Kanallar taraniyor...', 'db', 'process')
    vavoo.sky_dbfill(m3u8_generation=True)
    Logger(0, '[DB] Tamamlandi!', 'db', 'process')

def gen_m3u8():
    init_headless()
    import utils.vavoo as vavoo
    Logger(0, '[M3U8] Listeler olusturuluyor...', 'db', 'process')
    vavoo.gen_m3u8()
    Logger(0, '[M3U8] Tamamlandi!', 'db', 'process')

def grab_epg():
    init_headless()
    from helper.epg import service as epg
    Logger(0, '[EPG] Veriler cekiliyor...', 'epg', 'process')
    epg.run_grabber()
    Logger(0, '[EPG] Tamamlandi!', 'epg', 'process')

def get_vod():
    init_headless()
    import utils.xstream as xstream
    Logger(0, '[VOD] Veriler cekiliyor...', 'vod', 'process')
    xstream.getMovies()
    Logger(0, '[VOD] Tamamlandi!', 'vod', 'process')

def main():
    parser = argparse.ArgumentParser(description='VxParser Worker — Headless Mode')
    parser.add_argument('--host', default='0.0.0.0', help='Sunucu host')
    parser.add_argument('--port', type=int, default=8080, help='Sunucu port')
    parser.add_argument('--fill-db', action='store_true', help='Kanallari tara & DB doldur')
    parser.add_argument('--gen-m3u8', action='store_true', help='M3U8 listeleri olustur')
    parser.add_argument('--grab-epg', action='store_true', help='EPG verisi cek')
    parser.add_argument('--get-vod', action='store_true', help='VoD & Serien verisi cek')
    args = parser.parse_args()

    if args.fill_db:
        fill_db()
    elif args.gen_m3u8:
        gen_m3u8()
    elif args.grab_epg:
        grab_epg()
    elif args.get_vod:
        get_vod()
    else:
        start_api(args.host, args.port)

if __name__ == '__main__':
    main()
