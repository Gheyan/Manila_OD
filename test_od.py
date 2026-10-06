import pandas as pd
from manila_od import ODModel

STUDY = [f"Barangay {n}" for n in [649, 655, 657, 658, 659, 664, 666, 667, 668, 669, 670,
                                   676, 694, 696, 697, 699]]
OUTPUT_NAME = "study_area"                       # change per run

m = ODModel.load("od_bundle")
res = m.base()                                   # or m.run("my_scenario.json") for a hotspot test
od = pd.DataFrame(res.od, index=m.names, columns=m.names)

# A) only trips within the 16 barangays
inner = od.loc[STUDY, STUDY]
inner.round(0).astype(int).to_csv(f"{OUTPUT_NAME}_od_16x16.csv")

# B) the same plus one "Outside" zone for trips coming from / going to everywhere else
outside = [z for z in m.names if z not in STUDY]
mat = inner.copy()
mat["Outside"] = od.loc[STUDY, outside].sum(axis=1)                 # study -> outside
mat.loc["Outside"] = list(od.loc[outside, STUDY].sum(axis=0)) + [0] # outside -> study
mat.round(0).astype(int).to_csv(f"{OUTPUT_NAME}_od_17x17.csv")
print(mat.round(0).astype(int))