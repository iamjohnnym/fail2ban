#!/usr/bin/env python

from sys import argv
import tarfile
import os
from shutil import copyfile

script, domain = argv

url = "wget http://sourceforge.net/projects/fail2ban/files/fail2ban-stable/fail2ban-0.8.4/fail2ban-0.8.4.tar.bz2/download"
os.system(url)

mytarfile = "fail2ban-0.8.4.tar.bz2"

extractTarPath = '.'

tfile = tarfile.open(mytarfile)

if tarfile.is_tarfile(mytarfile):
    print "tar file contents:"
    print tfile.list(verbose=False)
    tfile.extractall(extractTarPath)
else:
    print mytarfile + " is not a tarfile."

os.system('python fail2ban-0.8.4/setup.py install')

copyfile('./fail2ban-0.8.4/files/redhat-initd', '/etc/init.d/fail2ban')
copyfile('/etc/fail2ban/jail.conf', '/etc/fail2ban/jail.conf-mtorg')
os.system('chkconfig --add fail2ban')
os.system('chkconfig fail2ban on')

jail_conf = """
#################################################
#    Fail2Ban jail.local configuration file     #   
#################################################
#           http://mediatemple.net/             #
#                                               #
# The DEFAULT allows a global definition of the #
#  options. They can be overridden in each jail #
#                   afterwards.                 #
#################################################

[DEFAULT]

# ignore our IP ranges
ignoreip = 127.0.0.1

# "bantime" is the number of seconds that a host is banned.
bantime  = 2400

# A host is banned if it has generated "maxretry" during the last "findtime"
# seconds.
findtime  = 600

# "maxretry" is the number of failures before a host get banned.
maxretry = 3

# Don't know how well other backend options work.
backend = polling

[ssh-iptables]

enabled      = true
filter       = sshd
action       = iptables[
                name     = SSH, 
                port     = ssh, 
                protocol = tcp
                ]
sendmail-whois[
    name     = SSH, 
    dest     = fail2ban@%s, 
    sender   = www@%s 
    ]
logpath      = /var/log/secure
maxretry     = 3

[proftpd-iptables]

enabled      = true 
filter       = proftpd
action       = iptables[
                name     = ProFTPD, 
                port     = ftp, 
                protocol = tcp
                ]
sendmail-whois[
    name     = ProFTPD, 
    dest     = fail2ban@%s, 
    sender   = www@%s
    ]
logpath      = /var/log/secure
maxretry     = 3

[postfix]

enabled      = true
filter       = postfix
action       = iptables[
                name     = Postfix, 
                port     = smtp, 
                protocol = tcp
                ]
sendmail-whois[
    name     = Postfix, 
    dest     = fail2ban@%s, 
    sender   = www@%s
    ]
logpath  = /var/log/maillog
maxretry = 5

#############################################################
# Fail2Ban filter.d/postfix.local configuration file        #
#############################################################
#                   http://mediatemple.net/                 # 
#############################################################
[Definition]

failregex = reject: RCPT from (.*)\[\]: 554
reject: RCPT from (.*)\[\]: 550
reject: RCPT from (.*)\[\]: 450

ignoreregex = 

#############################################################
# Fail2Ban action.d/sendmail-whois.local configuration file #
#############################################################
#                   http://mediatemple.net/                 #
#############################################################
[Definition]

actionstart = echo -en "Subject: [Fail2Ban] : started
From: Fail2Ban <>
To: \n
Hi,\n
The jail has been started successfully.\n
Regards,\n
Fail2Ban" | /usr/sbin/sendmail -f  

actionstop = echo -en "Subject: [Fail2Ban] : stopped
From: Fail2Ban <>
To: \n
Hi,\n
The jail  has been stopped.\n
Regards,\n
Fail2Ban" | /usr/sbin/sendmail -f  

actioncheck = 

actionban = echo -en "Subject: [Fail2Ban] : banned 
From: Fail2Ban <>
To: \n
Hi,\n
The IP  has just been banned by Fail2Ban after
attempts against .\n\n
Here are more information about :\n
`/usr/bin/dig -x `\n
Regards,\n
Fail2Ban" | /usr/sbin/sendmail -f  

actionunban = 

[Init]
name = default
dest = root
sender = fail2ban

""" (domain, domain, domain, domain, domain, domain)

makejail = open('/etc/fail2ban/jail.conf', 'w')

makefile.truncate()

makejail.write(jail_conf)

makejail.close()


