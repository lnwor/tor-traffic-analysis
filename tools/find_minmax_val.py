#!/bin/env python3

from pathlib import Path
import sys

def fetch_clients():
    c_tstamps = {}
    n = 0
    for p in Path('./pcaps').glob('*.log'):
        if "fileserver" in p.name:
            continue
        file = open("./pcaps/"+p.name, "r")
        lines = file.readlines()
        timestamps = []
        for line in lines:
            timestamps.append(float(line))
        if len(timestamps) == 0:
            print("Non è stato registrato nessun contenuto per " + p.name)
            continue
        index = p.name.find('-')
        c_tstamps[p.name[:index]] = timestamps
    return c_tstamps


def fetch_servers():
    s_tstamps = {}
    for p in Path('./pcaps').glob('*.log'):
        if "torclient" in p.name:
            continue
        file = open("./pcaps/"+p.name, "r")
        lines = file.readlines()
        timestamps = []
        for line in lines:
            timestamps.append(float(line))
        if len(timestamps) == 0:
            print("Non è stato registrato nessun contenuto per " + p.name)
            continue
        index = p.name.find('-')
        s_tstamps[p.name[:index]] = timestamps
    return s_tstamps

def main():
    clients_t = fetch_clients() # get client timestamps
    servers_t = fetch_servers() # get server timestamps
    diffs = []
    minn = 100000

    for i in range(100):
        s_times = servers_t["fileserver"+ str(i%10)]
        c_times = clients_t["torclient" + str(i)]
        tmp = 0
        for t in c_times:
            if (t - tmp) < minn:
                minn = (t - tmp)
            tmp = t
            for s_t in s_times:
                if (s_t - t) <= 0.3 and (s_t - t) >= 0.100:
                    diffs.append(s_t - t)
                    tmp = 0
                    break

    print("The maximum value is: "+str(max(diffs)))
    print("The minimum value is: "+str(min(diffs)))
    print("The average value is: "+str(sum(diffs)/len(diffs)))
    print("The minimum gap between each request is: "+str(minn))


if __name__ == '__main__':
    sys.exit(main())
