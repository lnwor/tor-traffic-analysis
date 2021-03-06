import matplotlib.pyplot as plt
import argparse
import seaborn as sns
import numpy as np
import matplotlib.ticker as mtick

parser = argparse.ArgumentParser(description="Generate config file.")
parser.add_argument(
    "filename", metavar="<filename>", type=str, nargs=1, help="Filename to plot"
)

args = parser.parse_args()

file = open(args.filename[0], "r")
lines = file.readlines()

x = []
y = []
for line in lines:
    tmp = line.split(",")
    x.append(int(tmp[0]))
    y.append(int(tmp[1]) / int(tmp[0]))

ax = sns.lineplot(x=x, y=y, ci=95)
ax.set(xlabel="Numero di client", ylabel="Percentuale di associazioni corrette")
ax.set_yticks(np.arange(0, 1, 0.1))
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.figure.savefig(args.filename[0] + ".png")
