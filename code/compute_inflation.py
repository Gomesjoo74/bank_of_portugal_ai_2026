import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- Load ---
df = pd.read_csv(
    "data/raw/cpi.csv",
    comment="#",
    parse_dates=["observation_date"],
)
df = df.rename(columns={"observation_date": "date", "CPIAUCSL": "cpi"})
df = df.dropna(subset=["cpi"]).sort_values("date").reset_index(drop=True)

# --- Compute YoY inflation ---
df["inflation"] = df["cpi"].pct_change(12) * 100
df = df.dropna(subset=["inflation"])

# --- Save ---
df[["date", "inflation"]].to_csv("data/processed/inflation.csv", index=False)

# --- Plot ---
crisis_start = pd.Timestamp("2019-01-01")
crisis_end   = df["date"].max()

fig, (ax_main, ax_zoom) = plt.subplots(
    1, 2,
    figsize=(14, 5),
    gridspec_kw={"width_ratios": [3, 1.4]},
)

# Shared style
ACCENT = "#cc785c"
ZERO   = "#888888"

for ax in (ax_main, ax_zoom):
    ax.axhline(0, color=ZERO, linewidth=0.8, linestyle="--")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="both", labelsize=9)

# — Main panel —
ax_main.plot(df["date"], df["inflation"], color=ACCENT, linewidth=1.2)
ax_main.set_title("US CPI — Year-over-year inflation (%)", fontsize=11, pad=10)
ax_main.set_ylabel("%", fontsize=9)
ax_main.xaxis.set_major_locator(mdates.YearLocator(10))
ax_main.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax_main.set_xlim(df["date"].min(), df["date"].max())

# Shade crisis window on main panel
ax_main.axvspan(crisis_start, crisis_end, color=ACCENT, alpha=0.08)

# — Zoom panel —
mask = (df["date"] >= crisis_start) & (df["date"] <= crisis_end)
dz   = df[mask]

ax_zoom.plot(dz["date"], dz["inflation"], color=ACCENT, linewidth=1.4)
peak = dz.loc[dz["inflation"].idxmax()]
ax_zoom.annotate(
    f"Peak\n{peak['inflation']:.1f}%",
    xy=(peak["date"], peak["inflation"]),
    xytext=(10, -28),
    textcoords="offset points",
    fontsize=8,
    color=ACCENT,
    arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8),
)
ax_zoom.set_title("Zoom: 2019 – present", fontsize=10, pad=10)
ax_zoom.xaxis.set_major_locator(mdates.YearLocator(1))
ax_zoom.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax_zoom.set_xlim(crisis_start, crisis_end)
plt.setp(ax_zoom.xaxis.get_majorticklabels(), rotation=45, ha="right")

fig.tight_layout(pad=2.0)
fig.savefig("slides/assets/inflation.png", dpi=150, bbox_inches="tight")
print("Saved: data/processed/inflation.csv")
print("Saved: slides/assets/inflation.png")
