# import requests
import sys
import platform
import os
import subprocess
from subprocess import check_output
import re
import json
import urllib
import urllib2
import getopt
import iwlist # Cred: https://github.com/iancoleman/python-iwlist

key = ""

def banner():
    print """
       :::::::::::''  ''::'      '::::::  `:::::::::::::'.:::::::::::::::
       :::::::::' :. :  :         ::::::  :::::::::::.:::':::::::::::::::
       ::::::::::  :   :::.       :::::::::::::..::::'     :::: : :::::::
       ::::::::    :':  "::'     '"::::::::::::: :'           '' ':::::::
       :'        : '   :  ::    .::::::::'    '                        .:
       :               :  .:: .::. ::::'                              :::
       :. .,.        :::  ':::::::::::.: '                      .:...::::
       :::::::.      '     .::::::: '''                         :: :::::.
       ::::::::            ':::::::::  '',            '    '   .:::::::::
       ::::::::.        :::::::::::: '':,:   '    :         ''' :::::::::
       ::::::::::      ::::::::::::'                        :::::::::::::
       : .::::::::.   .:''::::::::    '         ::   :   '::.::::::::::::
       :::::::::::::::. '  '::::::.  '  '     :::::.:.:.:.:.:::::::::::::
       :::::::::::::::: :     ':::::::::   ' ,:::::::::: : :.:'::::::::::
       ::::::::::::::::: '     :::::::::   . :'::::::::::::::' ':::::::::
       ::::::::::::::::::''   :::::::::: :' : ,:::::::::::'      ':::::::
       :::::::::::::::::'   .::::::::::::  ::::::::::::::::       :::::::
       :::::::::::::::::. .::::::::::::::::::::::::::::::::::::.'::::::::
       :::::::::::::::::' :::::::::::::::::::::::::::::::::::::::::::::::
       ::::::::::::::::::.:::::::::::::::::::::::::::::::::::::::::::::::
                                WHEREAMI??
    """
#
def usage():
    print "WHEREAMI"
    print
    print "Usage: whereami.py -k <GOOGLE_API_KEY>"
    print "-k --key         - google api key"
    print "-i              - wireless interface (LINUX ONLY)"
    print "-h              - prints this usage prompt"
    print
    print 'Linux Example: whereami.py -k XXXXXXXX -i wlan0'
    print "Run this on Python 2, not formatted for 3 yet"
    sys.exit()

def mac_ap():
    ## OSX
    cmd = ["/System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport", "-s"]
    aps = check_output(cmd)
    reg = "(?:[A-Fa-f0-9]{2}[:-]){5}(?:[A-Fa-f0-9]{2})"
    ap_array = []
    post_data = {}
    for line in aps.split('\n'):
        data = {}
        if len(line):
            ap = line.split()
            match = re.search(reg, ap[1])
            if match:
                data["macAddress"]= ap[1].upper()
                data["signalStrength"] = int(ap[2])
                ap_array.append(data)

    # print ap_array
    post_data["wifiAccessPoints"] = ap_array
    print "Access Points Discovered: %i" % len(ap_array)
    send_request(post_data)

def linux_ap(interface):
    path = "/sys/class/net/%s/wireless" % interface
    if not os.path.exists(path):
      print "Error: It appears that %s is not a wireless interface" % interface
      sys.exit()

    ap_array = []
    post_data = {}
    content = iwlist.scan(interface=interface)
    cells = iwlist.parse(content)
    for cell in cells:
      data = {}
      data["macAddress"] = cell["mac"]
      data["signalStrength"] = cell["db"]
      ap_array.append(data)

    post_data["wifiAccessPoints"] = ap_array
    print "Access Points Discovered: %i" % len(ap_array)
    send_request(post_data)




def send_request(data):
    global key
    json_data = json.dumps(data)
    url = "https://www.googleapis.com/geolocation/v1/geolocate?key=%s" % key
    headers = {"Content-Type": "application/json"}

    req = urllib2.Request(url, json_data, headers)
    res = urllib2.urlopen(req)
    response = res.read()
    res = json.loads(response)
    lat, long, acc = res["location"]["lat"] , res["location"]["lng"], res["accuracy"]
    print "\tLatitude: %s, Longitude: %s, Accuracy: %s" % (lat, long, acc)

def main():
    global key
    interface = ""

    if len(sys.argv) == 1:
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hk:i:", ["help"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-k"):
            key = a
        elif o in ("-i"):
            interface = a
        else:
            assert False, "Unhandled Option"

    if platform.system() == 'Darwin':
        banner()
        mac_ap()
    elif platform.system() == "Linux":
        banner()
        if not interface:
          print "Error: Interface is required on Linux Systems"
          sys.exit()
        else:
          linux_ap(interface)




main()
