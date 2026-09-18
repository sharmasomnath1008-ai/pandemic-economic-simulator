import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Pandemic Economic Impact Simulator",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CUSTOM DESIGN
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #0b1020;
}

.hero {
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(135deg, #111936, #211650);
    border: 1px solid #3949ab;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 36px;
    margin-bottom: 8px;
}

.hero p {
    color: #cbd5ff;
    font-size: 17px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">

<h1>📊 Pandemic Economic Impact Simulator</h1>

<p>
Design and Analysis of Simulation Framework for Pandemic
Economic Impact Modelling
</p>

</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Simulation Controls")

months = st.sidebar.slider(
    "Simulation Period (Months)",
    6,
    36,
    18
)

intervention = st.sidebar.slider(
    "Intervention Intensity (%)",
    0,
    100,
    60
)

infection = st.sidebar.slider(
    "Peak Infection Pressure (%)",
    5,
    80,
    35
)

recovery = st.sidebar.slider(
    "Recovery Strength (%)",
    10,
    100,
    70
)

baseline_gdp = st.sidebar.number_input(
    "Baseline GDP Index",
    min_value=50.0,
    max_value=200.0,
    value=100.0
)

employment_sensitivity = st.sidebar.slider(
    "Employment Sensitivity",
    0.1,
    1.5,
    0.7,
    0.1
)

run = st.sidebar.button(
    "▶ Run Simulation",
    use_container_width=True
)

# =========================================================
# TIME AXIS
# =========================================================

time = np.arange(months)

# =========================================================
# PANDEMIC MODEL
# =========================================================

peak_month = max(
    1,
    int(months * 0.30)
)

width = max(
    1,
    months * 0.18
)

infection_curve = (
    infection
    *
    np.exp(
        -(
            (time - peak_month) ** 2
        )
        /
        (2 * width ** 2)
    )
)

infection_curve = np.clip(
    infection_curve,
    0,
    100
)

# =========================================================
# RECOVERY MODEL
# =========================================================

recovery_curve = (
    np.maximum(
        0,
        time - peak_month
    )
    /
    max(
        1,
        months - peak_month
    )
)

recovery_curve = np.minimum(
    recovery_curve,
    1
)

# =========================================================
# ECONOMIC SHOCK
# =========================================================

economic_shock = (
    0.35 * infection_curve
    +
    0.45 * intervention
)

economic_shock *= (
    1 - recovery / 180
)

economic_shock *= (
    1 - 0.55 * recovery_curve
)

# =========================================================
# GDP MODEL
# =========================================================

gdp = (
    baseline_gdp
    *
    (
        1 -
        economic_shock / 100
    )
)

# =========================================================
# EMPLOYMENT MODEL
# =========================================================

employment = (
    100
    -
    employment_sensitivity
    *
    economic_shock
)

# =========================================================
# DEMAND MODEL
# =========================================================

demand = (
    100
    -
    0.80
    *
    economic_shock
)

# =========================================================
# RECOVERY INDEX
# =========================================================

recovery_index = np.minimum(
    100,
    100
    -
    economic_shock
    +
    20 * recovery_curve
)

# =========================================================
# DATAFRAME
# =========================================================

data = pd.DataFrame({

    "Month":
        time + 1,

    "Infection Pressure (%)":
        infection_curve,

    "GDP Index":
        gdp,

    "Employment Index":
        employment,

    "Demand Index":
        demand,

    "Recovery Index":
        recovery_index
})

# =========================================================
# CALCULATE KPIs
# =========================================================

peak_gdp_loss = (
    (
        baseline_gdp
        -
        gdp.min()
    )
    /
    baseline_gdp
    *
    100
)

peak_employment_loss = (
    100 -
    employment.min()
)

peak_infection = (
    infection_curve.max()
)

# =========================================================
# RECOVERY MONTH
# =========================================================

recovered = (
    data["GDP Index"]
    >=
    baseline_gdp * 0.95
)

if recovered.any():

    recovery_month = int(
        data.loc[
            recovered,
            "Month"
        ].iloc[0]
    )

else:

    recovery_month = None

# =========================================================
# DASHBOARD KPIs
# =========================================================

st.subheader("📌 Simulation Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Peak GDP Impact",
        f"-{peak_gdp_loss:.1f}%"
    )

with col2:

    st.metric(
        "Employment Impact",
        f"-{peak_employment_loss:.1f}%"
    )

with col3:

    st.metric(
        "Peak Infection",
        f"{peak_infection:.1f}%"
    )

with col4:

    if recovery_month:

        st.metric(
            "95% GDP Recovery",
            f"Month {recovery_month}"
        )

    else:

        st.metric(
            "95% GDP Recovery",
            "Not Reached"
        )

# =========================================================
# ECONOMIC GRAPH
# =========================================================

st.subheader("📈 Economic Impact Analysis")

left, right = st.columns(2)

with left:

    fig1 = px.line(
        data,
        x="Month",
        y=[
            "GDP Index",
            "Employment Index",
            "Demand Index"
        ],
        markers=True,
        title="Economic Indicators Over Time"
    )

    fig1.update_layout(
        template="plotly_dark",
        legend_title_text=""
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

# =========================================================
# PANDEMIC GRAPH
# =========================================================

with right:

    fig2 = px.line(
        data,
        x="Month",
        y=[
            "Infection Pressure (%)",
            "Recovery Index"
        ],
        markers=True,
        title="Pandemic Pressure & Recovery"
    )

    fig2.update_layout(
        template="plotly_dark",
        legend_title_text=""
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =========================================================
# SCENARIO ANALYSIS
# =========================================================

st.subheader("🔬 Policy Scenario Comparison")

scenarios = [
    ("No Intervention", 0),
    ("Partial Intervention", 50),
    ("Strict Intervention", 90)
]

scenario_results = []

for name, intervention_level in scenarios:

    scenario_shock = (
        0.35 * infection_curve
        +
        0.45 * intervention_level
    )

    scenario_shock *= (
        1 - recovery / 180
    )

    scenario_shock *= (
        1 - 0.55 * recovery_curve
    )

    scenario_gdp = (
        baseline_gdp
        *
        (
            1 -
            scenario_shock / 100
        )
    )

    gdp_loss = (
        (
            baseline_gdp
            -
            scenario_gdp.min()
        )
        /
        baseline_gdp
        *
        100
    )

    scenario_results.append({

        "Scenario":
            name,

        "Intervention (%)":
            intervention_level,

        "Minimum GDP Index":
            round(
                float(
                    scenario_gdp.min()
                ),
                2
            ),

        "Peak GDP Loss (%)":
            round(
                float(gdp_loss),
                2
            )
    })

scenario_df = pd.DataFrame(
    scenario_results
)

# =========================================================
# SCENARIO TABLE
# =========================================================

st.dataframe(
    scenario_df,
    use_container_width=True,
    hide_index=True
)

# =========================================================
# SCENARIO GRAPH
# =========================================================

fig3 = px.bar(
    scenario_df,
    x="Scenario",
    y="Peak GDP Loss (%)",
    text_auto=".2f",
    title="Peak GDP Loss by Scenario"
)

fig3.update_layout(
    template="plotly_dark"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =========================================================
# ASSUMPTIONS
# =========================================================

st.subheader("📋 Model Assumptions")

st.markdown("""
### Pandemic Model

- Infection pressure follows a smooth rise-and-fall curve.
- Peak infection pressure is controlled by the user.
- Simulation duration can be changed.

### Economic Model

- GDP is represented using a normalized index.
- Employment is represented using an index.
- Demand is represented using an index.
- Pandemic pressure produces an economic shock.

### Recovery Model

- Recovery strength controls the recovery process.
- GDP recovery is measured against the baseline GDP.

### Scenario Analysis

The system compares:

- No Intervention
- Partial Intervention
- Strict Intervention

> **Note:** This is an educational simulation framework.
> Results depend on the selected assumptions and are not
> real-world economic forecasts.
""")

# =========================================================
# DOWNLOAD CSV
# =========================================================

st.subheader("📥 Export Results")

csv_file = data.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇ Download Simulation Results",
    data=csv_file,
    file_name="pandemic_economic_simulation.csv",
    mime="text/csv"
)

# =========================================================
# SUCCESS MESSAGE
# =========================================================

if run:

    st.success(
        "✅ Simulation completed successfully!"
    )

    st.info(
        "Change the parameters from the sidebar "
        "to run another simulation."
    )