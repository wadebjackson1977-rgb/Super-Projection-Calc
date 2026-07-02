import streamlit as st
import pandas as pd
import numpy as np

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
CONCESSIONAL_CAP = 32500
employer_cont_init = salary * employer_rate
initial_sacrifice_amount = salary * sacrifice_percentage
total_concessional_init = initial_sacrifice_amount + employer_cont_init

if total_concessional_init > CONCESSIONAL_CAP:
    st.sidebar.error(f"⚠️ Initial Total Concessional Contribution (${total_concessional_init:,.0f}) exceeds the ${CONCESSIONAL_CAP:,.0f} cap!")
else:
    st.sidebar.success(f"Initial Total Concessional Contribution: ${total_concessional_init:,.0f}")

st.sidebar.markdown("---")
st.sidebar.header("Stress Testing & Adjustments")
stress_test_toggle = st.sidebar.toggle("Enable Market Volatility Stress Test", value=False)
if stress_test_toggle:
    volatility_slider = st.sidebar.slider("Market Volatility (%)", 0, 30, 15) / 100
else:
    volatility_slider = 0

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

# Calculations (Fortnightly Model)
num_periods = time_horizon * 26
fortnightly_mean_return = (1 + cust_return) ** (1 / 26) - 1
fortnightly_volatility = volatility_slider / np.sqrt(26) # Annual volatility scaled to fortnight

data = []
current_bal = starting_balance
cumulative_contributions = 0

# Track yearly variables
curr_salary = salary
curr_sacrifice_annual = initial_sacrifice_amount

for period in range(1, num_periods + 1):
    # Update annual stats at the start of each year (every 26 periods)
    if period % 26 == 1 and period > 1:
        curr_salary *= (1 + salary_growth)
        curr_sacrifice_annual *= (1 + contribution_growth)

    # Pro-rate annual figures for this period
    period_salary = curr_salary / 26
    period_sacrifice = curr_sacrifice_annual / 26
    employer_cont = period_salary * employer_rate
    period_admin_fee = admin_fee / 26
    period_insurance = insurance_premium / 26
    period_extra = extra_contribution / 26
    
    # Check for Lump Sum
    injection = lump_sum if (period - 1) // 26 + 1 == lump_sum_year and period % 26 == 1 else 0
    
    # Track contributions
    cumulative_contributions += (employer_cont + period_sacrifice + period_extra)
    
    # Net contribution calculation
    net_cont = ((employer_cont + period_sacrifice) * 0.85) - period_admin_fee - period_insurance + period_extra
    
    # Apply growth with optional stress testing
    if stress_test_toggle:
        # Normal distribution centered around mean return with user-defined volatility
        fortnightly_return = np.random.normal(fortnightly_mean_return, fortnightly_volatility)
    else:
        fortnightly_return = fortnightly_mean_return
        
    current_bal = (current_bal + net_cont + injection) * (1 + fortnightly_return)
    
    # Record data every year end
    if period % 26 == 0:
        yr = period // 26
        real_bal = current_bal / ((1 + inflation_rate) ** yr)
        data.append({
            "Year": yr,
            "Nominal Balance ($)": current_bal,
            "Real Purchasing Power ($)": real_bal,
            "Cumulative Contributions ($)": cumulative_contributions
        })

df = pd.DataFrame(data)

# Visuals
st.subheader("Projected Balance Over Time")
st.line_chart(df.set_index("Year")[["Nominal Balance ($)", "Real Purchasing Power ($)"]])

st.subheader("Summary Projection")
st.dataframe(df.style.format({
    "Nominal Balance ($)": "${:,.0f}",
    "Real Purchasing Power ($)": "${:,.0f}",
    "Cumulative Contributions ($)": "${:,.0f}"
}))

st.markdown("---")
st.write("**Note:** This projection accounts for annual fee/insurance erosion and contribution taxes. Remember to review Division 296 rules if your nominal balance crosses $3,000,000.")
st.write("**Note:** The prepopulated Fees and Insurance figures are indicative of a QPS officer with a Qsuper Account.")
