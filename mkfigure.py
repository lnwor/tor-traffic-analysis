import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.ticker as mtick

pdata = pd.read_csv(r"./data.csv")

ax = sns.lineplot(x="n", y="vals", data=pdata)
ax.set(xlabel="Numero di client", ylabel="Percentuale di associazioni corrette")
ax.set_yticks(np.arange(0, 1, 0.1))
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.figure.savefig("data.png")
