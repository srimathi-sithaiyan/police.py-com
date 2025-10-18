import pymysql
import streamlit as st
import pandas as pd

#connect to mysql
def create_connection():
    try:
        connection = pymysql.connect(
             host = "localhost",
             user = "root", 
             password = "root",
             database ="police_log",
             cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        st.error(f"Database connection Error: {e}")
        return None
    
    
# Fetch the data
def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                police_ledger = pd.DataFrame(result)
                return police_ledger
        finally:
            connection.close()
    else:
        return pd.DataFrame()
    
    
# Steamlit
import streamlit as st
st.set_page_config(page_title="Police Data Dashboard", layout="wide")

st.title("Filter Police Log Data")
st.markdown("Police Digital Ledger")

import pandas as pd

#show the tables 
import streamlit as st
st.header("police incident ledger overview")
query = "Select * from police_check"
data= fetch_data(query)
st.dataframe(data, use_container_width=True)
  

#metrix
st.header("Metrix View")


col1, col2, col3 = st.columns(3)

with col1:
    vehicle_numbers = data.shape[0]
    st.metric("Total_vehicle_numbers",vehicle_numbers)

with col2:
    Violation = data[data['stop_outcome'].str.contains("violation", case=False,na=False)].shape[0]
    st.metric("Total_Violation",Violation)

with col3:
    reports = data[data['stop_outcome'].str.contains("reports", case=False,na=False)].shape[0]
    st.metric("Office_reports",reports)  

# Queries
st.header("Information Insights") 

selected_query = st.selectbox("Select a query to Run",[
    "Drug_related stops top10 vehicle_Number",
    "Frequently searched vehicles",
    "Highest arrest rate driver_age",
    "Which gender drivers stopped in countries",
    "Highest search in race and gender combination",
    "Which time most traffic_stops",
    "Average stop duration for different violations",
    "During the night time to lead arrest",
    "Violation associated with arrests",
    "Violation with younger drivers(<25)",
    "violation with search or arrest",
    "Which countries involved highest drug_related stops",
    "Arrest rate by country and violation",
    "Which country stops with search conducted",
    "Breakdowns of stops and Arrest by country",
    "Driver violation based on age and race",
    "Time period analysis of stops",
    "Violation with search and arrest",
    "Driver Demographics by country",
    "Top5 violations with highest arrest rate"
])

query_map = {
      "Drug_related stops top10 vehicle_Number": "SELECT vehicle_number, COUNT(*) AS drug_stop_count FROM police_ledger WHERE drug_related = True group By vehicle_number Order BY drug_stop_count DESC LIMIT 10",
      "Frequently searched vehicles": "SELECT vehicle_number, COUNT(*) AS search_count FROM police_ledger WHERE search_conducted = True GROUP BY vehicle_number ORDER BY search_count DESC",
      "Highest arrest rate driver_age": "SELECT driver_age, COUNT(*) total_stops SUM(is_arrested) AS total_arrests SUM(is_arrested)*1.0/ COUNT(*) AS arrest_rate FROM police_ledger GROUP BY driver_age ORDER BY arrest_rate DESC LIMIT 1",
      "Which gender drivers stopped in countries":"SELECT  country_name, driver_gender, COUNT(*) AS stop_count FROM police_ledger GROUP BY country_name, driver_gender ORDER BY country_name, stops_count DESC",
      "Highest search in race and gender combination":"SELECT driver_race, driver_gender, COUNT(*) AS search_count FROM police_ledger WHERE search_conducted = True GROUP BY driver_race, driver_gender ORDER BY search_count DESC LIMIT 1",
      "Which time most traffic_stops":"SELECT stop_time, COUNT(*) AS stop_count FROM police_ledger GROUP BY stop_time ORDER BY stop_count DESC LIMIT 1",
      "Average stop duration for different violations":"SELECT violation, AVG (stop_duration) AS avg_stop_duration FROM police_ledger GROUP BY violation ORDER BY avg_stop_duration DESC",
      "During the night time to lead arrest":"SELECT* FROM police_ledger WHERE is_arrested = True AND(stop_time >= '00:20:00' OR stop_time <'00:06:00')",
      "Violation associated with arrests":"SELECT violation, COUNT(*) AS arrest_count FROM police_ledger WHERE is_arrested = True GROUP BY violation ORDER BY arrest_count DESC",
      "Violation with younger drivers(<25)":"SELECT violation, COUNT(*)AS violation_count FROM police_ledger WHERE driver_age<25 GROUP BY violation ORDER BY violation_count DESC",
      "violation with search or arrest":"SELECT violation, COUNT(*)AS count_events FROM police_ledger WHERE search_conducted = True OR is_arrested = True GROUP BY violation ORDER BY count_events DESC",
      "Which countries involved highest drug_related stops":"SELECT country_name, COUNT(*)AS drug_stop_count FROM police_ledger WHERE drug_related = True GROUP BY country_name ORDER BY drug_stop_count DESC LIMIT1",
      "Arrest rate by country and violation":"SELECT country_name, violation, SUM(CASH WHEN is arrestd = True THEN 1 ELSE 0 END)* 1.0/ COUNT(*) AS arrest_rate FROM police_ledger GROUB BY country_name, violation ORDER BY arrest_rate DESC",
      "Which country stops with search conducted":"SELECT country_name, COUNT(*) AS search_count FROM police_ledger WHERE search_conducted = True GROUP BY country_name ORDER BY search_count DESC",
      "Breakdowns of stops and Arrest by country":"SELECT country_name, COUNT(*) AS total_stops, SUM(CASH WHEN is_arrested = True THEN 1 ELSE 0 END) AS total_arrests FROM police_ledger GROUP BY country_name ORDER BY total_stops DESC",
      "Driver violation based on age and race":"SELECT driver_age, driver_race,violation, COUNT(*) AS violation_count FROM police_ledger GROUP BY driver_age, driver_race, violation ORDER BY driver_age, driver_race, violation_count DESC",
      "Time period analysis of stops":"SELECT SUBSTRING(stop_time,1,2) AS stop_hour, COUNT(*) AS stop_count FROM police_ledger GROUP BY stop_hour ORDER BY stop_hour",
      "Violation with search and arrest":"SELECT violation, COUNT(*) AS event_count FROM police_ledger WHERE search_conducted = True OR is_arrested = True GROUP BY violation ORDER BY event_count DESC",
      "Driver Demographics by country":"SELECT country_name, driver_gender, driver_race, AVG(driver_age) AS avg_age, COUNT(*) AS total_stops FROM police_ledger GROUP BY country_name, driver_gender, driver_race ORDER BY country_name, total_stops DESC",
      "Top5 violations with highest arrest rate":"SELECT violation, SUM(CASH WHEN is_arrested = True THEN 1 ELSE 0 END) * 1.0/ COUNT(*) AS arrest_rate, COUNT(*) AS total_stops FROM police_ledger GROUP BY violation ORDER BY arrest_rate DESC LIMIT 5"
}

if st.button("Run Query"):
    result = fetch_data(query_map[selected_query])
    if not result.empty:
        st.write(result)
    else: 
        st.warning("No results found for the selected query.")

st.header("Add New Police Ledger & Predict Outcome and Violation")   


# Inputs & Outputs
with st.form("new_ledger_form"):
    stop_date = st.date_input("Stop_Date")
    stop_time = st.time_input("Stop_Time")
    country_name = st.text_input("Country_Name")
    driver_gender = st.selectbox("Driver_Gender",["male","female"])
    driver_age = st.number_input("Driver_Age", min_value=16, max_value=100, value=27)
    driver_race = st.text_input("Driver_Race")
    search_conducted = st.selectbox("Was a search conducted?", ["0","1"])
    search_type = st.text-input("Search_Type")
    drug_related_stop = st.selectbox("Was it Drug Related?", ["0","1"])
    stop_duration = st.selectbox("Stop_Duration",data['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("Vehicle_Number")
    

    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

    if  submitted:
        # Filter data for prediction
        filtered_data = data[
            (data['driver_gender'] == driver_gender) &
            (data['driver_age'] == driver_age) &
            (data['search_conducted'] == int(search_conducted)) &
            (data['stop_duration'] == stop_duration) &
            (data['drugs_related_stop'] == int(drugs_related_stop))
        ]

        #Output
        if not filtered_data.empty:
            predicted_outcome = filtered_data['stop_outcome'].mode()[0]
            predicted_violation = filtered_data['violation'].mode()[0]
        else:
            predicted_outcome = "warning"
            predicted_violation = "speeding"

        # Summary
        search_text = "A search was conducted" if int(search_conducted) else "No search was conducted" 
        drug_text = "was drug related" if int(drugs_related_stop) else "was not drug related"

        st.markdown("""
        Prediction Summary

        predicted violation: {predicted_violation}
        predicted stop outcome: {predicted_outcome}  

        A {driver_age}-year_old {driver_gender} driver in {country_name} was stopped at {stop_time.strftime('%I:%M %P')} on {stop_date},
        {search_text}, and the stop {drug_text}.
        stop duration: {stop_duration}.
        Vehicle Number: {vehicle_number}.
        """)                                                                       
            









      
   

            

      




   




       
            
      
      

                
   


    


 

    

    
   
   






    


    
