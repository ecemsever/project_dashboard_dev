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

with st.sidebar:
    aemo = Image.open(dir+'/aemo.png')
    st.image(aemo)
    st.markdown("Our project mission is seamless power grid system management with efficient resource allocation achieved by data driven operation, maintenance & planning")

st.markdown("""## Energy Analytics for Victoria, Australia by PowerRangers""")

def history():
    history_data = pd.read_csv(dir+'/1_weeks_to_8_hours_pred.csv')
    #history_data = pd.read_csv(dir+'/8_hour_predictions.csv.csv')    
    date_col = 'timestamp'
    # Construct date granularity features for past data
    history_data['Day'] = pd.to_datetime(history_data[date_col]).dt.date
    history_data['Year'] = pd.to_datetime(history_data[date_col]).dt.year
    history_data['Month'] = pd.to_datetime(history_data[date_col]).dt.month
    history_data['Week'] = pd.to_datetime(history_data[date_col]).dt.strftime('%W')
    history_data[['Month']]=history_data[['Month']].astype(str).apply(lambda x: x.str.zfill(2))
    history_data[['Week']]=history_data[['Week']].astype(str).apply(lambda x: x.str.zfill(2))
    history_data['Year/Month'] = history_data['Year'].astype(str) + '/' + history_data.Month.astype(str)
    history_data['Year/Week'] = history_data['Year'].astype(str) + '/' + history_data.Week.astype(str)
    history_data = history_data.rename(columns={"timestamp": "Date"})
    return history_data

def data_8_hours():
    #pred_8_hours = pd.read_csv(dir+'/1_weeks_to_8_hours_pred.csv')
    pred_8_hours = pd.read_csv(dir+'/8_hour_predictions.csv')    
    #pred_8_hours = pred_8_hours.rename(columns={"valid_start": "Date"})
    pred_8_hours=pred_8_hours.rename(columns={"timestamp": "Date"})

    return pred_8_hours

def data_168_hours():
    #pred_168_hours = pd.read_csv(dir+'/4_weeks_to_1_weeks_pred.csv')
    pred_168_hours = pd.read_csv(dir+'/168_hour_predictions.csv')    
    #pred_168_hours=pred_168_hours.rename(columns={"valid_start": "Date"})
    pred_168_hours=pred_168_hours.rename(columns={"timestamp": "Date"})
    return pred_168_hours

history_data = history()
pred_8_hours = data_8_hours()
pred_168_hours = data_168_hours()

# Mape calculation function
def calculate_mape(actual, predicted):
    return (1 / len(actual)) * sum(abs((actual - predicted) / actual) * 100)

# Function for converting to csv for download
def convert_df(df):
    return df.to_csv().encode('utf-8')


# Name the tabs
tab1, tab2, tab3, tab4 = st.tabs(["🌍 Historical Analytics", "📈 Shift Based Predictive Analytics", "📊 Weekly Predictive Analytics", "📬 Contact Us"])

with tab1:
    
    history_data_daily = history_data.groupby(['Day'])['total_demand'].agg('sum').reset_index(name='Total Demand')


    d1, d2 = st.columns(2)
    #Default start date is the minimum date in the data
    start_date = min(history_data_daily["Day"])
    
    #Start Date filter
    sd = d1.date_input("📆 Select a starting date",start_date)

    #Default end date is the maximum date in the data
    end_date=max(history_data_daily["Day"])

    # End date filter
    ed=d2.date_input("📆 Select a end date",end_date)

    # Time granularity selectbox. 
    with d1:
        option = st.selectbox(
        'Please select a time granularity',
        ('Hourly', 'Daily', 'Weekly','Monthly'))

    # Depending on the selection, graph is updated
    if option=='Daily' :
        line_graph = px.line(
            data_frame = history_data_daily[history_data_daily["Day"].between(sd, ed)], title='Total Demand Daily', 
            x='Day', y='Total Demand')
        st.plotly_chart(line_graph,use_container_width = True)
        
    elif option == 'Hourly':
        # Create the line graph for hourly
        line_graph2 = px.line(
            data_frame = history_data[history_data["Day"].between(sd, ed)], title='Total Demand Hourly', 
            x='Day', y='total_demand',
            hover_data = ["Date"]
            )
        st.plotly_chart(line_graph2,use_container_width = True)
        
    elif option == 'Weekly' :
        pred_8_hours_weekly = history_data[history_data["Day"].between(sd, ed)].groupby(['Year/Week'])['total_demand'].agg('sum').reset_index(name='Total Demand')
        
        # Create the line graph for weekly
        line_graph4 = px.line(
             data_frame = pred_8_hours_weekly, title='Total Demand Weekly', 
             x='Year/Week', y='Total Demand')
        st.plotly_chart(line_graph4,use_container_width = True)

    else:
        pred_8_hours_monthly = history_data[history_data["Day"].between(sd, ed)].groupby(['Year/Month'])['total_demand'].agg('sum').reset_index(name='Total Demand')

        # Create the line graph for monthly
        line_graph3 = px.line(
            data_frame = pred_8_hours_monthly, title='Total Demand Monthly', 
            x='Year/Month', y='Total Demand')
        st.plotly_chart(line_graph3,use_container_width = True)


with tab2:

    # Processing prediction data to prepare it for the mape calculation
    # Get the latest 8 values in the data and flatten 8 predictions that corresponds to that actual values
    def t_minus_1_data_process_8hours(): 
        # get latest 8 values
        t_minus_1_all = pred_8_hours.iloc[(len(pred_8_hours)-9):len(pred_8_hours)]
        # hold actual values in one dataframe
        t_minus_1_actual = t_minus_1_all[['Date','total_demand']].iloc[0:8]
        # flatten 8 predictions that corresponds to that actual values 
        t_minus_1_pred = pd.DataFrame(t_minus_1_all.iloc[0,2:10]).reset_index(drop=True)
        t_minus_1_pred = t_minus_1_pred.rename(columns={t_minus_1_pred.columns[-1] : "demand_prediction"})
        # merge actual and predicted values
        t_minus_1 = pd.concat([t_minus_1_actual.reset_index(drop=True), t_minus_1_pred.reset_index(drop=True)], axis=1)
        t_minus_1 = pd.DataFrame(t_minus_1)
        t_minus_1['demand_prediction'] = t_minus_1['demand_prediction'].astype(float)

        return t_minus_1
    
    # Preparing data for the prediction plot
    def pred_data_process_8hours():
        latest_pred = pd.DataFrame(pred_8_hours.iloc[-1,2:10]).reset_index(drop=True)
        latest_pred = latest_pred.rename(columns={latest_pred.columns[-1] : "demand_prediction"})
        latest_pred_date = pred_8_hours['Date'].iloc[-1]
        pred_dates = pd.date_range(start=(pd.to_datetime(latest_pred_date)), end=(pd.to_datetime(latest_pred_date) + pd.Timedelta(hours=7)),freq='H')
        pred_w_dates = pd.concat([latest_pred.reset_index(drop=True), pd.DataFrame(pred_dates).reset_index(drop=True)], axis=1).rename(columns={0 : "Date", "demand_prediction" : "Prediction"})

        return pred_w_dates
    
    t_minus_1= t_minus_1_data_process_8hours()
    pred_w_dates = pred_data_process_8hours()

    # Download predictions
    csv = convert_df(pred_w_dates)
    st.download_button(
        label="Download Predictions as CSV",
        data=csv,
        file_name='predictions_8hours.csv',
        mime='text/csv',
    )

    if st.button('Update the Data', type="primary"):
        pred_8_hours = data_8_hours()
        t_minus_1= t_minus_1_data_process_8hours()
        pred_w_dates = pred_data_process_8hours()

    mape = calculate_mape(t_minus_1['total_demand'],t_minus_1['demand_prediction'])

    # Publishing the first row
    col1, col2, col3 = st.columns(3)
    col1.metric("Prediction Available till", str(pd.to_datetime(pred_8_hours['Date'].iloc[-1]) + pd.Timedelta(hours=8)), "")
    col2.metric("Last Update", str(pd.Timestamp.today().strftime('%Y-%m-%d')) , "", delta_color="off")
    col3.metric("MAPE", str(round(mape,2))+"%")

    # Actual vs Prediction Graph
    line_graph0 = px.line(
        data_frame = t_minus_1, title = 'Actual vs Predicted Hourly Demand for the last 8-hour period', 
        x='Date', y = ['total_demand','demand_prediction'],
        hover_data = ["Date"],
        labels = {"timestamp": "Date","variable":""},
        color_discrete_sequence = ['red', 'blue']
        )
    new = {"demand_prediction": "Prediction","total_demand": "Actual Demand"}
    line_graph0.for_each_trace(lambda t: t.update(name = new[t.name]))
    line_graph0.update_layout(yaxis=dict(range = [6000, max(t_minus_1['total_demand']*1.3)]))
    st.plotly_chart(line_graph0,use_container_width = True)
  
    # Prediction Graph for the next 8 hours
    line_graph_pred = px.line(
        data_frame = pred_w_dates, title='Next 8 hours Hourly Predictions', 
        x='Date', y='Prediction',
        )
    line_graph_pred.update_layout(yaxis=dict(range=[6000, max(pred_w_dates['Prediction']*1.3)]))
    st.plotly_chart(line_graph_pred,use_container_width = True)

with tab3:
    
    # Processing prediction data to prepare it for the mape calculation
    t_minus_1_168hours_all = pred_168_hours.iloc[(len(pred_168_hours)-169):len(pred_168_hours)]
    t_minus_1_168hours_actual = t_minus_1_168hours_all[['Date','total_demand']].iloc[1:169]
    t_minus_1_168hours_pred = pd.DataFrame(t_minus_1_168hours_all.iloc[0,2:170]).reset_index(drop=True)
    t_minus_1_168hours_pred = t_minus_1_168hours_pred.rename(columns={t_minus_1_168hours_pred.columns[-1] : "demand_prediction"})
    
    t_minus_1_168hours = pd.concat([t_minus_1_168hours_actual.reset_index(drop=True), t_minus_1_168hours_pred.reset_index(drop=True)], axis=1)
    t_minus_1_168hours = pd.DataFrame(t_minus_1_168hours)

    mape = calculate_mape(t_minus_1_168hours['total_demand'],t_minus_1_168hours['demand_prediction'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Prediction Available till", str(pd.to_datetime(pred_168_hours['Date'].iloc[-1]) + pd.Timedelta(hours=168)), "")
    col2.metric("Last Update", str(pd.Timestamp.today().strftime('%Y-%m-%d')), "",delta_color="off")
    col3.metric("MAPE", str(round(mape,2))+"%")
    
    t_minus_1_168hours['demand_prediction'] = t_minus_1_168hours['demand_prediction'].astype(float)

    # Prepare data for prediction plot
    latest_pred_168hours= pd.DataFrame(pred_168_hours.iloc[-1,2:170]).reset_index(drop=True)
    latest_pred_168hours = latest_pred_168hours.rename(columns={latest_pred_168hours.columns[-1] : "demand_prediction"})

    latest_pred_168hours_date = pred_168_hours['Date'].iloc[-1]

    pred_dates_168hours=pd.date_range(start=(pd.to_datetime(latest_pred_168hours_date)), end=(pd.to_datetime(latest_pred_168hours_date) + pd.Timedelta(hours=167)),freq='H')
    pred_w_dates_168hours = pd.concat([latest_pred_168hours.reset_index(drop=True), pd.DataFrame(pred_dates_168hours).reset_index(drop=True)], axis=1).rename(columns={0 : "Date", "demand_prediction" : "Prediction"})

    csv = convert_df(pred_w_dates_168hours)
    st.download_button(
        label="Download Predictions as CSV",
        data=csv,
        file_name='predictions_168hours.csv',
        mime='text/csv',
    )
    
    # Actual vs Prediction Graph
    line_graph168 = px.line(
        data_frame = t_minus_1_168hours, title='Actual vs Predicted Hourly Demand for the last 168-hour period', 
        x='Date', y=['total_demand','demand_prediction'],
        hover_data=["Date"],
        labels={"timestamp": "Date","variable":""},
        color_discrete_sequence=['red', 'blue']
        )
    new = {"demand_prediction": "Prediction","total_demand": "Actual Demand"}
    line_graph168.for_each_trace(lambda t: t.update(name = new[t.name]))
    st.plotly_chart(line_graph168,use_container_width = True)


    # Prediction Graph for the next 168 hours
    line_graph_pred168 = px.line(
        data_frame = pred_w_dates_168hours, title='Next 168 hours Hourly Predictions', 
        x='Date', y='Prediction',
        )
    st.plotly_chart(line_graph_pred168,use_container_width = True)

with tab4:
    st.balloons()
    #st.info('Ecem Savaş', icon="🚨")
    #st.link_button("Ecem Savaş", "https://www.linkedin.com/in/ecemsever-bilkent/")
    #st.snow()



