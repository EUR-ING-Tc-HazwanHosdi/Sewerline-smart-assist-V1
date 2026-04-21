import streamlit as st
import math
import pandas as pd

# =========================
# APP CONFIG
# =========================
st.set_page_config(page_title="SewerLine Design Smart Assist Pro", layout="wide")

st.title("🚧 SewerLine Design Smart Assist Pro")
st.subheader("MSIG Vol. 3–Based Gravity Sewer Design System")

st.markdown("""
Engineering advisory tool for preliminary sewer pipe sizing based on PE and hydraulic constraints.
""")

# =========================
# INPUT SECTION
# =========================
st.sidebar.header("📥 Input Parameters")

PE = st.sidebar.number_input("Population Equivalent (PE)", min_value=1, value=1000)
q_per_capita = st.sidebar.number_input("Wastewater Generation (L/PE/day)", value=225)
slope = st.sidebar.number_input("Pipe Slope (S)", value=0.005, format="%.4f")

material = st.sidebar.selectbox("Pipe Material", [
    "uPVC",
    "HDPE",
    "Concrete",
    "Vitrified Clay"
])

# Manning n values
n_values = {
    "uPVC": 0.009,
    "HDPE": 0.010,
    "Concrete": 0.013,
    "Vitrified Clay": 0.011
}

n = n_values[material]

# =========================
# PIPE SIZES (ENGINEERING STANDARD - mm)
# =========================
pipe_sizes_mm = [150, 225, 300, 375, 450, 600]
pipe_sizes_m = [d / 1000 for d in pipe_sizes_mm]

# =========================
# FLOW CALCULATION
# =========================
q_m3_day = (PE * q_per_capita) / 1000
Qavg = q_m3_day / 86400

PF = 1 + (14 / (4 + math.sqrt(PE / 1000)))
Qpeak = Qavg * PF

# =========================
# MANNING FUNCTION
# =========================
def manning_Q(D, S, n):
    A = math.pi * D**2 / 4
    R = D / 4
    Q = (1/n) * A * (R ** (2/3)) * (S ** 0.5)
    V = Q / A
    return Q, V, R

# =========================
# DESIGN ENGINE
# =========================
results = []
selected = None

for D_mm, D in zip(pipe_sizes_mm, pipe_sizes_m):

    Qcap, V, R = manning_Q(D, slope, n)

    # MSIG checks
    if Qcap < Qpeak:
        status = "❌ Undersized"
    elif V < 0.6:
        status = "⚠ Low Velocity"
    elif V > 3.0:
        status = "⚠ High Velocity"
    else:
        status = "✔ Acceptable"

        if selected is None:
            selected = {
                "Diameter_mm": D_mm,
                "Qcap": Qcap,
                "V": V,
                "R": R
            }

    results.append({
        "Pipe Size (mm)": D_mm,
        "Capacity (m³/s)": round(Qcap, 5),
        "Velocity (m/s)": round(V, 3),
        "Status": status
    })

df = pd.DataFrame(results)

# =========================
# OUTPUT SECTION
# =========================
st.header("📊 Design Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Qavg (m³/s)", f"{Qavg:.6f}")
col2.metric("Qpeak (m³/s)", f"{Qpeak:.6f}")
col3.metric("Material", material)

# =========================
# PIPE SELECTION TABLE
# =========================
st.subheader("📏 Pipe Sizing Results (MSIG Check)")
st.dataframe(df, use_container_width=True)

# =========================
# RECOMMENDATION ENGINE
# =========================
st.subheader("🟢 Recommended Design")

if selected:

    st.success("✔ MSIG-Compliant Solution Found")

    st.write(f"**Recommended Pipe Size:** {selected['Diameter_mm']} mm")
    st.write(f"**Flow Capacity:** {selected['Qcap']:.5f} m³/s")
    st.write(f"**Velocity:** {selected['V']:.2f} m/s")
    st.write(f"**Slope Used:** {slope}")

    # Engineering interpretation
    if selected["V"] < 0.8:
        st.warning("⚠ Slightly low velocity – consider increasing slope for better self-cleansing")
    elif selected["V"] > 2.5:
        st.warning("⚠ High velocity – check erosion risk and pipe material suitability")

else:
    st.error("❌ No compliant pipe size found. Adjust slope or parameters.")

# =========================
# COMPLIANCE CHECK PANEL
# =========================
st.subheader("⚠ MSIG Compliance Check")

if selected:
    V = selected["V"]

    if 0.6 <= V <= 3.0:
        st.success("✔ Velocity within MSIG acceptable range (0.6–3.0 m/s)")
    else:
        st.error("❌ Velocity outside MSIG range")
