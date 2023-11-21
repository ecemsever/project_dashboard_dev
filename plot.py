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
pred_8_hours['Month'] = pd.to_datetime(pred_8_hours['valid_start']).dt.month


pred_8_hours[['Month']]=pred_8_hours[['Month']].astype(str).apply(lambda x: x.str.zfill(2))


pred_8_hours['Year/Month'] = pred_8_hours['Year'].astype(str) + '/' + pred_8_hours.Month.astype(str)
#pred_8_hours['Year/Month'] = construct_path(pred_8_hours['Year'].astype(str),pred_8_hours['Month'].astype(str))
pred_8_hours=pred_8_hours.rename(columns={"valid_start": "Date"})


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
    with d1:
        option = st.selectbox(
        'Please select a time granularity',
        ('Hourly', 'Daily', 'Monthly'))

    end_date=max(pred_8_hours_daily["Day"])
    ed=d2.date_input("Select a end date",end_date)
    
    if option=='Daily' :
        line_graph = px.line(
            data_frame = pred_8_hours_daily[pred_8_hours_daily["Day"].between(sd, ed)], title='Total Demand Daily', 
            x='Day', y='Total Demand')
        line_graph.update_layout(width=1300,height=600)
        st.plotly_chart(line_graph)
    elif option == 'Hourly':
        # Create the line graph for hourly
        line_graph2 = px.line(
            data_frame = pred_8_hours[pred_8_hours["Day"].between(sd, ed)], title='Total Demand Hourly', 
            x='Day', y='total_demand',
            hover_data=["Date"]
            )
        line_graph2.update_layout(width=1300,height=600)
        st.plotly_chart(line_graph2)
    else:
        pred_8_hours_monthly = pred_8_hours[pred_8_hours["Day"].between(sd, ed)].groupby(['Year/Month'])['total_demand'].agg('sum').reset_index(name='Total Demand')

        line_graph3 = px.line(
            data_frame = pred_8_hours_monthly, title='Total Demand Monthly', 
            x='Year/Month', y='Total Demand')
        line_graph3.update_layout(width=1300,height=600)
        st.plotly_chart(line_graph3)

with tab2:
    def calculate_mape(actual, predicted):
        return (1 / len(actual)) * sum(abs((actual - predicted) / actual) * 100)

    t_minus_1_all = pred_8_hours.iloc[(len(pred_8_hours)-9):len(pred_8_hours)]
    t_minus_1_actual = t_minus_1_all[['Date','total_demand']].iloc[0:8]
    t_minus_1_pred = pd.DataFrame(t_minus_1_all.iloc[0,6:14]).reset_index(drop=True).rename(columns={25615 : "demand_prediction"})
    
    #st.text(len(t_minus_1_all))
    #st.table(t_minus_1_all)
    #st.table(t_minus_1_actual)
    #st.table(t_minus_1_pred)

    t_minus_1 = pd.concat([t_minus_1_actual.reset_index(drop=True), t_minus_1_pred.reset_index(drop=True)], axis=1)
    t_minus_1 = pd.DataFrame(t_minus_1)

    mape = calculate_mape(t_minus_1['total_demand'],t_minus_1['demand_prediction'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Prediction Available till", str(pd.to_datetime(pred_8_hours['Date'].iloc[-1]) + pd.Timedelta(hours=8)), "")
    col2.metric("Last Update", "11/21/2023 00:00", "",delta_color="off")
    #col3.metric("Accuracy", "86%")
    col3.metric("MAPE", str(round(mape,2))+"%")

    #st.text(pd.to_datetime(max(t_minus_1['Date'])) + pd.Timedelta(hours=8))
    #st.text(pd.to_datetime(max(t_minus_1['Date'])))
   

    #pred_8_hours_last_month = pred_8_hours[(pd.to_datetime(pred_8_hours['Date']).dt.year==2018) & (pd.to_datetime(pred_8_hours['Date']).dt.month>3)]
    latest_pred= pd.DataFrame(pred_8_hours.iloc[-1,6:14]).reset_index(drop=True).rename(columns={25615 : "demand_prediction"})
    latest_pred_date = pred_8_hours['Date'].iloc[-1]

    pred_dates=pd.date_range(start=(pd.to_datetime(latest_pred_date)), end=(pd.to_datetime(latest_pred_date) + pd.Timedelta(hours=7)),freq='H')
    pred_w_dates = pd.concat([latest_pred.reset_index(drop=True), pd.DataFrame(pred_dates).reset_index(drop=True)], axis=1).rename(columns={0 : "Date", 25623 : "Prediction"})


    t_minus_1['demand_prediction'] = t_minus_1['demand_prediction'].astype(float)

    line_graph0 = px.line(
        data_frame = t_minus_1, title='Total Demand vs Predicted Hourly', 
        x='Date', y=['total_demand','demand_prediction'],
        hover_data=["Date"],
        labels={"valid_start": "Date","variable":""},
        color_discrete_sequence=['red', 'blue']
        )
    new = {"demand_prediction": "Prediction","total_demand": "Total Demand"}
    line_graph0.for_each_trace(lambda t: t.update(name = new[t.name]))
    line_graph0.update_layout(width=1300,height=400)
    #line_graph0.update_xaxes(dtick=86400000.0)
    st.plotly_chart(line_graph0)


    line_graph_pred = px.line(
        data_frame = pred_w_dates, title='Predicted Hourly', 
        x='Date', y='Prediction',
        )
    line_graph_pred.update_layout(width=1300,height=400)

    st.plotly_chart(line_graph_pred)