import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(page_title="Wade's Super Calculator", layout="wide")

st.title("Wade's Superannuation Projection Calculator")
st.markdown("Project your super balance factoring in SGC scaling, salary growth, and compliance.")

# Sidebar Controls
st.sidebar.header("Standard Assumptions")
starting_balance = st.sidebar.number_input("Starting Balance ($)", value=100000, step=1000)
salary = st.sidebar.number_input("Annual Salary ($)", value=100000, step=1000)
current_age = st.sidebar.slider("Current Age", 18, 75, 30)
retirement_age = st.sidebar.slider("Retirement Age", current_age, 85, 60)
time_horizon = retirement_age - current_age

st.sidebar.markdown(f"**Time Horizon:** {time_horizon} years")

employer_rate = st.sidebar.slider("Employer SGC Rate (%)", 10.0, 18.0, 11.5, step=0.5) / 100
sacrifice_percentage = st.sidebar.slider("Salary Sacrifice (%)", 0.0, 15.0, 0.0, step=0.5) / 100

# Cap Compliance Check (Initial)
employer_cont_init = salary * employer_rate
initial_sacrifice_amount = salary * sacrifice_percentage
total_concessional_init = initial_sacrifice_amount + employer_cont_init

if total_concessional_init > 30000:
    st.sidebar.error(f"⚠️ Initial Total Concessional Contribution (${total_concessional_init:,.0f}) exceeds the $30,000 cap!")
else:
    st.sidebar.success(f"Initial Total Concessional Contribution: ${total_concessional_init:,.0f}")

st.sidebar.markdown("---")
st.sidebar.header("Adjustment Sliders")
salary_growth = st.sidebar.slider("Annual Salary Increase (%)", 0.0, 10.0, 3.0) / 100
contribution_growth = st.sidebar.slider("Annual Sacrifice Increase (%)", 0.0, 10.0, 3.0) / 100
extra_contribution = st.sidebar.slider("Extra After-Tax Contribution ($)", 0, 50000, 0, step=1000)
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
curr_salary = salary
curr_sacrifice = initial_sacrifice_amount

for yr in range(1, time_horizon + 1):
    # Grow salary and sacrifice for this year
    curr_salary *= (1 + salary_growth)
    curr_sacrifice *= (1 + contribution_growth)
    
    # Calculate current employer contribution
    employer_cont = curr_salary * employer_rate
    
    # Determine if lump sum applies
    injection = lump_sum if yr == lump_sum_year else 0
    
    # Deduct costs, add net concessional (15% tax) + after-tax extra contribution
    net_cont = ((employer_cont + curr_sacrifice) * 0.85) - admin_fee - insurance_premium + extra_contribution
    
    # Apply growth (including injection)
    current_bal = (current_bal + net_cont + injection) * (1 + cust_return)
    
    # Inflation discount
    real_bal = current_bal / ((1 + inflation_rate) ** yr)
    
    data.append({
        "Year": yr,
        "Nominal Balance ($)": current_bal,
        "Real Purchasing Power ($)": real_bal
    })

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
st.write("**Note:** The prepopulated Fees and Insurance figures are indicative of a QPS officer with a Qsuper Account.")
