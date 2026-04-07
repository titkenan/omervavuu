import sys, os, pwd, base64, re, subprocess

UFILE = b'[Unit]\nSourcePath=\nDescription=MastaaaS VxParser Service\nWants=network-online.target\nAfter=multi-user.target\nStartLimitIntervalSec=0\n \n[Service]\nUser=\nRestart=always\nRestartSec=5\nExecStart=\nExecReload=\nExecStop=\n \n[Install]\nWantedBy=multi-user.target\n\n\n'
SFILE = b'#!/bin/bash\n\nROOTPATH=\nSERVICE=$ROOTPATH/vx-service.py\n\nstart() {\n    pids=$(ps aux | grep \'vx-service.py\' | grep -v grep | awk \'{print $2}\')\n    if ! [ "$pids" == "" ]; then\n        echo \'vxparser.service is already running\'\n        return 1\n    fi\n    echo \'Starting VxParser Service ...\'\n    python3 $SERVICE &\n    echo \'Running in foreground...\'\n    sleep infinity\n}\n\nstop() {\n    pids=$(ps aux | grep "vx-service.py" | grep -v grep | awk \'{print $2}\')\n    if [ "$pids" == "" ]; then\n        echo "vxparser.service is not running"\n        return 1\n    fi\n    echo "Stopping VxParser Service ..."\n    kill -9 $pids 2>/dev/null\n    sleep 1\n}\n\nrestart() {\n    stop\n    sleep 1\n    start\n}\n\ncase "$1" in\n    start) start ;;\n    stop) stop ;;\n    reload) restart ;;\n    restart) restart ;;\n    *) echo "Usage: $0 {start|stop|restart|reload}" ;;\nesac\n\nexit 0\n\n'
MFILE = b'import utils.common as com\ncom.check()\n\nimport cli, services\n\n\ndef main():\n    services.handler(\'init\')\n    #cli.menu()\n\n\nif __name__ == "__main__":\n    main()\n'

CUID = os.getuid()
CU = pwd.getpwuid(CUID)[0]
RP = os.path.dirname(os.path.abspath(__file__))
PUID = os.stat(RP).st_uid
PU = pwd.getpwuid(PUID)[0]


class col:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    YELLOW = '\033[33m'
    ENDC = '\033[0m'
    DEFAULT = '\033[0m'
    BOLD = '\033[1m'


def printc(rText, rColour=col.OKBLUE, rPadding=0):
    print("%s ┌─────────────────────────────────────────────────┐ %s" % (rColour, col.ENDC))
    for i in range(rPadding): print("%s │                                                 │ %s" % (rColour, col.ENDC))
    if isinstance(rText, str):
        print("%s │ %s%s%s │ %s" % (rColour, " "*round(23-(len(rText)/2)), rText, " "*round(46-(22-(len(rText)/2))-len(rText)), col.ENDC))
    elif isinstance(rText, list):
        for text in rText:
            print("%s │ %s%s%s │ %s" % (rColour, " "*round(23-(len(text)/2)), text, " "*round(46-(22-(len(text)/2))-len(text)), col.ENDC))
    for i in range(rPadding): print("%s │                                                 │ %s" % (rColour, col.ENDC))
    print("%s └─────────────────────────────────────────────────┘ %s" % (rColour, col.ENDC))
    print(" ")


def pre_check(lang=1):
    if not CUID == 0:
        printc(["You need to be run this Script @ root!" if lang == 1 else "Dieses Script muss als Admin gestartet werden!"], col.FAIL)
        if prompt_sudo() != 0: return False
        else: proc = subprocess.call("sudo -S python3 install.py".split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if os.path.exists(os.path.join(RP, 'service')): os.remove(os.path.join(RP, 'service'))
    if os.path.exists(os.path.join(RP, 'vx-service.py')): os.remove(os.path.join(RP, 'vx-service.py'))
    if os.path.exists("/etc/systemd/system/vxparser.service"): os.remove("/etc/systemd/system/vxparser.service")
    return True


def prompt_sudo():
    ret = CUID
    if os.geteuid() != 0:
        msg = "[sudo] password for %u:"
        ret = subprocess.run("sudo -p '%s' -S python3 %s/install.py" % (msg, RP), shell=True)
    return ret


def main(lang=1):
    pre = pre_check(lang)
    if pre == True: printc(["Welcome to my" if lang == 1 else "Willkommen zu meiner", "vxparser.service Installation ..."], col.HEADER)
    else: return False
    if not CU == PU:
        printc(["Current User of this Directory is: %s" % PU if lang == 1 else "Aktueller User dieses Ordners ist: %s" % PU, "Would you like to install service as %s?" % PU if lang == 1 else "Möchten sie den Service als %s installieren?" % PU ], col.WARNING)
        i = input("(Y/n): " if lang == 1 else "(J/n): ")
        if i == "" or i.upper() in [ "YES", "Y", "J", "JA" ]: USER = PU
        else: USER = CU
    else: USER = CU
    printc("Install Services as User: %s" % USER if lang == 1 else "Installiere Services als User: %s" % USER, col.DEFAULT)

    printc(["Creating File:" if lang == 1 else "Erstelle Datei:", str(os.path.join(RP, 'service')) ], col.DEFAULT)
    rFile = open(os.path.join(RP, 'service'), "wb")
    rFile.write(SFILE)
    rFile.close()
    if not os.path.exists(os.path.join(RP, 'service')): 
        return printc(["Failed!" if lang == 1 else "Fehler!","Please try again ..." if lang == 1 else "Bitte erneut versuchen ..."], col.FAIL)
    os.system("sed -i -e 's|ROOTPATH=|ROOTPATH=%s|g' %s" %(RP, str(os.path.join(RP, 'service'))))
    os.system("chmod +x %s" % os.path.join(RP, 'service'))
    if not USER == 'root':
        os.system('chown %s:%s %s' %(USER, USER, str(os.path.join(RP, 'service'))))

    printc(["Creating File:" if lang == 1 else "Erstelle Datei:", str(os.path.join(RP, 'vx-service.py')) ], col.DEFAULT)
    rFile = open(os.path.join(RP, 'vx-service.py'), "wb")
    rFile.write(MFILE)
    rFile.close()
    if not os.path.exists(os.path.join(RP, 'vx-service.py')):
        return printc(["Failed!" if lang == 1 else "Fehler!","Please try again ..." if lang == 1 else "Bitte erneut versuchen ..."], col.FAIL)
    os.system("chmod +x %s" % os.path.join(RP, 'vx-service.py'))
    if not USER == 'root':
        os.system('chown %s:%s %s' %(USER, USER, str(os.path.join(RP, 'vx-service.py'))))

    printc(["Creating File:" if lang == 1 else "Erstelle Datei:", "/etc/systemd/system/vxparser.service" ], col.DEFAULT)
    rFile = open("/etc/systemd/system/vxparser.service", "wb")
    rFile.write(UFILE)
    rFile.close()
    if not os.path.exists("/etc/systemd/system/vxparser.service"):
        return printc(["Failed!" if lang == 1 else "Fehler!","Please try again ..." if lang == 1 else "Bitte erneut versuchen ..."], col.FAIL)
    os.system("sed -i -e 's|SourcePath=|SourcePath=%s|g' %s" %(str(os.path.join(RP, 'service')), "/etc/systemd/system/vxparser.service"))
    os.system("sed -i -e 's|User=|User=%s|g' %s" %(USER, "/etc/systemd/system/vxparser.service"))
    os.system("sed -i -e 's|ExecStart=|ExecStart=/bin/bash %s start|g' %s" %(str(os.path.join(RP, 'service')), "/etc/systemd/system/vxparser.service"))
    os.system("sed -i -e 's|ExecReload=|ExecReload=/bin/bash %s reload|g' %s" %(str(os.path.join(RP, 'service')), "/etc/systemd/system/vxparser.service"))
    os.system("sed -i -e 's|ExecStop=|ExecStop=/bin/bash %s stop|g' %s" %(str(os.path.join(RP, 'service')), "/etc/systemd/system/vxparser.service"))
    os.system("sudo chmod +x /etc/systemd/system/vxparser.service")
    printc("Everything looks Good !" if lang == 1 else "Alles sieht Gut aus !", col.OKGREEN)
    printc("Would you like to enable Service now?" if lang == 1 else "Möchten sie den Service jetzt aktivieren?", col.WARNING)
    i = input("(Y/n): " if lang == 1 else "(J/n): ")
    if i == "" or i.upper() in [ "YES", "Y", "J", "JA" ]:
        os.system("sudo systemctl daemon-reload")
        os.system("sudo systemctl enable vxparser.service")
        os.system("sudo systemctl start vxparser.service")
    else:
        printc(["OK!","To enable Service run:" if lang == 1 else "Zur Service aktivierung tippe ein:", "sudo systemctl daemon-reload", "sudo systemctl enable vxparser.service", "sudo systemctl start vxparser.service"], col.DEFAULT)
    printc(["Everything is Done !" if lang == 1 else "Alles in Ordnung !", "Have fun with it ..." if lang == 1 else "Viel Spass mit dem vxparser ...", "Copyright by Mastaaa @2025"], col.OKBLUE)
    return


if __name__ == "__main__":
    l = 0
    main(0)
