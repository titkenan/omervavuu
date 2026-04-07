import os, sys
from time import sleep
rp = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(rp)
sys.path.append(os.path.join(rp, 'helper', 'resolveurl', 'lib'))
sys.path.append(os.path.join(rp, 'helper', 'sites'))
sys.path.append(os.path.join(rp, 'helper'))
sys.path.append(os.path.join(rp, 'utils'))
import utils.common as com
com.check()

import cli, services


def main():
    while True:
        init = int(com.get_setting('init'))
        if init == 0: cli.premenu()
        elif init == 1: break
        sleep(1)
    services.handler('init')
    cli.menu()


if __name__ == "__main__":
    main()
