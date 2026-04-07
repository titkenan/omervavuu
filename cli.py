import inquirer, re, time, os, json
from datetime import timedelta

import utils.common as com
from utils.common import Logger as Logger
import utils.xstream as xstream
import utils.vavoo as vavoo
import services

con = com.con0
con1 = com.con1
cache = com.cp


def initMenu():
    c = []
    lang = int(com.get_setting('lang'))
    c.append(("German" if lang == 1 else "Deutsch","0"))
    c.append(("English" if lang == 1 else "Englisch","1"))
    q = [ inquirer.List("item", message="Select Menu Language (Hit [ENTER] to select Item)" if lang == 1 else "Wähle Menü Sprache (Zum bestätigen [ENTER])", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def initMenu2():
    lang = int(com.get_setting('lang'))
    cur = con.cursor()
    c = []
    d = []
    k = []
    for row in cur.execute('SELECT * FROM settings WHERE name="m3u8_service" OR name="epg_service" OR name="vod_service"'):
        info = json.loads(row['info'])
        c.append((info[lang], row['name']))
        if int(row['value']) == 1: d.append(row['name'])
        k.append(row['name'])
    q = [ inquirer.Checkbox("check", message="Services first Config. (select: [RIGHT], deselect: [LEFT], save: [ENTER])" if lang == 1 else "Service erst Einstellung. (makieren: [RECHTS], demakieren: [LINKS], bestätigen: [ENTER])", choices=c, default=d, carousel=True) ]
    quest = inquirer.prompt(q)
    for key in k:
        if str(key) in quest["check"] and not str(key) in d:
            com.set_setting(str(key), str(1))
        if not str(key) in quest["check"] and str(key) in d:
            com.set_setting(str(key), str(0))
    return True

def mainMenu():
    lang = int(com.get_setting('lang'))
    c = []
    c.append((" ","0"))
    c.append(("Settings =>" if lang == 1 else "Einstellungen =>","settings"))
    c.append(("Vavoo Submenü (LiveTV) =>" if lang == 1 else "Vavoo Untermenü (LiveTV) =>","submenu_vavoo"))
    c.append(("Xstream Submenü (VoD's & Series) =>" if lang == 1 else "Xstream Untermenü (VoD's & Series) =>", "submenu_xstream"))
    c.append(("Stop Services", "stop_service"))
    c.append(("Restart Services" if lang == 1 else "Starte Services Neu", "restart_service"))
    c.append(("- Clean Database (Settings)" if lang == 1 else "- Leere Datenbank (Einstellungen)","clean_db"))
    c.append(("- Clear Data Path" if lang == 1 else "- Lösche Data Ordner","clear_data"))
    c.append(("Install vxparser.service into Unix System" if lang == 1 else "Installiere vxparser.service in ein Unix System", "install_py"))
    c.append(("<= Shutdown" if lang == 1 else "<= Herunterfahren","shutdown"))
    q = [ inquirer.List("item", message="Main Menu" if lang == 1 else "Haupt Menu", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def vavooMenu():
    lang = int(com.get_setting('lang'))
    c = []
    c.append((" ","0"))
    c.append(("Settings =>" if lang == 1 else "Einstellungen =>","settings"))
    c.append(("List|Group|Stream Submenü =>" if lang == 1 else "List|Group|Stream Untermenü =>","submenu_lgs"))
    c.append(("Fill Database with LiveTV Data" if lang == 1 else "Fülle Datenbank mit LiveTV Daten", "fill_db"))
    c.append(("Generate M3U8 Lists" if lang == 1 else "Erstelle M3U8 Listen","gen_list"))
    c.append(("Get epg.xml.gz" if lang == 1 else "Hole epg.xml.gz", "get_epg"))
    c.append(("- Clean Database (LiveTV)" if lang == 1 else "- Lösche Datenbank (LiveTV)","clean_db"))
    c.append(("<= Main Menu" if lang == 1 else "<= Haupt Menu","back"))
    q = [ inquirer.List("item", message="Sky Live TV", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def xstreamMenu():
    lang = int(com.get_setting('lang'))
    c = []
    c.append((" ","0"))
    c.append(("Settings =>" if lang == 1 else "Einstellungen =>","settings"))
    c.append(("Global Search" if lang == 1 else "Globale Suche","search"))
    c.append(("Get New VoD & Series" if lang == 1 else "Hole neue VoD & Serien Daten","get_new"))
    c.append(("ReCreate vod+series.m3u8" if lang == 1 else "Erstelle vod+series.m3u8 erneut","gen_lists"))
    c.append(("- Clean Database (Streams)" if lang == 1 else "- Lösche Datenbank (Streams)","clean_db"))
    c.append(("<= Main Menu","back"))
    q = [ inquirer.List("item", message="VoD & Series", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def lgsMenu():
    lang = int(com.get_setting('lang'))
    c = []
    c.append(("<= Back" if lang == 1 else "<= Zurück","back"))
    c.append(("M3U List Menü =>" if lang == 1 else "M3U8 Listen Menü =>","lmenu"))
    c.append(("Group Menü =>" if lang == 1 else "Gruppen Menü =>","gmenu"))
    c.append(("Stream Menü =>" if lang == 1 else "Stream Menü =>","smenu"))
    q = [ inquirer.List("item", message="List|Group|Stream Menu", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def lMenu():
    lang = int(com.get_setting('lang'))
    c = []
    c.append(("<= Back" if lang == 1 else "<= Zurück","back"))
    c.append(("Add New List" if lang == 1 else "Neue M3u8 Liste hinzufügen","add_list"))
    c.append(("Edit List" if lang == 1 else "Bearbeite M3u8 Liste","edit_list"))
    c.append(("Delete List" if lang == 1 else "Lösche M3u8 Liste","del_list"))
    q = [ inquirer.List("item", message="M3U8 List Menu" if lang == 1 else "M3u8 Listen Menu", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def gMenu():
    lang = int(com.get_setting('lang'))
    c = []
    c.append(("<= Back" if lang == 1 else "<= Zurück","back"))
    c.append(("Add New Group" if lang == 1 else "Neue Gruppe hinzufügen","add_group"))
    c.append(("Edit Group" if lang == 1 else "Bearbeite eine Gruppe","edit_group"))
    c.append(("Delete Group" if lang == 1 else "Lösche eine Gruppe","del_group"))
    q = [ inquirer.List("item", message="Group Menu" if lang == 1 else "Gruppen Menu", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def sMenu():
    lang = int(com.get_setting('lang'))
    c = []
    c.append(("<= Back" if lang == 1 else "<= Zurück","back"))
    c.append(("Add Streams to Group" if lang == 1 else "Füge Streams zu einer Gruppe hinzu","add_streams"))
    c.append(("Edit Streams in List" if lang == 1 else "Bearbeite Streams in M3u8 Liste","edit_streams"))
    q = [ inquirer.List("item", message="Stream Menu", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    return quest['item']


def xstreamSettings():
    lang = int(com.get_setting('lang'))
    cur = con.cursor()
    c = []
    d = []
    keys = []
    vals = []
    x = 0
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Xstream') + '"'):
        site = re.sub('_auto|_search', '', row['name'])
        if "_auto" in row['name']: name = site+': auto list creation?' if lang == 1 else site+': automatische list erstellung?'
        else: name = site+': global search?' if lang == 1 else site+': globale suche?'
        c.append((name, str(x)))
        if int(row['value']) == 1: d.append(str(x))
        keys.append(row['name'])
        vals.append(row['value'])
        x += 1
    q = [ inquirer.Checkbox("check", message="Site Settings" if lang == 1 else "Seiten Einstellungen", choices=c, default=d, carousel=True) ]
    quest = inquirer.prompt(q)
    for y in range(0, x):
        if str(y) in quest["check"] and not str(y) in d:
            com.set_setting(keys[y], str(1))
        if not str(y) in quest["check"] and str(y) in d:
            com.set_setting(keys[y], str(0))
    return True


def mainSettings():
    lang = int(com.get_setting('lang'))
    cur = con.cursor()
    c = []
    rows = []
    x = 0
    l = 0
    c.append(("<= Back" if lang == 1 else "<= Zurück","-1"))
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Main') + '"'):
        if row['type'] == 'text':
            val = row['value']
        if row['type'] == 'bool' or row['type'] == 'select':
            values = json.loads(row['values'])
            val = values[row['value']]
        if len(val) > l:
            l = len(val)
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Main') + '"'):
        rows.append(row)
        if row['type'] == 'text':
            val = row['value']
        if row['type'] == 'bool' or row['type'] == 'select':
            values = json.loads(row['values'])
            val = values[row['value']]
        t = '] '
        if not l - len(val) == 0:
            for i in range(0, l-len(val)):
                t += ' '
        inf = json.loads(str(row['info']))
        c.append(('['+val+t+inf[lang], str(x)))
        x += 1
    q = [ inquirer.List("item", message="Main Settings" if lang == 1 else "Haupt Einstellungen", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    if not quest["item"] == '-1':
        row = rows[int(quest["item"])]
        if row['type'] == 'text':
            q2 = [ inquirer.Text("input", message="edit: "+row["name"] if lang == 1 else "bearbeite: "+row["name"], default=row["value"]) ]
            quest2 = inquirer.prompt(q2)
            com.set_setting(row["name"], quest2["input"])
        if row['type'] == 'bool':
            values = json.loads(row['values'])
            for v in values:
                if not v == row['value']:
                    new = v
                    break
            com.set_setting(row["name"], new)
        if row['type'] == 'select':
            c2 = []
            values = json.loads(row['values'])
            for v in values:
                c2.append(('['+values[v]+']', v))
            q2 = [ inquirer.List("item", message="select: "+row['name'] if lang == 1 else "gewählt: "+row['name'], choices=c2, carousel=True) ]
            quest2 = inquirer.prompt(q2)
            com.set_setting(row["name"], quest2["item"])
    else: return 'back'
    return True


def vavooSettings():
    lang = int(com.get_setting('lang'))
    cur = con.cursor()
    c = []
    rows = []
    x = 0
    l = 0
    c.append(("<= Back" if lang == 1 else "<= Zurück","-1"))
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Vavoo') + '"'):
        if row['type'] == 'text':
            val = row['value']
        if row['type'] == 'bool' or row['type'] == 'select':
            values = json.loads(row['values'])
            val = values[row['value']]
        if len(val) > l:
            l = len(val)
    for row in cur.execute('SELECT * FROM settings WHERE grp="' + str('Vavoo') + '"'):
        rows.append(row)
        if row['type'] == 'text':
            val = row['value']
        if row['type'] == 'bool' or row['type'] == 'select':
            values = json.loads(row['values'])
            val = values[row['value']]
        t = '] '
        if not l - len(val) == 0:
            for i in range(0, l-len(val)):
                t += ' '
        inf = json.loads(str(row['info']))
        c.append(('['+val+t+inf[lang], str(x)))
        x += 1
    q = [ inquirer.List("item", message="EPG Settings" if lang == 1 else "Fernsehzeitung's Einstellungen", choices=c, carousel=True) ]
    quest = inquirer.prompt(q)
    if not quest["item"] == '-1':
        row = rows[int(quest["item"])]
        if row['type'] == 'text':
            q2 = [ inquirer.Text("input", message="edit: "+row["name"] if lang == 1 else "bearbeite: "+row["name"], default=row["value"]) ]
            quest2 = inquirer.prompt(q2)
            com.set_setting(row["name"], quest2["input"])
        if row['type'] == 'bool':
            values = json.loads(row['values'])
            for v in values:
                if not v == row['value']:
                    new = v
                    break
            com.set_setting(row["name"], new)
        if row['type'] == 'select':
            c2 = []
            values = json.loads(row['values'])
            for v in values:
                c2.append(('['+values[v]+']', v))
            q2 = [ inquirer.List("item", message="select: "+row['name'] if lang == 1 else "wähle: "+row["name"], choices=c2, carousel=True) ]
            quest2 = inquirer.prompt(q2)
            com.set_setting(row["name"], quest2["item"])
    else: return 'back'
    return True


def premenu():
    init = int(com.get_setting('init'))
    lang = int(com.get_setting('lang'))
    if init == 0:
        menu = 'init'
        while True:
            if menu == 'init':
                quest = initMenu()
                if not quest:
                    Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'init', 'settings')
                    return
                elif quest != '':
                    com.set_setting('lang', str(quest))
                    menu = 'next'
                    #return
            if menu == 'next':
                quest = initMenu2()
                if not quest: Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'init', 'settings')
                else:
                    com.set_setting('init', str(1))
                    return True
    else: return


def menu():
    lang = int(com.get_setting('lang'))
    menü = 'main'
    while True:
        if menü == 'msettings':
            quest = mainSettings()
            if not quest: Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'main', 'settings')
            elif quest == 'back': menü = 'main'
        if menü == 'main':
            time.sleep(0.2)
            item = mainMenu()
            if item == 'submenu_vavoo': menü = 'vavoo'
            if item == 'submenu_xstream': menü = 'xstream'
            if item == 'settings':
                menü = 'msettings'
                quest = mainSettings()
                if not quest: Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'main', 'settings')
                elif quest == 'back': menü = 'main'
            if item == 'shutdown':
                Logger(0, "Quitting Now..." if lang == 1 else "Schließe sofort...")
                services.handler('kill')
                con.close()
                break
            if item == 'stop_service': services.handler('service_stop')
            if item == 'restart_service': services.handler('service_restart')
            if item == 'clean_db':
                c = []
                c.append((" ","0"))
                c.append(("Yes" if lang == 1 else "Ja","yes"))
                c.append(("No" if lang == 1 else "Nein", "no"))
                c.append(("<= Back" if lang == 1 else "<= Zurück","back"))
                q = [ inquirer.List("item", message="Really Clean settings Database?" if lang == 1 else "Einstellungen wirklich aus Datenbank löschen?", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if quest['item'] == 'yes':
                    clean = com.clean_tables('settings')
                    if not clean: Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'db', 'clean')
                    else: Logger(0, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'db', 'clean')
            if item == 'clear_data':
                c = []
                c.append((" ","0"))
                c.append(("Yes" if lang == 1 else "Ja","yes"))
                c.append(("No" if lang == 1 else "Nein", "no"))
                c.append(("<= Back" if lang == 1 else "<= Zurück","back"))
                q = [ inquirer.List("item", message="Really Clear data Path?" if lang == 1 else "Daten Ordner wirklich löschen?", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if quest['item'] == 'yes':
                    services.handler('kill')
                    clear = com.clear_cache()
                    break
            if item == 'install_py':
                c = []
                c.append((" ","0"))
                c.append(("Yes" if lang == 1 else "Ja","yes"))
                c.append(("No" if lang == 1 else "Nein", "no"))
                c.append(("<= Back" if lang == 1 else "<= Zurück","back"))
                q = [ inquirer.List("item", message="Install vxparser.service into System?" if lang == 1 else "vxparser.service wirklich in das System installieren?", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if quest['item'] == 'yes':
                    import install
                    install.main(lang)
        if menü == 'xstream':
            item = xstreamMenu()
            if item == 'settings':
                quest = xstreamSettings()
                if not quest: Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'vod', 'settings')
                else: Logger(1, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'vod', 'settings')
            if item == 'back': menü = 'main'
            if item == 'clean_db':
                c = []
                c.append((" ","0"))
                c.append(("Yes" if lang == 1 else "Ja","yes"))
                c.append(("No" if lang == 1 else "Nein", "no"))
                c.append(("<= Back" if lang == 1 else "<= Zurück","back"))
                q = [ inquirer.List("item", message="Really clean Stream Database?" if lang == 1 else "Streams wirklich aus Datenbank löschen?", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if quest['item'] == 'yes':
                    clean = com.clean_tables('streams')
                    if not clean: Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'db', 'clean')
                    else: Logger(0, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'db', 'clean')
            if item == 'get_new': services.handler('vod_start')
                #st = int(time.time())
                #movies = xstream.getMovies()
                #if not movies: Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'vod', 'get')
                #else: Logger(0, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'vod', 'get')
                #Logger(1, 'Completed in %s' % timedelta(seconds=int(time.time())-st) if lang == 1 else 'Fertig in %s' % timedelta(seconds=int(time.time())-st), 'vod', 'get')
            if item == 'gen_lists':
                lists = xstream.genLists()
                if not lists: Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'vod', 'gen')
                else: Logger(0, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'vod', 'gen')
            if item == 'search':
                quest = inquirer.prompt([inquirer.Text("item", message="Search for?" if lang == 1 else "Suche nach?")])
                ser = xstream.search(quest['item'])
        if menü == 'vavoo':
            item = vavooMenu()
            if item == 'back': menü = 'main'
            if item == 'submenu_lgs': menü = 'lgs'
            if item == 'gen_list': services.handler('m3u8_start')
            if item == 'get_epg': services.handler('epg_start')
            if item == 'settings':
                menü = 'vsettings'
                quest = vavooSettings()
                if not quest: Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'vavoo', 'settings')
                elif quest == 'back': menü = 'vavoo'
            if item == 'clean_tv_db':
                c = []
                c.append((" ","0"))
                c.append(("Yes" if lang == 1 else "Ja","yes"))
                c.append(("No" if lang == 1 else "Nein", "no"))
                c.append(("<= Back" if lang == 1 else "<= Zurück","back"))
                q = [ inquirer.List("item", message="Really clean LiveTV Database?" if lang == 1 else "Wirklich LiveTV daten aus Datenbank löschen?", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if quest['item'] == 'yes':
                    clean = com.clean_tables('live')
                    if not clean: Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'db', 'clean')
                    else: Logger(0, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'db', 'clean')
            if item == 'fill_db': services.handler('db_start')
        if menü == 'vsettings':
            quest = vavooSettings()
            if not quest: Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'vavoo', 'settings')
            elif quest == 'back': menü = 'vavoo'
        if menü == 'lgs':
            item = lgsMenu()
            if item == 'back': menü = 'vavoo'
            if item == 'lmenu': menü = 'lmenu'
            if item == 'gmenu': menü = 'gmenu'
            if item == 'smenu': menü = 'smenu'
        if menü == 'lmenu':
            item = lMenu()
            if item == 'back': menü = 'lgs'
            if item == 'add_list':
                q = [ inquirer.Text("input", message="List Name", default='') ]
                quest = inquirer.prompt(q)
                cur = con.cursor()
                if quest["input"] == '': Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'add', 'list')
                else:
                    cur.execute('INSERT INTO lists VALUES (NULL,"' + str(quest["input"]) + '","' + str('1') + '")')
                    con.commit()
                    Logger(0, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'add', 'list')
            if item == 'edit_list':
                c = []
                c.append(("<= Back","-1"))
                cur = con.cursor()
                cur.execute('SELECT * FROM lists WHERE custom="1" ORDER BY id ASC')
                rows = cur.fetchall()
                for d in rows:
                    c.append((str(d['name']),str(d['id'])))
                q = [ inquirer.List("item", message="Edit Playlist" if lang == 1 else "Bearbeite Playlist", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if not quest['item'] == '-1':
                    cur.execute('SELECT * FROM lists WHERE id="' + quest["item"] + '"')
                    dat = cur.fetchone()
                    if dat:
                        q2 = [ inquirer.Text("input", message="edit", default=dat["name"]) ]
                        quest2 = inquirer.prompt(q2)
                        if quest2["input"] == '': Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'edit', 'list')
                        else:
                            cur.execute('UPDATE lists SET name="' + quest2["input"] + '" WHERE id="' + quest["item"] + '"')
                            con.commit()
                            Logger(0, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'edit', 'list')
            if item == 'del_list':
                cur = con.cursor()
                c = []
                c.append(("<= Back" if lang == 1 else "<= Zurück","-1"))
                cur.execute('SELECT * FROM lists WHERE custom="1" ORDER BY id ASC')
                rows = cur.fetchall()
                for d in rows:
                    c.append((str(d['name']),str(d['id'])))
                q = [ inquirer.List("item", message="Delete Playlist" if lang == 1 else "Lösche Playlist", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if not quest['item'] == '-1':
                    cur.execute('DELETE FROM lists WHERE id="'+ quest["item"] +'"')
                    con.commit()
                    Logger(0, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'delete', 'list')
        if menü == 'gmenu':
            item = gMenu()
            if item == 'back': menü = 'lgs'
            if item == 'add_group':
                c = []
                c.append(("<= Back" if lang == 1 else "<= Zurück","-1"))
                cur = con.cursor()
                for d in cur.execute('SELECT * FROM lists'):
                    c.append((str(d['name']),str(d['id'])))
                q = [ inquirer.List("item", message="Select Playlist" if lang == 1 else "Wähle Playlist aus", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if not quest['item'] == '-1':
                    lid = quest['item']
                    q2 = [ inquirer.Text("input", message="Group Name", default='') ]
                    quest2 = inquirer.prompt(q2)
                    if quest2["input"] == '': Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'add', 'group')
                    else:
                        cur.execute('INSERT INTO categories VALUES (NULL,"live","' + str(quest2["input"]) + '","' + str(lid) + '","1")')
                        con.commit()
                        Logger(0, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'add', 'group')
            if item == 'edit_group':
                cur = con.cursor()
                c = []
                c.append(("<= Back" if lang == 1 else "<= Zurück","-1"))
                tlid = None
                cur.execute('SELECT * FROM categories WHERE custom="1" ORDER BY lid ASC')
                rows = cur.fetchall()
                for d in rows:
                    if not d['lid'] == tlid:
                        cur.execute('SELECT * FROM lists WHERE id="' + str(d['lid']) + '"')
                        data = cur.fetchone()
                        c.append((data['name'] + ":",""))
                        tlid = d['lid']
                    c.append((str(d['category_name']),str(d['category_id'])))
                q = [ inquirer.List("item", message="Select Group" if lang == 1 else "Wähle Gruppe", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if not quest["item"] == '' and not quest["item"] == '-1':
                    cur.execute('SELECT * FROM categories WHERE category_id="' + quest["item"] + '"')
                    dat = cur.fetchone()
                    if dat:
                        q2 = [ inquirer.Text("input", message="edit", default=dat["category_name"]) ]
                        quest2 = inquirer.prompt(q2)
                        if quest2["input"] == '': Logger(3, 'Error!' if lang == 1 else 'Fehler!', 'edit', 'group')
                        else:
                            cur.execute('UPDATE categories SET category_name="' + quest2["input"] + '" WHERE category_id="' + quest["item"] + '"')
                            con.commit()
                            Logger(0, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'edit', 'group')
            if item == 'del_group':
                cur = con.cursor()
                c = []
                c.append(("<= Back" if lang == 1 else "<= Zurück","-1"))
                tlid = None
                cur.execute('SELECT * FROM categories WHERE custom="1" ORDER BY lid ASC')
                rows = cur.fetchall()
                for d in rows:
                    if not d['lid'] == tlid:
                        cur.execute('SELECT * FROM lists WHERE id="' + str(d['lid']) + '"')
                        data = cur.fetchone()
                        c.append((data['name'] + ":",""))
                        tlid = d['lid']
                    c.append((str(d['category_name']),str(d['category_id'])))
                q = [ inquirer.List("item", message="Select Group" if lang == 1 else "Wähle Gruppe", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if not quest["item"] == '' and not quest["item"] == '-1':
                    cur.execute('DELETE FROM categories WHERE category_id="'+ quest["item"] +'"')
                    con.commit()
                    Logger(0, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'delete', 'group')
        if menü == 'smenu':
            item = sMenu()
            lang = int(com.get_setting('lang'))
            if item == 'back': menü = 'lgs'
            if item == 'add_streams':
                cur = con.cursor()
                c = []
                c.append(("<= Back" if lang == 1 else "<= Zurück","-1"))
                tlid = None
                cur.execute('SELECT * FROM categories WHERE custom="1" ORDER BY lid ASC')
                rows = cur.fetchall()
                for d in rows:
                    if not d['lid'] == tlid:
                        cur.execute('SELECT * FROM lists WHERE id="' + str(d['lid']) + '"')
                        data = cur.fetchone()
                        c.append((data['name'] + ":",""))
                        tlid = d['lid']
                    c.append((str(d['category_name']),str(d['category_id'])))
                q = [ inquirer.List("item", message="Select Group" if lang == 1 else "Wähle Gruppe", choices=c, carousel=True) ]
                quest = inquirer.prompt(q)
                if not quest["item"] == '' and not quest["item"] == '-1':
                    c = []
                    c.append(("<= Back","-1"))
                    cur.execute('SELECT * FROM lists WHERE custom="0" ORDER BY id ASC')
                    rows = cur.fetchall()
                    for d in rows:
                        c.append((str(d['name']),str(d['name'])))
                    q = [ inquirer.List("item", message="Select Stream Country" if lang == 1 else "Wähle Streams vom Country", choices=c, carousel=True) ]
                    quest2 = inquirer.prompt(q)
                    if not quest2["item"] == '' and not quest2["item"] == '-1':
                        c = []
                        d = []
                        e = []
                        cur1 = con1.cursor()
                        cur1.execute('SELECT * FROM channel WHERE country="'+ quest2["item"] +'" ORDER BY name ASC')
                        rows1 = cur1.fetchall()
                        for ch in rows1:
                            cids = json.loads(ch['cid'])
                            c.append((str(ch['name']), str(ch['id'])))
                            if int(quest['item']) in cids: d.append(str(ch['id']))
                            e.append(str(ch['id']))
                        q = [ inquirer.Checkbox("check", message="Add Streams" if lang == 1 else "Füge Streams hinzu", choices=c, default=d, carousel=True) ]
                        quest3 = inquirer.prompt(q)
                        for i in e:
                            if i in quest3["check"] and not i in d:
                                cur1.execute('SELECT * FROM channel WHERE id="'+ i +'"')
                                row = cur1.fetchone()
                                if row:
                                    cids = json.loads(row['cid'])
                                    cids.append(int(quest["item"]))
                                    cur1.execute('UPDATE channel SET cid="' + str(cids) + '" WHERE id="' + i + '"')
                            if i in d and not i in quest3["check"]:
                                cur1.execute('SELECT * FROM channel WHERE id="'+ i +'"')
                                row = cur1.fetchone()
                                if row:
                                    cids = json.loads(row['cid'])
                                    z = 0
                                    for u in range(0, len(cids)-1):
                                        if cids[u] == int(quest["item"]):
                                            break
                                        z += 1
                                    del cids[z]
                                    cur1.execute('UPDATE channel SET cid="' + str(cids) + '" WHERE id="' + i + '"')
                        con1.commit()
                        Logger(0, 'Successful ...' if lang == 1 else 'Erfolgreich ...', 'add', 'streams')
            # if item == 'edit_streams':

