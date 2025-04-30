from datetime import datetime,date,timedelta #FURTHER IMPLEMENTATION
import pandas as pd
from thelib import customer_classifier,figbar_sliding,hourscomparaison_sliding,driveratio_sliding

theTrueDict=pd.read_csv('data/Drive_Pilot_Low_High_Performers.csv',header='infer')                          #reading data from csv
theDict=theTrueDict.set_index('encoded_vin').T.to_dict('list')                                              #dictionary creation
theDict = {vin: values[0] for vin, values in theTrueDict.set_index('encoded_vin').T.to_dict('list').items()}
print(theDict.items())                                                                                      #verbose (content displayed for debugging)
print("Our test subject is: {}".format(theDict.get("BRAVO")))                                               #We will use bravo for PoC 3MONTH 21st to 21st

today_str = "2024-03-21"
today_obj= datetime.strptime(today_str, "%Y-%m-%d")

dailyusage = pd.read_csv('data/Drive_Pilot_Daily_Usage_Data.csv',header='infer',usecols=['day','vin','sum_duration_active_minutes'])
dailyusage['day'] = pd.to_datetime(dailyusage['day'])


df=pd.read_csv('data/Drive_Pilot_Usage_Data.csv',header='infer',usecols=['day','vin','Count_ACCEPTED','Count_REJECTED','sum_duration_active','sum_duration_available']) #reading some columns
df['day'] = pd.to_datetime(df['day'])
print(df.head())
weekago_obj = today_obj - timedelta(days=7)                                                                 #DATETIMEOBJECTS FOR CONDITIONS
monthago_obj = today_obj - timedelta(days=30)
threemonthago_obj = today_obj - timedelta(days=90)
fleet_week = df[(df['day'] >= weekago_obj)]                                                                 #DATAFRAMES FOR GENERAL COMPARAISON
fleet_month = df[(df['day'] >= monthago_obj)]
fleet_3month = df[(df['day'] >= threemonthago_obj)]

fleet_weekly_total = dailyusage[dailyusage['day'] >= weekago_obj]
fleet_monthly_total = dailyusage[dailyusage['day'] >= monthago_obj]                                         #THIS ONES GIVE THE TOTAL USAGE FROM THE OTHER CSV
fleet_3month_total = dailyusage[dailyusage['day'] >= threemonthago_obj]

fleetsize=22                                                                                                #ONLY 22 vehicles provided values


for encoded_vin in theDict.keys():
    vin = theDict.get(encoded_vin)
    print("Now processing: {}".format(encoded_vin))
    
    df_week = df[(df['day'] >= weekago_obj) & (df['vin'] == vin)]
    df_month = df[(df['day'] >= monthago_obj) & (df['vin'] == vin)]                                         #FILTERING FOR TIME PERIODS
    df_3month = df[(df['day'] >= threemonthago_obj) & (df['vin'] == vin)]
    df_totalhours = dailyusage[(dailyusage['vin'] == vin)]

    #GENERAL CALCULATIONS
    hourscomparaison_sliding(
        df_week['sum_duration_active'].sum() / 3600,
        df_month['sum_duration_active'].sum() / 3600,
        df_3month['sum_duration_active'].sum() / 3600,                                                      #SECONDS TO HOUR CONVERSION
        fleet_week['sum_duration_active'].sum() / 3600/fleetsize,
        fleet_month['sum_duration_active'].sum() / 3600/fleetsize,
        fleet_3month['sum_duration_active'].sum() / 3600/fleetsize,
        encoded_vin
    )
    driveratio_sliding(
        df_week['sum_duration_available'].sum() /60,
        df_week['sum_duration_active'].sum() /60,
        df_month['sum_duration_available'].sum() /60,
        df_month['sum_duration_active'].sum() /60,                                                          #MINUTES TO HOUR CONVERSION DUE TO DIFFERENT SCHEMA
        df_3month['sum_duration_available'].sum() /60,
        df_3month['sum_duration_active'].sum() /60,
        encoded_vin
    )
    #Python dictionary format for saving values for each representation
    ffunnel_tdh = {'week': fleet_weekly_total.filter(regex='sum_duration_active_minutes').sum().iloc[0]/fleetsize/60,
                  'month': fleet_monthly_total.filter(regex='sum_duration_active_minutes').sum().iloc[0]/fleetsize/60,
                  '3month': fleet_3month_total.filter(regex='sum_duration_active_minutes').sum().iloc[0]/fleetsize/60}
    ffunnel_tah = {'week': fleet_week['sum_duration_available'].sum()/fleetsize/3600,
                   'month': fleet_month['sum_duration_available'].sum()/fleetsize/3600,
                   '3month': fleet_3month['sum_duration_available'].sum()/fleetsize/3600}
    ffunnel_teh = {'week': fleet_week['sum_duration_active'].sum()/fleetsize/3600,
                   'month': fleet_month['sum_duration_active'].sum()/fleetsize/3600,
                   '3month': fleet_3month['sum_duration_active'].sum()/fleetsize/3600}
    fdrivepilot_enable_events = {'week': fleet_week['Count_ACCEPTED'].sum()/fleetsize,
                                 'month': fleet_month['Count_ACCEPTED'].sum()/fleetsize,
                                 '3month': fleet_3month['Count_ACCEPTED'].sum()/fleetsize}

    print("{} has driven {} hours total".format(encoded_vin,df_totalhours[(df_totalhours['day']>=weekago_obj)].filter(regex='sum_duration_active_minutes').iloc[0].sum()))


    funnel_tdh = {'week': df_totalhours[(df_totalhours['day']>=weekago_obj)].filter(regex='sum_duration_active_minutes').sum().iloc[0]/60,
                  'month': df_totalhours[(df_totalhours['day']>=monthago_obj)].filter(regex='sum_duration_active_minutes').sum().iloc[0]/60,                                                #TOTAL DRIVING HOURS
                  '3month': df_totalhours[(df_totalhours['day']>=threemonthago_obj)].filter(regex='sum_duration_active_minutes').sum().iloc[0]/60}
    funnel_tah = {'week': df_week['sum_duration_available'].sum()/3600, 'month': df_month['sum_duration_available'].sum()/3600, '3month': df_3month['sum_duration_available'].sum()/3600}   #TOTAL AVAILABLE HOURS
    funnel_teh = {'week': df_week['sum_duration_active'].sum()/3600, 'month': df_month['sum_duration_active'].sum()/3600, '3month': df_3month['sum_duration_active'].sum()/3600}            #TOTAL ENABLED HOURS
    drivepilot_enable_events = {'week': df_week['Count_ACCEPTED'].sum(), 'month': df_month['Count_ACCEPTED'].sum(), '3month': df_3month['Count_ACCEPTED'].sum()}                            #NUMBER OF EVENTS
    

    figbar_sliding(funnel_tdh,funnel_tah,funnel_teh,drivepilot_enable_events,ffunnel_tdh,ffunnel_tah,ffunnel_teh,fdrivepilot_enable_events,encoded_vin)                                     


    print("textgen for {} running!".format(encoded_vin))                                                    #TEXT GENERATION FOR CONTENT PERSONALISATION
    df_textgen = theTrueDict[(theTrueDict['vin']==vin)]
    f = open('./webserver/fleet/{}/genAI.txt'.format(encoded_vin),"w")
    f.write(
        "Based on the car records of the last months you are <strong><b>{}</b></strong> with an average usage per day of the autonomous driving feature of <strong><b>{:.0f} mins</b></strong> versus the fleet average of <strong><b>{:.0f} minutes</b></strong>.\n\n<strong>Your Benefit:</strong> use this time in your daily drives to check your emails, listen and concentrate on your preferred podcasts or videos, talk in calm with your colleagues or relatives, or if you want to have a little of passion... simply kiss your companion !!\n\nHere a dashboard of your Drive Pilot usage:".format(df_textgen['performance_category'].iloc[0],int(df_textgen['sum_duration_active_minutes'].iloc[0]/90),(dailyusage['sum_duration_active_minutes'].sum()/fleetsize/90) ))
    

    df_textgen = theTrueDict[(theTrueDict['vin']==vin)]
    f = open('./webserver/fleet/{}/feedback.txt'.format(encoded_vin),"w")
    f.write(
        "We need your opinion. We have been observing that <strong><b>{}</b></strong> use DrivePilot based on the trips of the last months. We truly appreciate your feedback and would like to know your opinion about our product.\n\nPlease tell us the main reasons from the one we have selected for you, or if you prefer it and it is more convenient for you, simply leave us an audio message with your opinion".format(customer_classifier(df_textgen['performance_category'].iloc[0])))

print("All done")