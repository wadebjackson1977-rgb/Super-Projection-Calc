import streamlit as st
import pandas as pd

st.set_page_config(page_title="Advanced Super Calculator", layout="wide")

st.title("Advanced Superannuation Projection Calculator")
st.markdown("Project your super balance factoring in real-world costs and timing.")

# Sidebar Controls
st.sidebar.header("Standard Assumptions")
starting_balance = st.sidebar.number_input("Starting Balance ($)", value=100000, step=1000)
gross_contribution = st.sidebar.number_input("Gross Annual Contribution ($)", value=25000, step=500)
contribution_growth = st.sidebar.slider("Annual Contribution Growth (%)", 0.0, 10.0, 3.0) / 100
time_horizon = st.sidebar.slider("Time Horizon (Years)", 5, 30, 10)

st.sidebar.markdown("---")
st.sidebar.subheader("Advanced Settings")
admin_fee = st.sidebar.number_input("Annual Admin Fee ($)", value=100, step=10)
insurance_premium = st.sidebar.number_input("Annual Insurance Premiums ($)", value=250, step=10)
lump_sum = st.sidebar.number_input("One-off Lump Sum Injection ($)", value=0, step=1000)
lump_sum_year = st.sidebar.number_input("Year of Lump Sum Injection", value=1, min_value=1, max_value=time_horizon, step=1)
cust_return = st.sidebar.slider("Return Rate (%)", 0.0, 20.0, 10.07) / 100
inflation_rate = st.sidebar.slider("Annual Inflation Rate (%)", 0.0, 5.0, 3.0) / 100

# Calculations
data = []
current_bal = starting_balance
cont = gross_contribution

for yr in range(1, time_horizon + 1):
    # Determine if lump sum applies this year
    injection = lump_sum if yr == lump_sum_year else 0
    
    # Deduct costs, add net contribution (15% tax)
    net_cont = (cont * 0.85) - admin_fee - insurance_premium
    
    # Apply growth (including injection)
    current_bal = (current_bal + net_cont + injection) * (1 + cust_return)
    
    # Inflation discount
    real_bal = current_bal / ((1 + inflation_rate) ** yr)
    
    data.append({
        "Year": yr,
        "Nominal Balance ($)": current_bal,
        "Real Purchasing Power ($)": real_bal
    })
    
    cont *= (1 + contribution_growth)

df = pd.DataFrame(data)

st.subheader("Projection Chart")
st.line_chart(df.set_index("Year"))

st.subheader("Summary Projection")
st.dataframe(df.style.format("${:,.0f}"))

st.markdown("---")
st.write("**Note:** This projection accounts for admin fees, insurance erosion, and contribution taxes. Remember to review Division 296 rules if your nominal balance crosses $3,000,000.")
