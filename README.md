# CommOpsAnalytics_TerritoryRec_Streamlit

## 1. Overview

This repository contains two Streamlit applications designed to assist in resource allocation for the Shockwave Medical commercial team. The apps recommend optimal locations for placing new Territory Managers (TM) and Field Clinical Specialists (FCS) in the USA.

## 2. Business Objective

Increase sales effectiveness by identifying geographic regions where adding a new TM or FCS would yield the greatest benefit. The models consider:
- Procedure volume
- Regional penetration
- Customer proximity to sales reps
- Estimated sales uplift

## 3. Users

- Colin Towner, VP, Global Commercial Operations  
- Ryan Melchior, Director, Sales Operations  
- Andy Heck, Sr. Sales Operations Manager  
- AVPs (Area Vice Presidents)

## 4. Streamlit Applications

### 4.1 US TM Add Recommendation

This app identifies regions where adding a TM will improve procedural coverage and penetration.

**Features:**
- Filter by account count and procedure thresholds
- Ranked table of recommendations
- Estimated coronary and peripheral unit increase
- Average distance reduction to customers
- PyDeck map comparison: current vs. proposed TM coverage

### 4.2 US FCS Add Recommendation

This app supports decisions about new FCS hires based on correlation between penetration and proximity to reps.

**Features:**
- Correlation analysis: rep distance vs. penetration
- Territory ranking with projected sales lift
- ZIP code recommendations for FCS placement
- Account assignments by territory
- PyDeck visualizations: before vs. after

## 5. Usage Patterns

- **TM Add App**: Used during headcount planning, territory design, and business reviews.
- **FCS Add App**: Used when hiring new FCS or reassessing regional coverage.

## 6. Technical & Functional Requirements

### Streamlit Dependencies
- Streamlit
- Snowflake Connector
- PyDeck
- Altair
- Pandas
- Seaborn
- Matplotlib

### 6.1 Data Sources

**Snowflake Schema:** `DEVELOPMENT.COMM_OPS_ANALYTICS`

#### 🔹 US TM Add Recommendation – Tables
- `TM_PLACEMENT_REGION_RANK_10ACCT_5000PROC`
- `TM_PLACEMENT_REGION_RANK_10ACCT_7500PROC`
- `TM_PLACEMENT_REGION_RANK_15ACCT_5000PROC`
- `TM_PLACEMENT_REGION_RANK_15ACCT_7500PROC`
- `TM_PLACEMENT_CUSTOMER_ASSIGNMENT_ADD_NEW_TM_10ACCT_5000PROC_FEA`
- `TM_PLACEMENT_CUSTOMER_ASSIGNMENT_ADD_NEW_TM_10ACCT_7500PROC_FEA`
- `TM_PLACEMENT_CUSTOMER_ASSIGNMENT_ADD_NEW_TM_15ACCT_5000PROC_FEA`
- `TM_PLACEMENT_CUSTOMER_ASSIGNMENT_ADD_NEW_TM_15ACCT_7500PROC_FEA`
- `TM_PLACEMENT_CUSTOMER_ASSIGNMENT_CURRENT_10ACCT_5000PROC`
- `TM_PLACEMENT_CUSTOMER_ASSIGNMENT_CURRENT_10ACCT_7500PROC`
- `TM_PLACEMENT_CUSTOMER_ASSIGNMENT_CURRENT_15ACCT_5000PROC`
- `TM_PLACEMENT_CUSTOMER_ASSIGNMENT_CURRENT_15ACCT_7500PROC`

#### 🔹 US FCS Add Recommendation – Tables
- `FCS_PLACEMENT_TERRITORY_RANK`
- `FCS_PLACEMENT_CUSTOMER_ASSIGNMENT_ADD_NEW_FCS`
- `FCS_PLACEMENT_CUSTOMER_ASSIGNMENT_CURRENT`
- `FCS_PLACEMENT_ACCOUNT_FEATURE`
- `FCS_PLACEMENT_ACCT_MILES_PENERATION`
- `DEVELOPMENT.CERTIFIED.DIM_SALES_TERRITORY`

## 7. Error Handling

- **Snowflake issues** → Contact Snowflake support  
- **Streamlit app issues** → Jing Xie (Sr. Data Scientist)

## 8. Scope and Requirements

### US TM Add Recommendation App

**Scope:**
Supports headcount planning by identifying high-opportunity regions for new TM placement using procedure volume, account density, and rep distance.

**Requirements:**
- Display regions meeting selected thresholds (10/15 accounts, 5000/7500 procedures)
- Show:
  - Estimated coronary & peripheral uplift
  - Miles saved
  - Penetration rate improvements
- Recommend ZIP code for new TM
- Map account assignment changes (before vs after)
- Filterable regional drill-downs

### US FCS Add Recommendation App

**Scope:**
Supports clinical field expansion by identifying ZIPs where FCS proximity could boost penetration.

**Requirements:**
- Rank territories by projected uplift and miles saved
- Recommend ZIP for new FCS
- Show correlation plots (penetration vs. distance)
- Simulate post-hire customer reassignments
- Visualize:
  - Before/after assignments
  - Account procedure & proximity data
  - Assigned reps & regions
- Allow filtering by territory, assignments, and penetration
