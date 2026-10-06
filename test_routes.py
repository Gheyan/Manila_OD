"""Run after re-exporting od_bundle with the updated notebook (Cell 15)."""
import numpy as np
from manila_od import ODModel

m = ODModel.load("od_bundle")
base = m.base()

# 1. Library base = notebook matrix (now with category weights + route factor). Should print True.
ref = np.load("od_bundle/od_matrix_base_reference.npy")
print("matches notebook:", np.allclose(base.od, ref))

# 2. routes.csv + neighbors.csv reproduce the notebook's vehicle counts. Should print 1.0 for both.
print(m.check_routes())

# 3. Routes per barangay in the study area
rpz = m.routes_per_zone()
print(rpz[rpz["district"].isin(["Port Area", "Ermita", "Malate"])].sort_values("routes", ascending=False).head(10))

# 4. Remove the line serving the most zones: its zones lose attraction and arrivals
table = m.route_table().sort_values("n_zones", ascending=False)
print(table[["route_id", "mode", "relations", "n_zones"]].head(10))
rid = table["route_id"].iloc[0]
zones_of_rid = table["zones"].iloc[0].split(", ")
rows = [m.row_of[z] for z in zones_of_rid]
run = m.run({"routes": {"remove": [rid]}})
print(f"removed {rid}: attraction down in its zones:", bool((run.A[rows] <= base.A[rows] + 1e-9).all()))
print("arrivals change in its zones:", round(run.compare().loc[rows, "change"].sum(), 1))
print("total trips unchanged:", np.isclose(run.od.sum(), base.od.sum()))

# 5. A new line + a hotspot, saved like any other run
run = m.run({"routes": {"add": {"New Ermita loop": {"zones": ["Barangay 669", "Barangay 670", "Barangay 676"],
                                                    "mode": "share_taxi"}}},
             "attraction": {"Barangay 669": 0.5}})
run.save("runs", name="test_new_route")

# 6. Facility category weights (new baseline, beta recalibrated)
r = m.run({"category_weights": {"mall": 2}})
print("mall x2: beta", round(r.beta, 4), "| recalibrated:", r.recalibrated)

# 7. Sensitivity of the route exponent (report this in the methods chapter)
for g in (0.0, 0.3, 0.6):
    r = m.run({"route_exponent": g})
    print(f"route_exponent {g}: beta {r.beta:.4f} | Manila trips staying in Manila "
          f"{r.summary()['manila_trips_staying_in_manila']:.3f}")
