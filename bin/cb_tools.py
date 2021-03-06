__author__ = '0xnix'

#
# Generates a dir for carbonblack feeds
# Can also stand up a SimpleHTTPServer to host the feeds
#
from os import chdir, listdir, mkdir, getcwd, path
import SimpleHTTPServer
import SocketServer
from re import sub, search
from json import dump, loads
from socket import gethostname

from feeds import FeedModules
from tools import regex
from cbdata import generate_feed

mods = FeedModules()

def gen_feed_list():
    #generates feed list from FeedModules()
    feed_list = []

    for f in dir(mods):
        if f.endswith('_update'):
            #strip _update suffix
            f = sub("_update", '', f)
            feed_list.append(f)

    return feed_list

def run_feed_server():
    #stands up the feed server, points to the CB/json_feeds dir
    print getcwd()
    chdir('../bin/cbdata/json_feeds/')
    port = 8000
    handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", port), handler)

    try:
        print '[+] CB Feed Server listening at http://%s:8000' % gethostname()
        httpd.serve_forever()
    except:
        print "[-] Server exited"

    return

def CB_gen():
    #cbfeed generator
    #
    feed_list = gen_feed_list()

    # Check for feed_meta dir
    if path.isdir("bin/cbdata/feed_meta/"):
        feedinfo = listdir("bin/cbdata/feed_meta/")
    else:
        try:
            mkdir('bin/cbdata/feed_meta')
            feedinfo = listdir("bin/cbdata/feed_meta/")
        except:
            print '[-] Error creating feed_meta directory, may need to adjust permissions'

    #Check for JSON_feed dir
    if path.isdir("bin/cbdata/json_feeds/"):
        pass
    else:
        try:
            mkdir('bin/cbdata/json_feeds')
        except:
            '[-] Error creating json_feeds directory, may need to adjust permissions'


    print '[*] Checking for existing feed metadata necessary to generate feeds...'
    for f in feed_list:
        #check for feed_info files correlating to feed_list
        json_path = 'bin/cbdata/json_feeds/%s' % f

        if f in feedinfo:
            print f + ': yes'

        else:
            print f + ': no'
            print '[-] No metadata found for %s' % f
            meta = get_feed_info(f)

        #generate json_feed for feed module
        meta_file = 'bin/cbdata/feed_meta/%s' % f
        meta = open(meta_file, 'r').read()
        try:
            loads(meta)    # checks that meta file is valid JSON string
        except:
            print '[-] %s is not a valid meta file.\nWould you like to create a valid metadata file?' % meta_file
            choice = raw_input('> (y/n) ')
            if choice == 'y':
                meta = get_feed_info(f)
            elif choice == 'n':
                '[*] Moving on then..'
            else:
                print '[!] Invalid choice. Better luck next time..'
                exit(0)

        #Creating JSON feed using scripts in cbfeeds/
        data = generate_feed.create_feed(meta)
        print data

        #Saving the data to file in json_feeds/
        try:
            print '[*] Dumping data to %s' % json_path
            dump_data = open(json_path, 'w+').write(data)
        except:
            print '[-] Could not dump report to %s' % json_path
            exit(0)

        next = raw_input('[*] Continue? (yes/no): ')
        if next == 'yes':
            pass
        elif next == 'no':
            print '[*] Exiting..'
            exit(0)
        else:
            'Nice try wise guy'

    return

def get_feed_info(f):
    #interactive prompt for gathering and storing feed info data
    feed_dict = {}
    feedpath = 'bin/cbdata/feed_meta/%s' % f    # Path for new feed metadata
    meta_file = open(feedpath, 'w+')
    name = f
    host = gethostname()
    ioc_file = 'intel/%s_ioc' % f
    feed_link = 'http://%s/%s' % (host, ioc_file)
    report_name = f + '_report'

    # Find URL in feeds.py
    try:
        feedfile = open('bin/feeds.py', 'r').readlines()
    except:
        print '[-] Could not open file'
        exit(0)

    count = 0
    stat = 0
    for line in feedfile:
        line = line.lower()
        fn = f.lower()
        if fn in line:
            loc = feedfile[count+1]
            searches = search(regex('URL'), loc)
            if searches == None:
                pass
            else:
                result = searches.group(0)
                stat=1
        else:
            count+=1

    if stat == 0:
        print '[-] Could not locate URL in feeds modules.. please provide it below:'
        provider_url = raw_input('> ')
    else:
        provider_url = result

    # Choose Display Name
    display_name = f
    print "[*] Is '%s' okay for Feed Display Name? ([RETURN], or specify new display name)" % display_name
    choice = raw_input('\r> ')
    if len(choice) == 0:
        pass
    else:
        display_name = choice

    # Choose Summary
    summary = f
    print "[*] Is '%s' okay for Feed Summary? ([RETURN], or specify summary)" % summary
    choice = raw_input('\r> ')
    if len(choice) == 0:
        pass
    else:
        summary = choice

    # Choose Tech Data
    tech_data = 'There are no requirements to share any data to receive this feed.'
    print "[*] Is '%s'\n okay for Tech Data? ([RETURN], or specify new display name)" % tech_data
    choice = raw_input('\r> ')
    if len(choice) == 0:
        pass
    else:
        tech_data = choice

    #Icon
    icon = ''
    iconic = raw_input('[*] Do you have an icon to upload? (yes or no)\n> ')
    if iconic == 'yes':
        icon = raw_input('[*] Please provide the full path to the image here:\n> ')
    elif iconic == 'no':
        pass
    else:
        '[-] Sorry, did not recognize that. You can add an icon later..'

    print '[*] Feed Info:'
    feed_meta = ['name', 'display_name', 'provider_url', 'summary', 'tech_data', 'icon', 'ioc_file', 'feed_link', 'report_name']
    for i in feed_meta:
        feed_dict[i] = locals()[i]

    try:
        json_data = dump(feed_dict, meta_file)
        print '[+] Successfully wrote metadata to %s' % feedpath
        meta_file.close()
    except:
        print '[-] Could not write JSON stream to file'

