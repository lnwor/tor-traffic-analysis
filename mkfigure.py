import seaborn as sns
import numpy as np
import pandas as pd

pdata = pd.read_csv(r"./test.csv")

ax = sns.lineplot(x="Latenza", y="vals", data=pdata)
ax.set(xlabel="Latenza", ylabel="% di associazioni corrette")
ax.set_yticks(np.arange(0, 1, 0.1))
ax.figure.savefig("latenze.png")
