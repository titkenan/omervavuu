import time, os, json, re, datetime
from multiprocessing import Process
from uvicorn import Server, Config

from utils.common import Logger as Logger
import utils.common as com
import utils.vavoo as vavoo
import utils.xstream as xstream
from helper.epg import service as epg
# UvicornServer'i dogrudan tanimla (dongulu import onlemek icin)
from multiprocessing import Process
class UvicornServer(Process):
    def __init__(self, config):
        super().__init__()
        self.config = config
    def stop(self):
        self.terminate()
    def run(self, *args, **kwargs):
        server = Server(config=self.config)
        server.run()

#cfg = common.config
cachepath = com.cp
jobs = []
proc = {}
proc['api'] = proc['m3u8'] = proc['epg'] = proc['vod'] = proc['m3u8_p'] = proc['epg_p'] = proc['vod_p'] = proc['db_p'] = None
procs = [ 'm3u8', 'epg', 'vod', 'm3u8_p', 'epg_p', 'vod_p', 'db_p' ]


def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


def handler(typ, name=None):
    lang = int(com.get_setting('lang'))
    if typ == 'init':
        if not proc['api']:
            ip = str(com.get_setting('server_host'))
            port = int(com.get_setting('server_port'))
            proc['api'] = UvicornServer(config=Config("api:app", host=ip, port=port, log_level="info", reload=True))
            proc['api'].start()
            Logger(1, 'Successful started...' if lang == 1 else 'Erfolgreich gestartet...', 'api', 'service')
        elif proc['api']: Logger(1, 'Service allready running ...' if lang == 1 else 'Service läuft schon ...', 'api', 'service')
        if not proc['m3u8'] and bool(int(com.get_setting('m3u8_service'))) == True:
            proc['m3u8'] = Process(target=loop_m3u8)
            proc['m3u8'].start()
            Logger(1, 'Successful started...' if lang == 1 else 'Erfolgreich gestartet...', 'db', 'service')
        elif proc['m3u8']: Logger(1, 'Service allready running ...' if lang == 1 else 'Service läuft schon ...', 'db', 'service')
        elif bool(int(com.get_setting('m3u8_service'))) == False: Logger(1, 'Service disabled ...' if lang == 1 else 'Service deaktiviert ...', 'db', 'service')
        if not proc['epg'] and bool(int(com.get_setting('epg_service'))) == True:
            proc['epg'] = Process(target=loop_epg)
            proc['epg'].start()
            Logger(1, 'Successful started...' if lang == 1 else 'Erfolgreich gestartet...', 'epg', 'service')
        elif proc['epg']: Logger(1, 'Service allready running ...' if lang == 1 else 'Service läuft schon ...', 'epg', 'service')
        elif bool(int(com.get_setting('epg_service'))) == False: Logger(1, 'Service disabled ...' if lang == 1 else 'Service deaktiviert ...', 'epg', 'service')
        if not proc['vod'] and bool(int(com.get_setting('vod_service'))) == True:
            proc['vod'] = Process(target=loop_vod)
            proc['vod'].start()
            Logger(1, 'Successful started...' if lang == 1 else 'Erfolgreich gestartet...', 'vod', 'service')
        elif proc['vod']: Logger(1, 'Service allready running ...' if lang == 1 else 'Service läuft schon ...', 'vod', 'service')
        elif bool(int(com.get_setting('vod_service'))) == False: Logger(1, 'Service disabled ...' if lang == 1 else 'Service deaktiviert ...', 'vod', 'service')
    if typ == 'kill':
        for p in procs:
            if proc[p]:
                proc[p].join(timeout=0)
                if proc[p].is_alive():
                    if '_p' in p: Logger(1, 'terminate ...' if lang == 1 else 'töte ...', re.sub('_p', '', p), 'process')
                    else: Logger(1, 'terminate ...' if lang == 1 else 'töte ...', p, 'service')
                    proc[p].terminate()
                    proc[p] = None
        if len(jobs) > 0:
            for job in jobs:
                job.join(timeout=0)
                if job.is_alive():
                    Logger(1, 'terminate ...' if lang == 1 else 'töte ...', 'process', 'jobs')
                    job.terminate()
                    job = None
        if proc['api']:
            Logger(1, 'terminate ...' if lang == 1 else 'töte ...', 'api', 'service')
            proc['api'].stop()
            proc['api'] = None
    if typ == 'service_stop':
        if proc['m3u8']:
            proc['m3u8'].join(timeout=0)
            if proc['m3u8'].is_alive():
                Logger(1, 'terminate ...' if lang == 1 else 'töte ...', 'db', 'service')
                proc['m3u8'].terminate()
                proc['m3u8'] = None
            else: Logger(1, 'not running ...' if lang == 1 else 'läuft noch nicht ...', 'db', 'service')
        else: Logger(1, 'not running ...' if lang == 1 else 'läuft noch nicht ...', 'db', 'service')
        if proc['epg']:
            proc['epg'].join(timeout=0)
            if proc['epg'].is_alive():
                Logger(1, 'terminate ...' if lang == 1 else 'töte ...', 'epg', 'service')
                proc['epg'].terminate()
                proc['epg'] = None
            else: Logger(1, 'not running ...' if lang == 1 else 'läuft noch nicht ...', 'epg', 'service')
        else: Logger(1, 'not running ...' if lang == 1 else 'läuft noch nicht ...', 'epg', 'service')
        if proc['vod']:
            proc['vod'].join(timeout=0)
            if proc['vod'].is_alive():
                Logger(1, 'terminate ...' if lang == 1 else 'töte ...', 'vod', 'service')
                proc['vod'].terminate()
                proc['vod'] = None
            else: Logger(1, 'not running ...' if lang == 1 else 'läuft noch nicht ...', 'vod', 'service')
        else: Logger(1, 'not running ...' if lang == 1 else 'läuft noch nicht ...', 'vod', 'service')
    if typ == 'service_restart':
        if bool(int(com.get_setting('m3u8_service'))) == True:
            if proc['m3u8']:
                proc['m3u8'].join(timeout=0)
                if proc['m3u8'].is_alive():
                    Logger(1, 'terminate ...' if lang == 1 else 'töte ...', 'db', 'service')
                    proc['m3u8'].terminate()
                    proc['m3u8'] = None
            proc['m3u8'] = Process(target=loop_m3u8)
            proc['m3u8'].start()
            Logger(1, 'Successful started...' if lang == 1 else 'Erfolgreich gestartet...', 'db', 'service')
        else: Logger(1, 'Service disabled ...' if lang == 1 else 'Service deaktiviert ...', 'db', 'service')
        if bool(int(com.get_setting('epg_service'))) == True:
            if proc['epg']:
                proc['epg'].join(timeout=0)
                if proc['epg'].is_alive():
                    Logger(1, 'terminate ...' if lang == 1 else 'töte ...', 'epg', 'service')
                    proc['epg'].terminate()
                    proc['epg'] = None
            proc['epg'] = Process(target=loop_epg)
            proc['epg'].start()
            Logger(1, 'Successful started...' if lang == 1 else 'Erfolgreich gestartet...', 'epg', 'service')
        else: Logger(1, 'Service disabled ...' if lang == 1 else 'Service deaktiviert ...', 'epg', 'service')
        if bool(int(com.get_setting('vod_service'))) == True:
            if proc['vod']:
                proc['vod'].join(timeout=0)
                if proc['vod'].is_alive():
                    Logger(1, 'terminate ...' if lang == 1 else 'töte ...', 'vod', 'service')
                    proc['vod'].terminate()
                    proc['vod'] = None
            proc['vod'] = Process(target=loop_vod)
            proc['vod'].start()
            Logger(1, 'Successful started...' if lang == 1 else 'Erfolgreich gestartet...', 'vod', 'service')
        else: Logger(1, 'Service disabled ...' if lang == 1 else 'Service deaktiviert ...', 'vod', 'service')
    if typ == 'db_start':
        if proc['db_p']:
            proc['db_p'].join(timeout=0)
            if proc['db_p'].is_alive():
                Logger(1, 'terminate ...' if lang == 1 else 'töte ...', 'db', 'process')
                proc['db_p'].terminate()
                proc['db_p'] = None
        proc['db_p'] = Process(target=vavoo.sky_dbfill, args=(False,))
        proc['db_p'].start()
        Logger(1, 'Successful started...' if lang == 1 else 'Erfolgreich gestartet...', 'db', 'process')
    if typ == 'epg_start':
        if proc['epg_p']:
            proc['epg_p'].join(timeout=0)
            if proc['epg_p'].is_alive():
                Logger(1, 'terminate ...' if lang == 1 else 'töte ...', 'epg', 'process')
                proc['epg_p'].terminate()
                proc['epg_p'] = None
        proc['epg_p'] = Process(target=epg.run_grabber)
        proc['epg_p'].start()
        Logger(1, 'Successful started...' if lang == 1 else 'Erfolgreich gestartet...', 'epg', 'process')
    if typ == 'm3u8_start':
        if proc['m3u8_p']:
            proc['m3u8_p'].join(timeout=0)
            if proc['m3u8_p'].is_alive():
                Logger(1, 'terminate ...' if lang == 1 else 'töte ...', 'db', 'process')
                proc['m3u8_p'].terminate()
                proc['m3u8_p'] = None
        proc['m3u8_p'] = Process(target=vavoo.gen_m3u8)
        proc['m3u8_p'].start()
        Logger(1, 'Successful started...' if lang == 1 else 'Erfolgreich gestartet...', 'db', 'process')
    if typ == 'vod_start':
        if proc['vod_p']:
            proc['vod_p'].join(timeout=0)
            if proc['vod_p'].is_alive():
                Logger(1, 'terminate ...' if lang == 1 else 'töte ...', 'vod', 'process')
                proc['vod_p'].terminate()
                proc['vod_p'] = None
        proc['vod_p'] = Process(target=xstream.getMovies)
        proc['vod_p'].start()
        Logger(1, 'Successful started...' if lang == 1 else 'Erfolgreich gestartet...', 'vod', 'process')
    return


def loop_m3u8():
    while True:
        now = int(time.time())
        last = int(com.get_setting('m3u8'))
        sleep = int(com.get_setting('m3u8_sleep'))
        lang = int(com.get_setting('lang'))
        if now > last + sleep * 24 * 60 * 60:
            vavoo.sky_dbfill()
            com.set_setting('m3u8', str(now))
        else:
            Logger(1, 'sleeping for %s ...' % str(datetime.timedelta(seconds=last + sleep * 60 * 60 - now)) if lang == 1 else 'schlafe für %s ...' % str(datetime.timedelta(seconds=last + sleep * 60 * 60 - now)), 'db', 'service')
            time.sleep(int(last + sleep * 24 * 60 * 60 - now))
    pass


def loop_epg():
    while True:
        lang = int(com.get_setting('lang'))
        sleep = int(com.get_setting('epg_sleep'))
        now = int(time.time())
        last = int(com.get_setting('epg'))
        if now > last + sleep * 24 * 60 * 60:
            epg.run_grabber()
            com.set_setting('epg', str(now))
        else:
            Logger(1, 'sleeping for %s ...' % str(datetime.timedelta(seconds=last + sleep * 24 * 60 * 60 - now)) if lang == 1 else 'schlafe für %s ...' % str(datetime.timedelta(seconds=last + sleep * 24 * 60 * 60 - now)), 'epg', 'service')
            time.sleep(int(last + sleep * 24 * 60 * 60 - now))
    pass


def loop_vod():
    while True:
        now = int(time.time())
        last = int(com.get_setting('vod'))
        sleep = int(com.get_setting('vod_sleep'))
        lang = int(com.get_setting('lang'))
        if now > last + sleep * 24 * 60 * 60:
            xstream.getMovies()
            com.set_setting('vod', str(now))
        else:
            Logger(1, 'sleeping for %s ...' % str(datetime.timedelta(seconds=last + sleep * 60 * 60 - now)) if lang == 1 else 'schlafe für %s ...' % str(datetime.timedelta(seconds=last + sleep * 60 * 60 - now)), 'vod', 'service')
            time.sleep(int(last + sleep * 24 * 60 * 60 - now))
    pass

