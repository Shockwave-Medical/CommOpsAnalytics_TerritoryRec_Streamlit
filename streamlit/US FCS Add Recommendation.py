# Import libraries
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import sum, col, when, max, lag
from snowflake.snowpark import Window
from datetime import timedelta
import altair as alt
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from pydeck.types import String
import random
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Get current session
session = get_active_session()
# Set page config
st.set_page_config(layout="wide")

def generate_random_color():
    import random
    return [random.randint(0, 255) for _ in range(3)]
    
##########################################################################################
########################### show the correlation table###########################################
st.title('US FCS Placement Dashboard')

st.write('''Pearson correlation analysis shows peneration rate negatively related 
to the distance between accounts and sales reps. Therefore, we are working to identify the optimal
location for a new FCS in each territory to minimize the average distance between accounts and sales reps.''')


#df_model=session.table('FCS_PLACEMENT_ACCOUNT_FEATURE_QTY').to_pandas() 
df_corr_data=session.table('FCS_PLACEMENT_ACCT_MILES_PENERATION').to_pandas()
c1, c2= st.columns(2)



## coronary plot
df_corr_c=df_corr_data[(~df_corr_data.ACT_SFDC_ID.isnull())
                    &(df_corr_data.AVG_CORONARY_PENETRATION>0)
                    &(df_corr_data.AVG_CORONARY_PENETRATION<0.8)
                    &(df_corr_data.DRIVE_MILES<250)].reset_index(drop=True)

# Create coronary figure with regression line
fig1, ax1 = plt.subplots(figsize=(6, 3))
sns.regplot(data=df_corr_c, x="DRIVE_MILES", y="AVG_CORONARY_PENETRATION", ax=ax1, 
            scatter_kws={'alpha':0.5}, line_kws={'color':'red'},ci=None)

ax1.set_title("Account Coronary Penetration VS Miles to Sales Rep",fontsize=8)
ax1.set_xlabel("Driving Miles from Account to Nearest Sale Rep",fontsize=8)  # Set X-axis label
ax1.set_ylabel("Coronary Penetration Rate",fontsize=8)  # Optional: Set Y-axis label
# Display plot
c1.pyplot(fig1)
c1.write('Distance from accounts to sales reps is significantly negatively correlated with coronary penetration rate.')



## peripheral plot
df_corr_p=df_corr_data[(~df_corr_data.ACT_SFDC_ID.isnull())
                    &(df_corr_data.AVG_PERIPHERAL_PENETRATION>0)
                    &(df_corr_data.AVG_PERIPHERAL_PENETRATION<0.8)
                    &(df_corr_data.DRIVE_MILES<250)].reset_index(drop=True)




# Create figure
fig2, ax2 = plt.subplots(figsize=(6, 3))
sns.regplot(data=df_corr_p, x="DRIVE_MILES", y="AVG_PERIPHERAL_PENETRATION", ax=ax2, 
           line_kws={'color':'red'},ci=None)


ax2.set_title("Account Peripheral Peneration VS Miles to Sale Rep",fontsize=8)
ax2.set_xlabel("Driving Miles from Account to Nearby Sale Rep",fontsize=8)  # Set X-axis label
ax2.set_ylabel("Peripheral Penetration Rate",fontsize=8)  # Optional: Set Y-axis label
# Display plot
c2.pyplot(fig2)
c2.write('Distance from accounts to sale reps is negatively correlated with peripheral penetration rate but not sigificantly.')






####################################################
##########territory Distance delta ###############
#####################################################


df_best_location=session.table('FCS_PLACEMENT_TERRITORY_RANK').to_pandas()
df_territory_all=session.table('DEVELOPMENT.CERTIFIED.DIM_SALES_TERRITORY').to_pandas()
df_reg_use=df_territory_all[(df_territory_all.L1_NAME=='US')&(df_territory_all.L0_NAME=='IVL')&(df_territory_all.L5_NAME.str.contains('US - '))].reset_index(drop=True)

df_reg_use=df_reg_use[['L4_NAME','L5_ID']].drop_duplicates()
#df_best_location['ANNUAL_UNITS_INCREASE_ESTIMATED']=df_best_location['ANNUAL_UNITS_INCREASE_ESTIMATED'].astype(int)
### add the peneration rate 
#df_terr_pene=session.table('FCS_PLACEMENT_TERRITORY_PENERATION_RATE').to_pandas()
#df_best_location=pd.merge(df_best_location,df_terr_pene, on=['TERRITORY_NAME'],how='left')
terr_cnt=len(set(df_best_location.TERRITORY_NAME))

st.subheader(f'Territory Ranking if Adding a New FCS')

df_best_location=pd.merge(df_best_location,df_reg_use,left_on='TERRITORY_ID',right_on='L5_ID',how='left')

df_best_location_show=df_best_location[[ 'L4_NAME',
                                        'TERRITORY_NAME',
                                        'NEW_FCS_ZIPCODE',
                                         'ACCOUNT_CNT_NEW_FCS',
                                        'DRIVING_MILES_DECREASE',
                                        'TERR_CORONARY_PENERATION', 
                                        'NEWFCS_CORONARY_PENERATION',
                                        'NEWFCS_CORONARY_PROCEDURES',
                                        'ESTIMATED_CORONARY_UNTIS_INCREASE',
                                        
                                        'TERR_PERIPHERAL_PENERATION',
                                        'NEWFCS_PERIPHERAL_PENERATION',
                                        'NEWFCS_PERIPHERAL_PROCEDURES',
                                        'ESTIMATED_PERIPHERAL_UNTIS_INCREASE',
                                        'FINAL_RANK']]

df_best_location_show['DRIVING_MILES_DECREASE']=df_best_location_show['DRIVING_MILES_DECREASE'].round(1)

df_best_location_show['TERR_CORONARY_PENERATION']=df_best_location_show['TERR_CORONARY_PENERATION'].apply(lambda x: f"{x:.1%}")
df_best_location_show['NEWFCS_CORONARY_PENERATION']=df_best_location_show['NEWFCS_CORONARY_PENERATION'].apply(lambda x: f"{x:.1%}")
df_best_location_show['TERR_PERIPHERAL_PENERATION']=df_best_location_show['TERR_PERIPHERAL_PENERATION'].apply(lambda x: f"{x:.1%}")
df_best_location_show['NEWFCS_PERIPHERAL_PENERATION']=df_best_location_show['NEWFCS_PERIPHERAL_PENERATION'].apply(lambda x: f"{x:.1%}")


df_best_location_show.rename(columns={'TERRITORY_NAME':'Territory',
                                      'L4_NAME':'Region',
                                      'NEW_FCS_ZIPCODE':"Ideal Zip Code for New FCS",
                                      'ACCOUNT_CNT_NEW_FCS':'Accounts Assgined to New FCS',
                                    'DRIVING_MILES_DECREASE':'Driving Miles Decrease' ,
                                    'TERR_CORONARY_PENERATION':'Territory Coronary Peneration Rate',
                                    'NEWFCS_CORONARY_PENERATION':'Accounts Assigned to New FCS Coronary Peneration Rate',
                                      'TERR_PERIPHERAL_PENERATION':'Territory Peripheral Peneration Rate',
                                        'NEWFCS_PERIPHERAL_PENERATION':'Accounts Assigned to New FCS Peripheral Peneration Rate',

                                     'NEWFCS_CORONARY_PROCEDURES':'Coronary Procedure of Accounts Assigned to New FCS',
                                     'NEWFCS_PERIPHERAL_PROCEDURES':'Peripheral Procedure of Accounts Assigned to New FCS',
                                     'ESTIMATED_CORONARY_UNTIS_INCREASE':'Estimated Annual Coronary Units Increase',
                                      'ESTIMATED_PERIPHERAL_UNTIS_INCREASE':'Estimated Annual Peripheral Units Increase',
                                    'FINAL_RANK':'Adding FCS Rank'},inplace=True)


st.dataframe(df_best_location_show.sort_values(by='Adding FCS Rank'),hide_index=True, use_container_width=True)




##########################################################################################
######################### MAP for All US Customers and New FCS ###########################
st.subheader(f'US Customers and Sales Reps Distribution for {terr_cnt} Territories')
multi = '''Red circles means new FCS, blue cricles means current TM or FCS, green circles means accounts'''
st.markdown(multi)

new_fcs_ind = st.selectbox(
    "Select what you want to display on the map:",
    ("Only New FCS and Accounts Assgined to Them", "New FCS, Current TM, FCS and Accounts", "Current TM, FCS and Accounts")
                            )

##########################################################################################
######################### Get the data for different opitions ###########################
# New assignment after adding the new FCS
df_assgin_new_all=session.table('FCS_PLACEMENT_CUSTOMER_ASSIGNMENT_ADD_NEW_FCS').to_pandas()
df_assgin_new_all=df_assgin_new_all[df_assgin_new_all.TERRITORY_ID.isin(df_best_location.TERRITORY_ID)].reset_index(drop=True)

df_assgin_new_all['SIZE']=3000
df_assgin_new_all['COLOR']=None

for i in range(df_assgin_new_all.shape[0]):
    df_assgin_new_all['COLOR'][i]=[0, 255, 0] # initial all colors are green
##########################################################################################




##########################################################################################
####################get the dataframe for new reps####################################### 
df_sale_rep_location=df_assgin_new_all[['TERRITORY_NAME','ASSIGN_TO','SALE_REP_LATITUDE','SALE_REP_LONGITUDE']].drop_duplicates().reset_index(drop=True)
# add sale rep user name
df_sale_rep_location['ACCOUNT_NAME']=df_sale_rep_location['ASSIGN_TO'].str.split('@',expand=True)[0]
df_sale_rep=df_sale_rep_location.rename(columns={'ASSIGN_TO':'ACCOUNT_ID','SALE_REP_LATITUDE':'ACCOUNT_LATITUDE','SALE_REP_LONGITUDE':'ACCOUNT_LONGITUDE'})
df_sale_rep['SIZE']=6000 # size of sale reps 
df_sale_rep['COLOR']=None # color of sale reps

for i in range(df_sale_rep.shape[0]):
    if df_sale_rep['ACCOUNT_NAME'][i]=='newfcs':
        df_sale_rep['COLOR'][i]=[255, 0, 0] #red for new fcs
    else:
        df_sale_rep['COLOR'][i]=[0, 0, 225] # blue for current sale reps


##########################################################################################
################### Get different sale rep based on selection##############################

#if new_fcs_ind=='New FCS, Current TM, FCS and Accounts':
    #df_sale_rep=df_assgin_new_all.copy()
if new_fcs_ind=='Current TM, FCS and Accounts':
    df_sale_rep=df_sale_rep[df_sale_rep.ACCOUNT_NAME!='newfcs'].reset_index(drop=True)

if new_fcs_ind=='Only New FCS and Accounts Assgined to Them':
    df_sale_rep=df_sale_rep[df_sale_rep.ACCOUNT_NAME=='newfcs'].reset_index(drop=True)
    df_assgin_new_all=df_assgin_new_all[df_assgin_new_all.ASSIGN_TO=='newfcs@shockwavemedical.com'].reset_index(drop=True)

    df_terr_min=df_assgin_new_all.groupby('TERRITORY_NAME')[['ACCOUNT_LATITUDE','ACCOUNT_LONGITUDE']].min().reset_index()
    df_terr_min=df_terr_min.rename(columns={'ACCOUNT_LATITUDE':'LAT_MIN','ACCOUNT_LONGITUDE':'LNG_MIN'})
    df_terr_max=df_assgin_new_all.groupby('TERRITORY_NAME')[['ACCOUNT_LATITUDE','ACCOUNT_LONGITUDE']].max().reset_index()
    df_terr_max=df_terr_max.rename(columns={'ACCOUNT_LATITUDE':'LAT_MAX','ACCOUNT_LONGITUDE':'LNG_MAX'})
    df_terr_points=pd.merge(df_terr_min,df_terr_max,on='TERRITORY_NAME')

    
    line_layers=[]
    for i in range(terr_cnt):
        data1=[{"start": [df_terr_points['LNG_MAX'][i], df_terr_points['LAT_MIN'][i]], "end": [df_terr_points['LNG_MAX'][i], df_terr_points['LAT_MAX'][i]]},  
        {"start": [df_terr_points['LNG_MAX'][i], df_terr_points['LAT_MAX'][i]], "end": [df_terr_points['LNG_MIN'][i], df_terr_points['LAT_MAX'][i]]},
        {"start": [df_terr_points['LNG_MIN'][i], df_terr_points['LAT_MAX'][i]], "end": [df_terr_points['LNG_MIN'][i], df_terr_points['LAT_MIN'][i]]},
        {"start": [df_terr_points['LNG_MIN'][i], df_terr_points['LAT_MIN'][i]], "end": [df_terr_points['LNG_MAX'][i], df_terr_points['LAT_MIN'][i]]}]
 
        line_layers.append(pdk.Layer(
          "LineLayer",
          data=data1,
            get_source_position="start",
            get_target_position="end",
            get_width=2,
            get_color=generate_random_color()  # Red color for lines
                    ))



df_show=pd.concat([df_sale_rep,df_assgin_new_all[df_sale_rep.columns]],ignore_index=True)
#st.dataframe(df_fcs_new)
df_show['ACCOUNT_LATITUDE'] = df_show['ACCOUNT_LATITUDE'].round(2)
df_show['ACCOUNT_LONGITUDE'] = df_show['ACCOUNT_LONGITUDE'].round(2)

scatter_layer_new = pdk.Layer(
    "ScatterplotLayer",
    data=df_show,
    pickable=True,
    get_position='[ACCOUNT_LONGITUDE, ACCOUNT_LATITUDE]',  # Set longitude and latitude
    get_radius='SIZE',  # Set a fixed radius
    get_color='COLOR',  # Set a fixed color with alpha
    auto_highlight=True
                            )

##########################################################################################
################### Draw the line boarder for territory   ##############################


# Define the view state (center the view around San Francisco)
view_state = pdk.ViewState(
    latitude=39,
    longitude=-94,
    zoom=5,
                            )

# Define a tooltip
tooltip = {
    "html": "<b>{ACCOUNT_NAME}</b>:<b>[{ACCOUNT_LATITUDE},{ACCOUNT_LONGITUDE}]<br>in {TERRITORY_NAME}",
    "style":    {
                 "backgroundColor": "steelblue",
                 "color": "white",
                 "fontSize": "12px"
                }
            }

# Create the Pydeck chart




# Render the chart in Streamlit
if new_fcs_ind!='Only New FCS and Accounts Assgined to Them':
    deck_new = pdk.Deck(
    map_style=None,
    layers=[scatter_layer_new],
    initial_view_state=view_state,
    tooltip=tooltip
                    )
    st.pydeck_chart(deck_new)

if new_fcs_ind=='Only New FCS and Accounts Assgined to Them':
    deck_new = pdk.Deck(
    map_style=None,
    layers=[scatter_layer_new,line_layers],
    initial_view_state=view_state,
    tooltip=tooltip
                    )
    st.pydeck_chart(deck_new)
##########################################################################################




##########################################################################################
###########################Break down by territoies  ##################################
st.subheader("Breakdown by Territories")
# Create a selectbox in Streamlit
terr_list=df_best_location['TERRITORY_NAME'].tolist()
terrs = st.multiselect("Select territories want to review:",terr_list,default=terr_list[0],key=2)



#  Accounts Assigned to New FCS 
df_terr_rate=df_best_location[['TERRITORY_NAME',
                                        'TERR_CORONARY_PENERATION', 
                                        'TERR_PERIPHERAL_PENERATION',
                                       ]].copy()

df_terr_rate['TERR_CORONARY_PENERATION']=df_terr_rate['TERR_CORONARY_PENERATION'].round(2)
df_terr_rate['TERR_PERIPHERAL_PENERATION']=df_terr_rate['TERR_PERIPHERAL_PENERATION'].round(2)

df_fea=session.table('FCS_PLACEMENT_ACCOUNT_FEATURE').to_pandas()
df_fea=df_fea.merge(df_terr_rate)

df_fea_use=df_fea[(df_fea.ASSIGN_TO=='newfcs@shockwavemedical.com')
                &(df_fea.TERRITORY_NAME.isin(terrs))][['TERRITORY_NAME', 'ACCOUNT_NAME', 'ASSIGN_TO',
                                                     'TERR_CORONARY_PENERATION','AVG_CORONARY_PENETRATION',
                    'AVG_CORONARY_PROCEDURES','TERR_PERIPHERAL_PENERATION',
                      
                  'AVG_PERIPHERAL_PENETRATION','AVG_PERIPHERAL_PROCEDURES']].reset_index(drop=True)

df_fea_use['TERR_CORONARY_PENERATION']=df_fea_use['TERR_CORONARY_PENERATION'].apply(lambda x: f"{x:.1%}")
df_fea_use['AVG_CORONARY_PENETRATION']=df_fea_use['AVG_CORONARY_PENETRATION'].apply(lambda x: f"{x:.1%}")
df_fea_use['TERR_PERIPHERAL_PENERATION']=df_fea_use['TERR_PERIPHERAL_PENERATION'].apply(lambda x: f"{x:.1%}")
df_fea_use['AVG_PERIPHERAL_PENETRATION']=df_fea_use['AVG_PERIPHERAL_PENETRATION'].apply(lambda x: f"{x:.1%}")

st.write("Here are the accounts assgiend to the new FCS for the selected territories")


df_fea_use.rename(columns={'TERRITORY_NAME':'Territory','ACCOUNT_NAME':'Account',
                           'ASSIGN_TO':'Assigned to',
                            'TERR_CORONARY_PENERATION':'Territory Coronary Peneration Rate',
                           'AVG_CORONARY_PROCEDURES':'Coronary Procedures Annual',
                           'TERR_PERIPHERAL_PENERATION':'Territory Peripheral Peneration Rate',
                           'AVG_PERIPHERAL_PROCEDURES':'Peripheral Procedures Annual',
                          'AVG_PERIPHERAL_PENETRATION':'Peripheral Peneration Rate',
                          'AVG_CORONARY_PENETRATION':'Coronary Peneration Rate'},inplace=True)
st.dataframe(df_fea_use,hide_index=True)


# best location for selected territory
df_best=df_best_location[df_best_location.TERRITORY_NAME.isin(terrs)].reset_index(drop=True)

curr_dists=df_best['CURRENT_AVERAGE_DISTANCE'].reset_index(drop=True)

df_assgin_old_all=session.table('FCS_PLACEMENT_CUSTOMER_ASSIGNMENT_CURRENT').to_pandas()
df_assgin_new_all=session.table('FCS_PLACEMENT_CUSTOMER_ASSIGNMENT_ADD_NEW_FCS').to_pandas()

def generate_random_color():
    return [random.randint(0, 255) for _ in range(3)]
    
scatter_layers=[]
text_layers=[]
scatter_layer_news=[]
text_layer_news=[]

repcnts=[]
cts=[]
vlats=[]
vlngs=[]

new_dists=[]
deltas=[]
units_pe=[]
units_cor=[]
zip_codes=[]
new_vlats=[]
new_vlngs=[]

# write a for loop to get info for every territory
for terr in terrs:
    
    ##################old assign###############################################################
    df_assgin_old=df_assgin_old_all[df_assgin_old_all.TERRITORY_NAME==terr].reset_index(drop=True)
    
    # create color list for sale reps
    df_old_color=df_assgin_old[['ASSIGN_TO']].drop_duplicates().reset_index(drop=True)

    import random
    color_list=[]
    for i in range(df_old_color.shape[0]):
        color_list.append(generate_random_color())
        
    # give color value for every rep
    df_old_color['COLOR']=color_list
    #st.dataframe(df_old_color)
    
    # give color for avery account based on assgined rep
    df_assgin_old_color=pd.merge(df_assgin_old,df_old_color,on='ASSIGN_TO',how='left')
    df_assgin_old_color['SIZE']=2000
    #st.dataframe(df_color)
    
    # get the dataframe for reps
    df_old_rep_location=df_assgin_old[['TERRITORY_NAME','ASSIGN_TO','SALE_REP_LATITUDE','SALE_REP_LONGITUDE']].drop_duplicates().reset_index(drop=True)
    df_old_rep_location['ACCOUNT_NAME']=df_old_rep_location['ASSIGN_TO'].str.split('@',expand=True)[0]
    df_old_rep_color=pd.merge(df_old_rep_location,df_old_color,how='left',on='ASSIGN_TO')
    df_old_rep_color=df_old_rep_color.rename(columns={'ASSIGN_TO':'ACCOUNT_ID','SALE_REP_LATITUDE':'ACCOUNT_LATITUDE','SALE_REP_LONGITUDE':'ACCOUNT_LONGITUDE'})
    df_old_rep_color['SIZE']=4000
    df_res_old=pd.concat([df_old_rep_color,df_assgin_old_color[df_old_rep_color.columns]],ignore_index=True)
    #st.dataframe(df_res_old)
    df_res_old['ACCOUNT_LATITUDE'] = df_res_old['ACCOUNT_LATITUDE'].round(4)
    df_res_old['ACCOUNT_LONGITUDE'] = df_res_old['ACCOUNT_LONGITUDE'].round(4)

    scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_res_old,
    pickable=True,
    get_position='[ACCOUNT_LONGITUDE, ACCOUNT_LATITUDE]',  # Set longitude and latitude
    get_radius='SIZE',  # Set a fixed radius
    get_color='COLOR',  # Set a fixed color with alpha
    auto_highlight=True        )
    
    scatter_layers.append(scatter_layer)


    text_layer =  pdk.Layer(  
    "TextLayer",
    data=df_old_rep_color,
    pickable=True,
    get_position='[ACCOUNT_LONGITUDE, ACCOUNT_LATITUDE]',
    get_text="ACCOUNT_NAME",
    get_size=14,
    get_color=[0,0,0],
    get_angle=0,
    # Note that string constants in pydeck are explicitly passed as strings
    # This distinguishes them from columns in a data set
    get_text_anchor=String("middle"),
    get_alignment_baseline=String("center"),
                            )
    
    text_layers.append(text_layer)

    repcnts.append(df_old_color.shape[0])
    cts.append(df_assgin_old.shape[0])
    vlats.append(df_res_old['ACCOUNT_LATITUDE'].mean())
    vlngs.append(df_res_old['ACCOUNT_LONGITUDE'].mean())

    ################################################################################
    #######################Data for new assignment #################################
    df_assgin_new=df_assgin_new_all[df_assgin_new_all.TERRITORY_NAME==terr].reset_index(drop=True)
    #st.dataframe(df_assgin_new)
    
    # Add new color for New FCS
    df_color_new=df_old_color._append({'ASSIGN_TO':'newfcs@shockwavemedical.com','COLOR':[255, 0, 0]},ignore_index=True)# red for new FCS
    df_assgin_new_color=pd.merge(df_assgin_new,df_color_new,on='ASSIGN_TO',how='left')
    df_assgin_new_color['SIZE']=2000
    
    # get the dataframe for new reps
    df_new_rep_location=df_assgin_new[['TERRITORY_NAME','ASSIGN_TO','SALE_REP_LATITUDE','SALE_REP_LONGITUDE']].drop_duplicates().reset_index(drop=True)
    df_new_rep_location['ACCOUNT_NAME']=df_new_rep_location['ASSIGN_TO'].str.split('@',expand=True)[0]
    df_new_rep_color=pd.merge(df_new_rep_location,df_color_new,how='left',on='ASSIGN_TO')
    df_new_rep_color=df_new_rep_color.rename(columns={'ASSIGN_TO':'ACCOUNT_ID','SALE_REP_LATITUDE':'ACCOUNT_LATITUDE','SALE_REP_LONGITUDE':'ACCOUNT_LONGITUDE'})
    df_new_rep_color['SIZE']=4000
    df_res_new=pd.concat([df_new_rep_color,df_assgin_new_color[df_new_rep_color.columns]],ignore_index=True)
    #st.dataframe(df_res_new)
    
    df_res_new['ACCOUNT_LATITUDE'] = df_res_new['ACCOUNT_LATITUDE'].round(4)
    df_res_new['ACCOUNT_LONGITUDE'] = df_res_new['ACCOUNT_LONGITUDE'].round(4)
    
    new_dists.append(df_best[df_best.TERRITORY_NAME==terr]['AVERAGE_DISTANCE_ADD_NEW_FCS'].reset_index(drop=True)[0])
    deltas.append(df_best[df_best.TERRITORY_NAME==terr]['DRIVING_MILES_DECREASE'].reset_index(drop=True)[0])
    units_pe.append(df_best[df_best.TERRITORY_NAME==terr]['ESTIMATED_PERIPHERAL_UNTIS_INCREASE'].reset_index(drop=True)[0])
    units_cor.append(df_best[df_best.TERRITORY_NAME==terr]['ESTIMATED_CORONARY_UNTIS_INCREASE'].reset_index(drop=True)[0])

    zip_codes.append(df_best[df_best.TERRITORY_NAME==terr]['NEW_FCS_ZIPCODE'].reset_index(drop=True)[0])



    scatter_layer_new = pdk.Layer(
    "ScatterplotLayer",
    data=df_res_new,
    pickable=True,
    get_position='[ACCOUNT_LONGITUDE, ACCOUNT_LATITUDE]',  # Set longitude and latitude
    get_radius='SIZE',  # Set a fixed radius
    get_color='COLOR',  # Set a fixed color with alpha
    auto_highlight=True
                                )
    
    scatter_layer_news.append(scatter_layer_new)
    
    text_layer_new =  pdk.Layer(  
    "TextLayer",
    data=df_new_rep_color,
    pickable=True,
    get_position='[ACCOUNT_LONGITUDE, ACCOUNT_LATITUDE]',
    get_text="ACCOUNT_NAME",
    get_size=14,
    get_color=[[0,0,0]],
    get_angle=0,
    # Note that string constants in pydeck are explicitly passed as strings
    # This distinguishes them from columns in a data set
    get_text_anchor=String("middle"),
    get_alignment_baseline=String("center"),
                            )
    text_layer_news.append(text_layer_new)


for i in range(len(terrs)):
    st.markdown(f'Currently there are {cts[i]} customers and {repcnts[i]} sale reps in {terrs[i]}, the average distance is {curr_dists[i].round(2)} miles.')
#st.markdown('''Small dots means customers, big dots means sale reps''')

# show the current assginment 
# Define the scatterplot layer

# Define the view state (center the view around San Francisco)
view_state = pdk.ViewState(
    latitude=vlats[0],
    longitude=vlngs[0],
    zoom=7,
)

# Define a tooltip
tooltip = {
   "html": "<b>{ACCOUNT_NAME}</b>:<b>[{ACCOUNT_LATITUDE},{ACCOUNT_LONGITUDE}]<br>in {TERRITORY_NAME}",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white",
        "fontSize": "12px"
    }
}

# Create the Pydeck chart
deck = pdk.Deck(
    map_style=None,
    layers=[scatter_layers,text_layers],
    initial_view_state=view_state,
    tooltip=tooltip
)

# Render the chart in Streamlit
st.pydeck_chart(deck)

##########################################################################################



####################################Add the New FCS ###############################################
# New assignment after adding the new FCS
####################################################################################


vlat=df_res_new[df_res_new.ACCOUNT_NAME=='newfcs'].reset_index(drop=True)['ACCOUNT_LATITUDE'][0]
vlng=df_res_new[df_res_new.ACCOUNT_NAME=='newfcs'].reset_index(drop=True)['ACCOUNT_LONGITUDE'][0]
# Define the view state (center the view around San Francisco)
view_state = pdk.ViewState(
    latitude=vlat,
    longitude=vlng,
    zoom=7,
)

# Define a tooltip
tooltip = {
    "html": "<b>{ACCOUNT_NAME}</b>:<b>[{ACCOUNT_LATITUDE},{ACCOUNT_LONGITUDE}]<br>in {TERRITORY_NAME}",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white",
        "fontSize": "12px"
    }
}

# Create the Pydeck chart
deck_new = pdk.Deck(
    map_style=None,
    layers=[scatter_layer_news,text_layer_news],
    initial_view_state=view_state,
    tooltip=tooltip
)
for i in range(len(terrs)):
    st.markdown(f'If hire a new FCS from zip code {zip_codes[i]}(red big circle) for {terrs[i]}, the average distance will decrease by {deltas[i].round(2)} miles and the estimated coronary annual units will increase by {units_cor[i]}, estimated peripheral annual units will increase by {units_pe[i]}')

# Render the chart in Streamlit
st.pydeck_chart(deck_new)
