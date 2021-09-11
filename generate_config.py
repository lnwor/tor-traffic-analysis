#!/bin/env python3
import yaml, sys, argparse, random


def main():
    generate_shadow()


def yaml_str_presenter(dumper, data):
    """
    Convert a string YAML representation to be more human friendly
    """
    if len(data.splitlines()) > 1:  # check for multiline string
        # note: pyyaml will use quoted style instead of the literal block style if the string
        # contains trailing whitespace: https://github.com/yaml/pyyaml/issues/121
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def yaml_dict_presenter(dumper, data):
    """
    Allow YAML to conserve the order
    """
    value = []
    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)
        value.append((node_key, node_value))
    return yaml.MappingNode(u"tag:yaml.org,2002:map", value)


def generate_shadow():
    shadow = {}
    inline = 'graph [\n  directed 0\n  node [\n    id 0\n    ip_address "0.0.0.0"\n    country_code "US"\n    bandwidth_down "1 Gbit"\n    bandwidth_up "1 Gbit"\n  ]\n  edge [\n    source 0\n    target 0\n    latency "50 ms"\n    jitter "0 ms"\n    packet_loss 0.0\n  ]\n]\n'
    shadow["general"] = {"stop_time": "30 min", "seed": 1835250621, "parallelism": 2}
    shadow["network"] = {}
    # shadow["network"]["use_shortest_path"] = False
    shadow["network"]["graph"] = {}
    shadow["network"]["graph"]["type"] = "gml"
    shadow["network"]["graph"]["inline"] = inline
    shadow["host_defaults"] = {}
    shadow["host_defaults"]["pcap_directory"] = "./pcaps"
    shadow["hosts"] = {}

    parser = argparse.ArgumentParser(description="Generate config file.")
    parser.add_argument(
        "clients", metavar="<clients>", type=int, nargs=1, help="Number of clients"
    )
    parser.add_argument(
        "servers", metavar="<servers>", type=int, nargs=1, help="Number of servers"
    )

    args = parser.parse_args()

    for i in range(args.servers[0]):
        shadow["hosts"]["fileserver" + str(i)] = {}
        shadow["hosts"]["fileserver" + str(i)]["processes"] = [
            {
                "path": "~/.local/bin/tgen",
                "args": "../../../conf/tgen.server.graphml.xml",
                "start_time": 1,
            }
        ]
    shadow["hosts"]["4uthority"] = {}
    shadow["hosts"]["4uthority"]["options"] = {"ip_address_hint": "100.0.0.1"}
    shadow["hosts"]["4uthority"]["processes"] = [
        {
            "path": "~/.local/bin/tor",
            "args": "--Address 4uthority --Nickname 4uthority --defaults-torrc torrc-defaults -f torrc",
            "start_time": 1,
        }
    ]
    shadow["hosts"]["exit1"] = {}
    shadow["hosts"]["exit1"]["processes"] = [
        {
            "path": "~/.local/bin/tor",
            "args": "--Address exit1 --Nickname exit1 --defaults-torrc torrc-defaults -f torrc",
            "start_time": 60,
        }
    ]
    shadow["hosts"]["exit2"] = {}
    shadow["hosts"]["exit2"]["processes"] = [
        {
            "path": "~/.local/bin/tor",
            "args": "--Address exit2 --Nickname exit2 --defaults-torrc torrc-defaults -f torrc",
            "start_time": 60,
        }
    ]
    shadow["hosts"]["relay1"] = {}
    shadow["hosts"]["relay1"]["processes"] = [
        {
            "path": "~/.local/bin/tor",
            "args": "--Address relay1 --Nickname relay1 --defaults-torrc torrc-defaults -f torrc",
            "start_time": 60,
        }
    ]
    shadow["hosts"]["relay2"] = {}
    shadow["hosts"]["relay2"]["processes"] = [
        {
            "path": "~/.local/bin/tor",
            "args": "--Address relay2 --Nickname relay2 --defaults-torrc torrc-defaults -f torrc",
            "start_time": 60,
        }
    ]
    pout = open("pairs.log", "w")
    for i in range(args.clients[0]):
        shadow["hosts"]["torclient" + str(i)] = {}
        shadow["hosts"]["torclient" + str(i)]["processes"] = []
        for _ in range(2):
            shadow["hosts"]["torclient" + str(i)]["processes"].append(None)
        shadow["hosts"]["torclient" + str(i)]["processes"][0] = {}
        shadow["hosts"]["torclient" + str(i)]["processes"][0][
            "path"
        ] = "~/.local/bin/tor"
        shadow["hosts"]["torclient" + str(i)]["processes"][0]["args"] = (
            "--Address torclient"
            + str(i)
            + " --Nickname torclient"
            + str(i)
            + " --defaults-torrc torrc-defaults -f torrc"
        )
        shadow["hosts"]["torclient" + str(i)]["processes"][0]["start_time"] = 900
        shadow["hosts"]["torclient" + str(i)]["processes"][1] = {}
        shadow["hosts"]["torclient" + str(i)]["processes"][1][
            "path"
        ] = "~/.local/bin/tgen"
        shadow["hosts"]["torclient" + str(i)]["processes"][1]["args"] = (
            "../../../conf/tgen.torclient" + str(i) + ".graphml.xml"
        )
        shadow["hosts"]["torclient" + str(i)]["processes"][1]["start_time"] = 1200

        pair = random.randint(0, args.servers[0] - 1)

        pout.write(str(i) + "|" + str(pair) + "\n")

        with open("./conf/tgen.torclient.graphml.xml", "r") as f:
            fout = open("./conf/tgen.torclient" + str(i) + ".graphml.xml", "w")
            lines = f.readlines()
            for line in lines:
                if "fileserver" in line:
                    fout.write(
                        '      <data key="d5">fileserver' + str(pair) + ":80</data>\n"
                    )
                # elif "start_time" in line:
                #     fout.write('      <data key="d0">'+str(random.randint(1,30))+'</data>\n')
                else:
                    fout.write(line)
            fout.close()

    pout.close()
    yaml.add_representer(str, yaml_str_presenter)
    yaml.add_representer(dict, yaml_dict_presenter)
    with open("shadow.yaml", "w") as f:
        yaml.dump(shadow, f, default_flow_style=False)


if __name__ == "__main__":
    sys.exit(main())
