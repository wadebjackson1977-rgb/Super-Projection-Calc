
import streamlit as st
import pandas as pd
import numpy as np

# Page Config
st.set_page_config(page_title="Superannuation Calculator", layout="wide")

st.title("Superannuation Projection Calculator")
st.markdown("Use this calculator to project your super balance based on historical performance and current tax rules.")

# Sidebar for Inputs
st.sidebar.header("Input Assumptions")

# Changed starting balance default from 780,000 to 100,000
starting_balance = st.sidebar.number_input("Starting Balance ($)", value=100000, step=1000)
gross_contribution = st.sidebar.number_input("Gross Annual Contribution ($)", value=25000, step=500)
contribution_growth = st.sidebar.slider("Annual Contribution Growth (%)", 0.0, 10.0, 3.0) / 100
cust_return = st.sidebar.slider("Custom Return Rate (%)", 0.0, 20.0, 10.07) / 100
avg_return = st.sidebar.slider("Industry Average Return (%)", 0.0, 20.0, 8.0) / 100
inflation_rate = st.sidebar.slider("Annual Inflation Rate (%)", 0.0, 5.0, 3.0) / 100
time_horizon = st.sidebar.slider("Time Horizon (Years)", 5, 30, 10)

# Calculations
data = []
current_cust = starting_balance
current_avg = starting_balance
cont = gross_contribution

for yr in range(1, time_horizon + 1):
    net_cont = cont * 0.85  # 15% tax
    
    # Custom
    current_cust = (current_cust + net_cont) * (1 + cust_return)
    cust_real = current_cust / ((1 + inflation_rate) ** yr)
    
    # Average
    current_avg = (current_avg + net_cont) * (1 + avg_return)
    avg_real = current_avg / ((1 + inflation_rate) ** yr)
    
    data.append({
        "Year": yr,
        "Custom (Nominal)": current_cust,
        "Custom (Real)": cust_real,
        "Average (Nominal)": current_avg,
        "Average (Real)": avg_real
    })
    
    cont *= (1 + contribution_growth)

df = pd.DataFrame(data)

# Visualizations
st.subheader("Projection Chart")
st.line_chart(df.set_index("Year"))

st.subheader("Summary Table")
st.dataframe(df.style.format("${:,.0f}"))

st.markdown("---")
st.subheader("Considerations")
st.write("- **Contributions Tax:** Automatically assumes 15% entry tax.")
st.write("- **Inflation:** Real values are discounted by your inflation setting.")
st.write("- **Div 296:** Note that balances exceeding $3M are subject to extra tax.")
