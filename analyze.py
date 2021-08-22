#!/usr/bin/env python3
from pathlib import Path
from bisect import bisect_left
import sys
from statistics import stdev

max_value = 30
min_value = (
    -0.1
)  # negativo perchè la versione di shadow in utilizzo in rari casi produce pcaps con timestamps anticipati
avg_diff = 0

# recupero i timestamp di tutti i client
def fetch_clients():
    c_tstamps = {}
    for p in Path("./pcaps").glob("*.log"):
        if "fileserver" in p.name:
            continue
        file = open("./pcaps/" + p.name, "r")
        lines = file.readlines()
        timestamps = []
        for line in lines:
            timestamps.append(float(line))
        if len(timestamps) == 0:
            print("Non è stato registrato nessun contenuto per " + p.name)
            continue
        c_tstamps[p.name] = timestamps
    return c_tstamps


# recupero i timestamp di tutti i server
def fetch_servers():
    s_tstamps = {}
    for p in Path("./pcaps").glob("*.log"):
        if "torclient" in p.name:
            continue
        file = open("./pcaps/" + p.name, "r")
        lines = file.readlines()
        timestamps = []
        for line in lines:
            timestamps.append(float(line))
        if len(timestamps) == 0:
            print("Non è stato registrato nessun contenuto per " + p.name)
            continue
        s_tstamps[p.name] = timestamps
    return s_tstamps


# trovo il numero più vicino a n della lista nlist
def closest(nlist, n):
    pos = bisect_left(nlist, n)
    if pos == 0:
        return nlist[0]
    if pos == len(nlist):
        return nlist[-1]
    before = nlist[pos - 1]
    after = nlist[pos]
    if n - before <= after - n and before >= (n - avg_diff + min_value):
        return before
    else:
        return after


# calcolo lo scarto quadratico medio (deviazione standard) sulle differenze tra i timestamp di server e client
def calc_dev(client, server):
    tlist = []
    for t in client:
        tlist.append(abs(t + avg_diff - closest(server, t + avg_diff)))
    return stdev(tlist)


def is_candidate(client, server):
    found = False
    for t in client:
        found = False
        for s_t in server:
            if (s_t - t) >= min_value and (s_t - t) <= max_value:
                found = True
        if not found:
            return False
    return True


def main():
    clients = fetch_clients()
    servers = fetch_servers()
    candidates = {}
    diffs = []  # usarlo per ottenere una media ed aggiornare lo script alla nuova media
    servername = ""
    fout = open("./matches.log", "w")

    for client in clients:
        candidates[client] = {}
        val_list = []
        for server in servers:
            if is_candidate(clients[client], servers[server]):
                candidates[client][server] = calc_dev(clients[client], servers[server])
                val_list = list(candidates[client].values())
        print("For the client " + client)
        for v in candidates[client].keys():
            print(v, candidates[client][v])
        if len(val_list) == 0:
            print("Il client " + client + " non ha candidati")
        else:
            pos = val_list.index(min(val_list))
            servername = list(candidates[client].keys())[pos]

        if servername != False:
            fout.write(client + "|" + servername + "\n")
            print(client + " si è connesso con " + servername)
    fout.close()
    pairs = open("./pairs.log")
    fout = open("./matches.log")
    linesout = fout.readlines()
    linespairs = pairs.readlines()
    count = 0
    for line in linesout:
        client, server = line.split("|")
        for linepair in linespairs:
            client_pair, server_pair = linepair.split("|")
            if client_pair == client[client.find("t", 1) + 1 : client.find("-")]:
                if (
                    int(client[client.find("t", 1) + 1 : client.find("-")]),
                    int(server[server.find("r", 8) + 1 : server.find("-")]),
                ) == (int(client_pair), int(server_pair)):
                    count += 1
                    break
    if count >= len(clients) * 0.8:
        print(
            "\033[32m"
            + str(count)
            + " out of "
            + str(len(clients))
            + " clients matched correctly"
            + "\033[m"
        )
    elif count >= len(clients) * 0.5:
        print(
            "\033[33m"
            + str(count)
            + " out of "
            + str(len(clients))
            + " clients matched correctly"
            + "\033[m"
        )
    else:
        print(
            "\033[31m"
            + str(count)
            + " out of "
            + str(len(clients))
            + " clients matched correctly"
            + "\033[m"
        )
    pairs.close()
    fout.close()


if __name__ == "__main__":
    sys.exit(main())
