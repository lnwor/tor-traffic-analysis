#!/usr/bin/env python3
from pathlib import Path
from bisect import bisect_left
import sys
from statistics import stdev

max_value = 20
min_value = 0.1

# recupero i timestamp di tutti i client
def fetch_clients():
    c_tstamps = {}
    for p in Path("./pcaps").glob("*.log"):
        if "torclient" not in p.name:
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
        if "fileserver" not in p.name:
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
    after = nlist[pos]
    return after


# calcolo lo scarto quadratico medio (deviazione standard) sulle differenze tra i timestamp di server e client
def calc_dev(client, server):
    tlist = []
    for t in client:
        tlist.append(abs(t - closest(server, t)))
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
    servername = ""
    fout = open("./matches.log", "w")

    for client in clients:
        candidates[client] = {}
        val_list = []
        if len(clients[client]) == 1:
            for server in servers:
                if is_candidate(clients[client], servers[server]):
                    candidates[client][server] = abs(
                        clients[client][0]
                        - closest(servers[server], clients[client][0] + 0.3)
                    )
            val_list = list(candidates[client].values())
            pos = val_list.index(min(val_list))
            servername = list(candidates[client].keys())[pos]
            fout.write(client + "|" + servername + "\n")
            print(client + " si è connesso con " + servername)
        else:
            for server in servers:
                if is_candidate(clients[client], servers[server]):
                    candidates[client][server] = calc_dev(
                        clients[client], servers[server]
                    )
                    val_list = list(candidates[client].values())
            print("Il client " + client + " ha i seguenti candidati:")
            for v in candidates[client].keys():
                print("La devstd per " + v + " è: " + str(candidates[client][v]))
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
        client, server = line.rstrip().split("|")
        for linepair in linespairs:
            client_pair, server_pair = linepair.rstrip().split("|")
            if client_pair == client[client.find("t", 1) + 1 : client.find("-")]:
                if (
                    int(client[client.find("t", 1) + 1 : client.find("-")]),
                    int(server[server.find("r", 8) + 1 : server.find("-")]),
                ) == (int(client_pair), int(server_pair)):
                    count += 1
                    break
                else:
                    print(
                        "Il client "
                        + client
                        + " è stato abbinato con il server "
                        + server
                        + " invece che con fileserver"
                        + server_pair
                    )
    if count >= len(clients) * 0.8:
        print(
            "\033[32m"
            + str(count)
            + " dei "
            + str(len(clients))
            + " client sono stati abbinari correttamente"
            + "\033[m",
            file=sys.stderr,
        )
    elif count >= len(clients) * 0.5:
        print(
            "\033[33m"
            + str(count)
            + " dei "
            + str(len(clients))
            + " client sono stati abbinari correttamente"
            + "\033[m",
            file=sys.stderr,
        )
    else:
        print(
            "\033[31m"
            + str(count)
            + " dei "
            + str(len(clients))
            + " client sono stati abbinari correttamente"
            + "\033[m",
            file=sys.stderr,
        )
    pairs.close()
    fout.close()


if __name__ == "__main__":
    sys.exit(main())
