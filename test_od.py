import numpy as np
from manila_od import ODModel

# 1. Load the bundle
m = ODModel.load("od_bundle")
print("zones:", len(m.names))

# 2. Base OD matrix
base = m.base()
od = base.od                                   # 919 x 919 numpy array (trips/day)
print("base matrix shape:", od.shape, "| total trips/day:", round(od.sum()))
print("base summary:", base.summary())

# 3. Check it matches the notebook's matrix (should print True)
ref = np.load("od_bundle/od_matrix_base_reference.npy")
print("matches notebook:", np.allclose(od, ref))

# 4. Save the base matrix with a name of your choice
base.save("runs", name="base_test")            # -> runs/base_test/

# 5. Try a hotspot scenario
run = m.run({"attraction": {"Barangay 669": 0.5}})
cmp = run.compare()
print(cmp[cmp["zone"] == "Barangay 669"])      # arrivals before vs after
print("total trips unchanged:", np.isclose(run.od.sum(), od.sum()))
run.save("runs", name="test_hotspot")

# 6. A filtered pair list for your program
pairs = run.top_pairs(share=0.8, districts=["Port Area", "Ermita", "Malate"], selection_mode="within")
print(pairs.head())
print("pairs kept:", len(pairs))