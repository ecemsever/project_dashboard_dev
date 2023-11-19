import pandas as pd
import plotly.express as px
import streamlit as st
import os
import datetime
from PIL import Image

dir = os.path.dirname(__file__)

st.set_page_config(
    page_title="Welcome to PowerRangers Dashboard",
    page_icon="👋",
    layout='wide'
    )

st.markdown("""## PowerRangers Energy Analytics Dashboard""")

pred_8_hours = pd.read_csv(dir+'/1_week_to_8_hours_pred.csv')
pred_8_hours['Day'] = pd.to_datetime(pred_8_hours['valid_start']).dt.date
pred_8_hours['Year'] = pd.to_datetime(pred_8_hours['valid_start']).dt.year

pred_8_hours_daily = pred_8_hours.groupby(['Day'])['total_demand'].agg('sum').reset_index(name='Total Demand')

#pred_168_hours = pd.read_csv(dir+'/4_weeks_to_1_weeks_pred.csv')
#pred_168_hours['Day'] = pd.to_datetime(pred_168_hours['valid_start']).dt.date
#pred_168_hours['Year'] = pd.to_datetime(pred_168_hours['valid_start']).dt.year

#pred_168_hours_daily = pred_168_hours.groupby(['Day'])['total_demand'].agg('sum').reset_index(name='Total Demand')


tab1, tab2 = st.tabs(["Historical Analytics", "Predictive Analytics"])

with tab1:
    d1, d2 = st.columns(2)
    start_date=min(pred_8_hours_daily["Day"])
    sd=d1.date_input("Select a starting date",start_date)

    end_date=max(pred_8_hours_daily["Day"])
    ed=d2.date_input("Select a end date",end_date)
    
    line_graph = px.line(
        data_frame = pred_8_hours_daily[pred_8_hours_daily["Day"].between(sd, ed)], title='Total Demand Daily', 
        x='Day', y='Total Demand')
    line_graph.update_layout(width=1300,height=400)
    st.plotly_chart(line_graph)

    # Create the line graph for hourly
    line_graph2 = px.line(
        data_frame = pred_8_hours[pred_8_hours["Day"].between(sd, ed)], title='Total Demand Hourly', 
        x='valid_start', y='total_demand')
    line_graph2.update_layout(width=1300,height=400)
    st.plotly_chart(line_graph2)

with tab2:
    def calculate_mape(actual, predicted):
        return (1 / len(actual)) * sum(abs((actual - predicted) / actual) * 100)

    t_minus_1_all = pred_8_hours.iloc[(len(pred_8_hours)-8):len(pred_8_hours)]

    t_minus_1_actual = t_minus_1_all[['valid_start','total_demand']]

    t_minus_1_pred = pd.DataFrame(t_minus_1_all.iloc[0,-10:-2]).reset_index(drop=True).rename(columns={25616 : "demand_prediction"})
    t_minus_1 = pd.concat([t_minus_1_actual.reset_index(drop=True), t_minus_1_pred], axis=1)

    mape = calculate_mape(t_minus_1['total_demand'],t_minus_1['demand_prediction'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Prediction Available till", "10/30/2023 00:00", "")
    col2.metric("Last Update", "10/23/2023 00:00", "10/22/2023 00:00",delta_color="off")
    #col3.metric("Accuracy", "86%")
    col3.metric("MAPE", str(round(mape,2))+"%")

    pred_8_hours_last_month=pred_8_hours[(pd.to_datetime(pred_8_hours['valid_start']).dt.year==2018) & (pd.to_datetime(pred_8_hours['valid_start']).dt.month>3)]
    line_graph3 = px.line(
        data_frame = pred_8_hours_last_month, title='Total Demand vs Predicted Hourly', 
        x='valid_start', y=['total_demand','demand_1_hour'],
        labels={
                "valid_start": "Date",
                "variable":""},
        color_discrete_sequence=['red', 'blue'])
    new = {"demand_1_hour": "Prediction","total_demand": "Total Demand"}
    line_graph3.for_each_trace(lambda t: t.update(name = new[t.name]))
    line_graph3.update_layout(width=1300,height=400)

    st.plotly_chart(line_graph3)
