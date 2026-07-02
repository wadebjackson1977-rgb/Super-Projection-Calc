import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(page_title="Advanced Super Calculator", layout="wide")

st.title("Advanced Superannuation Projection Calculator")
st.markdown("Project your super balance factoring in SGC scaling, contribution caps, and real-world costs.")

# Sidebar Controls
st.sidebar.header("Standard Assumptions")
starting_balance = st.sidebar.number_input("Starting Balance ($)", value=100000, step=1000)

st.sidebar.markdown("---")
st.sidebar.header("Employment & Compliance")
salary = st.sidebar.number_input("Annual Salary ($)", value=100000, step=1000)
employer_rate = st.sidebar.slider("Employer SGC Rate (%)", 10.0, 18.0, 11.5, step=0.5) / 100
gross_contribution = st.sidebar.number_input("Voluntary Salary Sacrifice ($)", value=0, step=500)

# Cap Compliance Check
employer_cont = salary * employer_rate
total_concessional = gross_contribution + employer_cont
if total_concessional > 30000:
    st.sidebar.error(f"⚠️ Total Concessional Contribution (${total_concessional:,.0f}) exceeds the $30,000 cap!")
else:
    st.sidebar.success(f"Total Concessional Contribution: ${total_concessional:,.0f}")

st.sidebar.markdown("---")
st.sidebar.header("Adjustment Sliders")
extra_contribution = st.sidebar.slider("Extra After-Tax Contribution ($)", 0, 50000, 0, step=1000)
contribution_growth = st.sidebar.slider("Contribution Growth (%)", 0.0, 10.0, 3.0) / 100
time_horizon = st.sidebar.slider("Time Horizon (Years)", 5, 30, 10)
cust_return = st.sidebar.slider("Return Rate (%)", 0.0, 20.0, 10.07) / 100
inflation_rate = st.sidebar.slider("Annual Inflation Rate (%)", 0.0, 5.0, 3.0) / 100

st.sidebar.markdown("---")
st.sidebar.subheader("Advanced Settings")
admin_fee = st.sidebar.number_input("Annual Admin Fee ($)", value=557, step=10)
insurance_premium = st.sidebar.number_input("Annual Insurance Premiums ($)", value=2220, step=10)
lump_sum = st.sidebar.number_input("One-off Lump Sum Injection ($)", value=0, step=1000)
lump_sum_year = st.sidebar.number_input("Year of Lump Sum Injection", value=1, min_value=1, max_value=time_horizon, step=1)

# Calculations
data = []
current_bal = starting_balance
# Effective contribution is employer SGC + Salary Sacrifice + Extra After-Tax
cont = employer_cont + gross_contribution

for yr in range(1, time_horizon + 1):
    # Determine if lump sum applies this year
    injection = lump_sum if yr == lump_sum_year else 0
    
    # Deduct costs, add net concessional (15% tax) + after-tax extra contribution
    net_cont = (cont * 0.85) - admin_fee - insurance_premium + extra_contribution
    
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

# Visuals
st.subheader("Projection Chart")
st.line_chart(df.set_index("Year"))

st.subheader("Summary Projection")
st.dataframe(df.style.format({
    "Nominal Balance ($)": "${:,.0f}",
    "Real Purchasing Power ($)": "${:,.0f}"
}))

st.markdown("---")
st.write("**Note:** This projection accounts for annual fee/insurance erosion and contribution taxes. Remember to review Division 296 rules if your nominal balance crosses $3,000,000.")
