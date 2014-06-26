__author__ = 'pendrak0n'
#
# When called, will search through Intel directory for each
# indicator in provided CSV or New-line formatted file.
#

import tools
import sys
import re
import os
from time import sleep

def search_intel(ioc):
    os.chdir('../')
    patt = tools.regex('ip')

    if ioc[-3:] == 'csv':
        print '[*] Pulling indicators as CSV values'
    else:
        print '[*] Assuming new-line formatted file'
    try:
        f = open(ioc, 'r').readlines()
    except:
        sys.stderr.write("[!] Cannot locate file: %s.\
        Please provide the full path." % ioc)
        exit(0)

    ioc_list = []
    for line in f:
        for match in patt.findall(line):
            ioc_list.append(match)

    sleep(2)
    os.chdir('intel')
    dir = os.listdir('.')

    total = float(len(ioc_list))
    print '[*] Found %d indicators in %s' % (total, ioc)
    frac = 1.0/total
    prog = 0.0
    matches = 0

    matched = open('../matches.txt', 'w+')

    for item in ioc_list:
        for i in dir:
            f2 = open(i, 'r')
            contents = f2.readlines()
            for line in contents:
                if item in line:
                    info = item + ' --> ' + i + '\n'
                    matched.write(info)
                    matches += 1
            else:
                pass
            f2.close()

        prog += frac
        update_progress(prog)

    print '[+] Search complete.'
    print '[+] %d matches found and stored in matches.txt' % matches


def single_search(ioc):
    os.chdir('../intel')
    dirs = os.listdir('.')

    if len(dirs) == 0:
        sys.stderr.write("[!] Cannot complete search, no files in intel directory. Exiting..\n")
        sys.exit(0)

    total = float(len(dirs))
    print 'there are %d files in Intel dir' % total

    frac = 1.0/total
    prog = 0.0
    matched = open('../matches.txt', 'w+')
    matches = 0

    for i_file in dirs:
        f2 = open(i_file, 'r')
        contents = f2.readlines()
        for line in contents:
            if ioc in line:
                info = line.rstrip('\n') + ' --> ' + i_file + '\n'
                matched.write(info)
                matches += 1
            else:
                pass
            f2.close()

        prog += frac
        update_progress(prog)


    print '[+] Search complete.'
    print '[+] %d matches found and stored in matches.txt' % matches


def update_progress(progress):
    barLength = 20  # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= .999:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rProgress: [{0}] {1}% {2}".format("#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

