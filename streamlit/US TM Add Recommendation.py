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
DEVELOPMENT.COMM_OPS_ANALYTICS.COMMOPSANALYTICS_TERRITORYREC_STREAMLIT
# Get current session
session = get_active_session()
# Set page config
st.set_page_config(layout="wide")

def generate_random_color():
    import random
    return [random.randint(0, 255) for _ in range(3)]

st.title('US Territory Manager Placement Recommendation Dashboard')
#st.write(f"Find the best loaction for the new Territory Manager for US regions")

##########################################################################################
########################### show the whole table###########################################



acct_cnt = st.radio("Select Minimum Account Counts per Territory:", [10, 15])


proc_cnt = st.radio("Select Minimum Sum of Procedure Counnts per Territory:", [5000, 7500])


#'TM_PLACEMENT_REGION_RANK_%sACCT_%sPROC'%(acct_cnt,proc_cnt)

##########################################################################################
########################### show the whole table###########################################
table_nm=f'TM_PLACEMENT_REGION_RANK_{acct_cnt}ACCT_{proc_cnt}PROC'
df_best_location=session.table(table_nm).to_pandas()
#st.dataframe(df_best_location)
df_best_location['NEW_TM_ZIPCODE']=df_best_location['NEW_TM_ZIPCODE'].astype(str)
reg_cnt=len(set(df_best_location['REGION_NAME']))
#st.dataframe(df_best_location)


st.subheader('Region Ranking if Adding a New Territory Manager')
#df_best_location['TOTAL_DISTANCE_DECREASE']=df_best_location['AVERAGE_DISTANCE_DELTA']*df_best_location['ACCOUNT_COUNT']
#df_best_location['TOTAL_DISTANCE_DECREASE']=np.round(df_best_location['TOTAL_DISTANCE_DECREASE'],2)
df_best_location['AVERAGE_DISTANCE_DECREASE']=np.round(df_best_location['AVERAGE_DISTANCE_DELTA'],2)
df_best_location['CURRENT_AVERAGE_DISTANCE']=df_best_location['CURRENT_AVERAGE_DISTANCE'].round(2)
df_best_location['REGION_CORONARY_PENERATION_RATE']=df_best_location['REGION_CORONARY_PENERATION_RATE'].apply(lambda x: f"{x:.1%}")
df_best_location['NEWTM_CORONARY_PENERATION_RATE']=df_best_location['NEWTM_CORONARY_PENERATION_RATE'].apply(lambda x: f"{x:.1%}")
df_best_location['REGION_PERIPHERAL_PENERATION_RATE']=df_best_location['REGION_PERIPHERAL_PENERATION_RATE'].apply(lambda x: f"{x:.1%}")
df_best_location['NEWTM_PERIPHERAL_PENERATION_RATE']=df_best_location['NEWTM_PERIPHERAL_PENERATION_RATE'].apply(lambda x: f"{x:.1%}")

df_best_location['ESTIMATED_CORONARY_UNTIS_INCREASE']=df_best_location['ESTIMATED_CORONARY_UNTIS_INCREASE'].astype(int)
df_best_location['ESTIMATED_PERIPHERAL_UNTIS_INCREASE']=df_best_location['ESTIMATED_PERIPHERAL_UNTIS_INCREASE'].astype(int)

#st.dataframe(df_best_location)

df_best_location_show=df_best_location[['REGION_NAME','NEW_TM_ZIPCODE',
                                        'NEWTM_ACCOUNT_CNT',
                                        'AVERAGE_DISTANCE_DECREASE',
                                        'REGION_CORONARY_PENERATION_RATE', 
                                        'NEWTM_CORONARY_PENERATION_RATE',
                                        'NEWTM_CORONARY_PROCEDURES',
                                        'ESTIMATED_CORONARY_UNTIS_INCREASE',
                                        
                                        'REGION_PERIPHERAL_PENERATION_RATE',
                                        'NEWTM_PERIPHERAL_PENERATION_RATE',
                                        'NEWTM_PERIPHERAL_PROCEDURES',
                                        'ESTIMATED_PERIPHERAL_UNTIS_INCREASE',
                                        'FINAL_RANK']]
df_best_location_show=df_best_location_show.rename(columns={'REGION_NAME':'Region',
                                                       'NEW_TM_ZIPCODE':"Ideal Zip Code for New TM",
                                                    'NEWTM_ACCOUNT_CNT':'Accounts Assigned to New TM',
                                                     'AVERAGE_DISTANCE_DECREASE':'Average Driving Miles Decrease Adding New TM',
                                                      'REGION_CORONARY_PENERATION_RATE':'Region Coronary Peneration Rate',
                                                      'NEWTM_CORONARY_PENERATION_RATE':'Accounts Assigned to New TM Coronary Peneration Rate',
                                                      'NEWTM_CORONARY_PROCEDURES':'Accounts Assigned to New TM Coronary Procedure',
                                                    'ESTIMATED_CORONARY_UNTIS_INCREASE':'Estimated Annual Coronary Units Increase',
                                                    
                                                    'REGION_PERIPHERAL_PENERATION_RATE':'Region Peripheral Peneration Rate',
                                                      'NEWTM_PERIPHERAL_PENERATION_RATE':'Accounts Assigned to New TM Peripheral Peneration Rate',
                                                      'NEWTM_PERIPHERAL_PROCEDURES':'Accounts Assigned to New TM Peripheral Procedure',
                                                    'ESTIMATED_PERIPHERAL_UNTIS_INCREASE':'Estimated Annual Peripheral Units Increase',

                                                      'FINAL_RANK':'Adding TM Rank'})
st.dataframe(df_best_location_show.sort_values(by='Adding TM Rank'),hide_index=True,use_container_width=True)



###################################################################################
###########################Map to show ALl Region##################################


st.subheader(f'US Customers and Territory Managers Distribution for {reg_cnt} Regions')
multi = '''Red circles means new Territory Manager, blue cricles means current Territory Manager, green circles means accounts'''
st.markdown(multi)

new_fcs_ind = st.selectbox(
    "Select what you want to display on the map:",
    ("Only New TM nd Accounts Assgined to Them", 
     "All TM (current and new) and Accounts", 
     "Current TM and Accounts")
                            )

######################New assignment after adding the new TM################################## 

new_assign=f'TM_PLACEMENT_CUSTOMER_ASSIGNMENT_ADD_NEW_TM_{acct_cnt}ACCT_{proc_cnt}PROC_FEA'

curr_assign=f'TM_PLACEMENT_CUSTOMER_ASSIGNMENT_CURRENT_{acct_cnt}ACCT_{proc_cnt}PROC'

df_assgin_new_all=session.table(new_assign).to_pandas()

#df_assgin_new_all=df_assgin_new_all[df_assgin_new_all.REGION_NAME.isin(df_best_location.REGION_NAME)].reset_index(drop=True)

df_assgin_now=session.table(curr_assign).to_pandas()


df_assgin_new_all=df_assgin_new_all.merge(df_assgin_now[['ACCOUNT_ID','ACCOUNT_NAME']].drop_duplicates())

df_assgin_new_all['SIZE']=6000
df_assgin_new_all['COLOR']=None

for i in range(df_assgin_new_all.shape[0]):
    df_assgin_new_all['COLOR'][i]=[0, 255, 0] # initial all colors are green
### df_assgin_new_all is all the customers

#st.write('df_assgin_new_all is')
#st.dataframe(df_assgin_new_all.head(20))

####################get the dataframe for new reps####################################### 
# get the  sale rep's location
df_sale_rep_location=df_assgin_new_all[['REGION_NAME','ASSIGN_TO','SALE_REP_LATITUDE',
                                        'SALE_REP_LONGITUDE']].drop_duplicates().reset_index(drop=True)
# add sale rep user name
df_sale_rep_location['ACCOUNT_NAME']=df_sale_rep_location['ASSIGN_TO'].str.split('@',expand=True)[0]

df_sale_rep=df_sale_rep_location.rename(columns={'ASSIGN_TO':'ACCOUNT_ID',
                                                 'SALE_REP_LATITUDE':'ACCOUNT_LATITUDE',
                                                 'SALE_REP_LONGITUDE':'ACCOUNT_LONGITUDE'})
df_sale_rep['SIZE']=9000 # size of sale reps 
df_sale_rep['COLOR']=None # color of sale reps

for i in range(df_sale_rep.shape[0]):
    if df_sale_rep['ACCOUNT_NAME'][i]=='newtm':
        df_sale_rep['COLOR'][i]=[255, 0, 0] #red for new tm
    else:
        df_sale_rep['COLOR'][i]=[0, 0, 225] # blue for current sale reps

#st.write("this is all the TM")
#st.dataframe(df_sale_rep)


################### Get different sale rep based on selection##############################

if new_fcs_ind=='All TM (current and new) and Accounts':
    #df_sale_rep=df_assgin_new_all.copy()
    df_show=pd.concat([df_sale_rep,df_assgin_new_all[df_sale_rep.columns]],ignore_index=True)

if new_fcs_ind=='Current TM and Accounts':
    df_sale_rep=df_sale_rep[df_sale_rep.ACCOUNT_NAME!='newtm'].reset_index(drop=True)
    df_show=pd.concat([df_sale_rep,df_assgin_new_all[df_sale_rep.columns]],ignore_index=True)


if new_fcs_ind=='Only New TM nd Accounts Assgined to Them':
    df_sale_rep=df_sale_rep[df_sale_rep.ACCOUNT_NAME=='newtm'].reset_index(drop=True)
    df_assgin_new_all=df_assgin_new_all[df_assgin_new_all.ASSIGN_TO=='newtm@shockwavemedical.com'].reset_index(drop=True)
    df_show=pd.concat([df_sale_rep,df_assgin_new_all[df_sale_rep.columns]],ignore_index=True)
    df_show=df_show[df_show.REGION_NAME.isin(df_best_location.REGION_NAME)].reset_index(drop=True)





#st.dataframe(df_show)
df_show['ACCOUNT_LATITUDE'] = df_show['ACCOUNT_LATITUDE'].round(2)
df_show['ACCOUNT_LONGITUDE'] = df_show['ACCOUNT_LONGITUDE'].round(2)

# get the board line 
df_terr_min=df_show.groupby('REGION_NAME')[['ACCOUNT_LATITUDE','ACCOUNT_LONGITUDE']].min().reset_index()
df_terr_min=df_terr_min.rename(columns={'ACCOUNT_LATITUDE':'LAT_MIN','ACCOUNT_LONGITUDE':'LNG_MIN'})
df_terr_max=df_show.groupby('REGION_NAME')[['ACCOUNT_LATITUDE','ACCOUNT_LONGITUDE']].max().reset_index()
df_terr_max=df_terr_max.rename(columns={'ACCOUNT_LATITUDE':'LAT_MAX','ACCOUNT_LONGITUDE':'LNG_MAX'})
df_terr_points=pd.merge(df_terr_min,df_terr_max,on='REGION_NAME')


line_layers=[]
for i in range(reg_cnt):
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
    "html": "<b>{ACCOUNT_NAME}</b>:<b>[{ACCOUNT_LATITUDE},{ACCOUNT_LONGITUDE}]<br>in {REGION_NAME}",
    "style":    {
                 "backgroundColor": "steelblue",
                 "color": "white",
                 "fontSize": "12px"
                }
            }

# Create the Pydeck chart




# Render the chart in Streamlit
if new_fcs_ind!='Only New TM nd Accounts Assgined to Them':
    deck_new = pdk.Deck(
     map_style=None,
    layers=[scatter_layer_new],
    initial_view_state=view_state,
    tooltip=tooltip)
    #st.pydeck_chart(deck_new)

if new_fcs_ind=='Only New TM nd Accounts Assgined to Them':
    deck_new = pdk.Deck(
    map_style=None,
    layers=[scatter_layer_new,line_layers],
    initial_view_state=view_state,
    tooltip=tooltip)

st.pydeck_chart(deck_new)
##########################################################################################









###################################################################################
###########################Break down by regions ##################################

st.subheader("Breakdown by Regions")
# Create a selectbox in Streamlit
region_list=df_best_location['REGION_NAME'].drop_duplicates().tolist()
regions= st.multiselect("Select regions want to review:",region_list,default=region_list[0])

# best location for selected territory
df_best=df_best_location[df_best_location.REGION_NAME.isin(regions)].reset_index(drop=True)



curr_dists=df_best['CURRENT_AVERAGE_DISTANCE'].reset_index(drop=True)

df_assgin_old_all=session.table(curr_assign).to_pandas()
df_assgin_new_all=session.table(new_assign).to_pandas()




df_assgin_new_all=pd.merge(df_assgin_new_all,df_assgin_old_all[['ACCOUNT_ID','ACCOUNT_NAME']],on='ACCOUNT_ID',how='left')
df_assgin_new_all=pd.merge(df_assgin_new_all,df_assgin_old_all[['ASSIGN_TO','TERRITORY_NAME_SALE_REP']].drop_duplicates(),
                           on='ASSIGN_TO',how='left')

df_assgin_new_all.rename(columns={'TERRITORY_NAME_SALE_REP':'TERRIOTY_ASSGINED_ADDING_NEW_TM'},inplace=True)

df_assgin_new_all['TERRIOTY_ASSGINED_ADDING_NEW_TM']=df_assgin_new_all['TERRIOTY_ASSGINED_ADDING_NEW_TM'].fillna('New Territory')

df_reg_old=df_assgin_old_all[df_assgin_old_all.REGION_NAME.isin(regions)].reset_index(drop=True)
df_reg_new=df_assgin_new_all[df_assgin_new_all.REGION_NAME.isin(regions)].reset_index(drop=True)


df_one_reg_res=pd.merge(df_reg_old[['ACCOUNT_ID','ACCOUNT_NAME','TERRITORY_NAME_ACCOUNT','TERRITORY_NAME_SALE_REP']], 
                        df_reg_new[[ 'ACCOUNT_ID','TERRIOTY_ASSGINED_ADDING_NEW_TM',
                                     'AVG_CORONARY_PROCEDURES','AVG_PERIPHERAL_PROCEDURES']],on='ACCOUNT_ID',how='left')

df_one_reg_res.rename(columns={'TERRITORY_NAME_ACCOUNT':'TERRITORY_ACCOUNT_FROM_CURRENT',
                               'TERRITORY_NAME_SALE_REP':'TERRITORY_ASSIGNED_CURRENT'},inplace=True)

df_one_reg_res['SWITCH_TERRITORY_IND']=np.where(df_one_reg_res['TERRITORY_ASSIGNED_CURRENT']==df_one_reg_res['TERRIOTY_ASSGINED_ADDING_NEW_TM'],'NO','YES')

df_one_reg_res_show=df_one_reg_res[['ACCOUNT_NAME','TERRIOTY_ASSGINED_ADDING_NEW_TM','AVG_CORONARY_PROCEDURES','AVG_PERIPHERAL_PROCEDURES']]

df_one_reg_res_show['AVG_CORONARY_PROCEDURES']=df_one_reg_res_show['AVG_CORONARY_PROCEDURES'].fillna(0).astype(int)
df_one_reg_res_show['AVG_PERIPHERAL_PROCEDURES']=df_one_reg_res_show['AVG_PERIPHERAL_PROCEDURES'].fillna(0).astype(int)

df_one_reg_res_show.rename(columns={'ACCOUNT_NAME':'Account',
                                    'TERRIOTY_ASSGINED_ADDING_NEW_TM':'Territory Assgined',
                                   'AVG_CORONARY_PROCEDURES':'Annual Coronary Procedure',
                                   'AVG_PERIPHERAL_PROCEDURES':'Annual Peripheral Procedure'},inplace=True)

st.dataframe(df_one_reg_res_show, hide_index=True,use_container_width=False)


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
zip_codes=[]
unit_c=[]
unit_p=[]
new_vlats=[]
new_vlngs=[] 

# write a for loop to get info for every region
for reg in regions:
    
    ##################old assign###############################################################
    df_assgin_old=df_assgin_old_all[df_assgin_old_all.REGION_NAME==reg].reset_index(drop=True)
    
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
    df_assgin_old_color['SIZE']=6000
    #st.dataframe(df_color)
    
    # get the dataframe for reps
    df_old_rep_location=df_assgin_old[['REGION_NAME','ASSIGN_TO','SALE_REP_LATITUDE','SALE_REP_LONGITUDE']].drop_duplicates().reset_index(drop=True)
    df_old_rep_location['ACCOUNT_NAME']=df_old_rep_location['ASSIGN_TO'].str.split('@',expand=True)[0]
    df_old_rep_color=pd.merge(df_old_rep_location,df_old_color,how='left',on='ASSIGN_TO')
    df_old_rep_color=df_old_rep_color.rename(columns={'ASSIGN_TO':'ACCOUNT_ID','SALE_REP_LATITUDE':'ACCOUNT_LATITUDE','SALE_REP_LONGITUDE':'ACCOUNT_LONGITUDE'})
    df_old_rep_color['SIZE']=12000
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
    get_size=12,
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
    df_assgin_new=df_assgin_new_all[df_assgin_new_all.REGION_NAME==reg].reset_index(drop=True)
    #st.dataframe(df_assgin_new)
    
    # Add new color for New FCS
    df_color_new=df_old_color._append({'ASSIGN_TO':'newtm@shockwavemedical.com','COLOR':[255, 0, 0]},ignore_index=True)# red for new FCS
    df_assgin_new_color=pd.merge(df_assgin_new,df_color_new,on='ASSIGN_TO',how='left')
    df_assgin_new_color['SIZE']=6000
    
    # get the dataframe for new reps
    df_new_rep_location=df_assgin_new[['REGION_NAME','ASSIGN_TO','SALE_REP_LATITUDE','SALE_REP_LONGITUDE']].drop_duplicates().reset_index(drop=True)
    df_new_rep_location['ACCOUNT_NAME']=df_new_rep_location['ASSIGN_TO'].str.split('@',expand=True)[0]
    df_new_rep_color=pd.merge(df_new_rep_location,df_color_new,how='left',on='ASSIGN_TO')
    df_new_rep_color=df_new_rep_color.rename(columns={'ASSIGN_TO':'ACCOUNT_ID','SALE_REP_LATITUDE':'ACCOUNT_LATITUDE','SALE_REP_LONGITUDE':'ACCOUNT_LONGITUDE'})
    df_new_rep_color['SIZE']=12000
    df_res_new=pd.concat([df_new_rep_color,df_assgin_new_color[df_new_rep_color.columns]],ignore_index=True)
    #st.dataframe(df_res_new)
    
    df_res_new['ACCOUNT_LATITUDE'] = df_res_new['ACCOUNT_LATITUDE'].round(4)
    df_res_new['ACCOUNT_LONGITUDE'] = df_res_new['ACCOUNT_LONGITUDE'].round(4)
    
    new_dists.append(df_best[df_best.REGION_NAME==reg]['AVERAGE_DISTANCE_ADD_NEW_TM'].reset_index(drop=True)[0])
    deltas.append(df_best[df_best.REGION_NAME==reg]['AVERAGE_DISTANCE_DELTA'].reset_index(drop=True)[0])
    zip_codes.append(df_best[df_best.REGION_NAME==reg]['NEW_TM_ZIPCODE'].reset_index(drop=True)[0])
    unit_c.append(df_best[df_best.REGION_NAME==reg]['ESTIMATED_CORONARY_UNTIS_INCREASE'].reset_index(drop=True)[0])
    unit_p.append(df_best[df_best.REGION_NAME==reg]['ESTIMATED_PERIPHERAL_UNTIS_INCREASE'].reset_index(drop=True)[0])



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
    get_size=10,
    get_color=[[0,0,0]],
    get_angle=0,
    # Note that string constants in pydeck are explicitly passed as strings
    # This distinguishes them from columns in a data set
    get_text_anchor=String("middle"),
    get_alignment_baseline=String("center"),
                            )
    text_layer_news.append(text_layer_new)


for i in range(len(regions)):
    st.markdown(f'Currently there are {cts[i]} accounts and {repcnts[i]} territory managers in {regions[i]}, the average distance is {curr_dists[i]} miles.')
#st.markdown('''Small dots means customers, big dots means sale reps''')

# show the current assginment 
# Define the scatterplot layer

# Define the view state (center the view around San Francisco)
view_state = pdk.ViewState(
    latitude=vlats[0],
    longitude=vlngs[0],
    zoom=3,
)

# Define a tooltip
tooltip = {
   "html": "<b>{ACCOUNT_NAME}</b>:<b>[{ACCOUNT_LATITUDE},{ACCOUNT_LONGITUDE}]<br>in {REGION_NAME}",
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


vlat=df_res_new[df_res_new.ACCOUNT_NAME=='newtm'].reset_index(drop=True)['ACCOUNT_LATITUDE'][0]
vlng=df_res_new[df_res_new.ACCOUNT_NAME=='newtm'].reset_index(drop=True)['ACCOUNT_LONGITUDE'][0]
# Define the view state (center the view around San Francisco)
view_state = pdk.ViewState(
    latitude=vlat,
    longitude=vlng,
    zoom=3,
)

# Define a tooltip
tooltip = {
    "html": "<b>{ACCOUNT_NAME}</b>:<b>[{ACCOUNT_LATITUDE},{ACCOUNT_LONGITUDE}]<br>in {REGION_NAME}",
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
for i in range(len(regions)):
    st.markdown(f'If hiring a new TM in zip code {zip_codes[i]}(red big circle in the map), the average distance will decrease by {np.round(deltas[i],2)} miles, estimated annual coronary untis will increase by {unit_c[i]}, peripheral untis will increase by {unit_p[i]}')

# Render the chart in Streamlit
st.pydeck_chart(deck_new)
