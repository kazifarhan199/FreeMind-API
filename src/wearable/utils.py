from . import models
from datetime import date

# saving raw daily data from garmin (can be used to refer back to, if need be)     
def save_garmin_daily_data_to_db(data):
    # Create or update the data in the database
    try:
        # Create or retrieve the instance from the db
        instance = models.GarminDailyData.objects.create(
                data=data
            )
        # save the instance
        instance.save()
    except Exception as e:
        # handle the exception
        print(f'Error saving data: {e}')    


# saving raw stress data from garmin (can be used to refer back to, if need be)
def save_garmin_stress_data_to_db(data):
    # Create or update the data in the database
    try:
        # Create or retrieve the instance from the db
        instance = models.GarminStressData.objects.create(
                data=data
            )
        # save the instance
        instance.save()
    except Exception as e:
        # handle the exception
        print(f'Error saving data: {e}')    

# saving raw sleep data from garmin (can be used to refer back to, if need be)
def save_garmin_sleep_data_to_db(data):
    # Create or update the data in the database
    try:
        # Create or retrieve the instance from the db
        instance = models.GarminSleepData.objects.create(
                data=data
            )
        # save the instance
        instance.save()
    except Exception as e:
        # handle the exception
        print(f'Error saving data: {e}')    


# saving daily data from garmin (just the columns needed instead of all the data)
def dataToDailies(data):
    
    try:
        # Create or retrieve the instance from the db
        #  data = {'dailies': [ {'userId': ... } { } { } ]} 
        today=date.today()
        dailiesList=data['dailies']
        print(dailiesList==None)
        print(dailiesList)
        for day in dailiesList:
            filter= models.DailyData.objects.filter(is_active=True, userId = day.get('userId'),userAccessToken=day.get('userAccessToken'),calendarDate=day.get('calendarDate'))
            if(filter.exists()):

                for i in filter:
                    i.is_active=False
                    i.save()
            #create a instance in the DB
            #print(str(today))
            #print(str(day.get('calendarDate')))
            #print(True if (str(today)==str(day.get('calendarDate'))) else False)
            instance = models.DailyData.objects.create(
                
                is_active= True if (str(today)==str(day.get('calendarDate'))) else False,
                userId = day.get('userId'),
                userAccessToken=day.get('userAccessToken'),
                summaryId=day.get('summaryId'),
                calendarDate=day.get('calendarDate'),
                activeKilocalories = day.get('activeKilocalories'),
                steps = day.get('steps'),

                durationInSeconds = day.get('durationInSeconds'),
                startTimeInSeconds = day.get('startTimeInSeconds'),
                startTimeOffsetInSeconds = day.get('startTimeOffsetInSeconds'),

                minHeartRateInBeatsPerMinute = day.get('minHeartRateInBeatsPerMinute'),
                maxHeartRateInBeatsPerMinute = day.get('maxHeartRateInBeatsPerMinute'),
                averageHeartRateInBeatsPerMinute = day.get('averageHeartRateInBeatsPerMinute'),
                restingHeartRateInBeatsPerMinute = day.get('restingHeartRateInBeatsPerMinute'),

                maxStressLevel = day.get('maxStressLevel'),
                activityStressDurationInSeconds = day.get('activityStressDurationInSeconds'),
                lowStressDurationInSeconds = day.get('lowStressDurationInSeconds'),
                mediumStressDurationInSeconds = day.get('mediumStressDurationInSeconds'),
                highStressDurationInSeconds = day.get('highStressDurationInSeconds'),
                stressQualifier = day.get('stressQualifier'),
            )
            # save the instance
            instance.save()
            # before calling the function what if both sleep and daily have new data at the same time
            # how will that be handled
            
        #this block will filter the latest data of the user in question and makes a call to the analysis function

        # Alternative
        # models.DailyData.objects.filter(userId = day.get('userId'),userAccessToken=day.get('userAccessToken'),calendarDate=day.get('calendarDate')).order_by('-id').last()
        
        filter= models.DailyData.objects.filter(is_active=True, userId = day.get('userId'),userAccessToken=day.get('userAccessToken'),calendarDate=day.get('calendarDate'))
        if(filter.exists()):
            for curr_obj in filter:
                dataAnalysis(curr_obj, _type='daily')
            
            
    except Exception as e:
        # handle the exception
        print(f'Error saving data: {e}') 

# saving sleep data from garmin (just the columns needed instead of all the data)
def dataToSleep(data):
    
    try:
        sleepList=data['sleeps']
        today=date.today()
        for sleep in sleepList:
            filter= models.SleepData.objects.filter(is_active=True, userId = sleep.get('userId'),userAccessToken=sleep.get('userAccessToken'),calendarDate=sleep.get('calendarDate'))
            if(filter.exists()):

                for i in filter:
                    i.is_active=False
                    i.save()
            # Create a instance in the db
            instance = models.SleepData.objects.create( 
                is_active= True if (str(today)==str(day.get('calendarDate'))) else False,              
                userId = sleep.get('userId'),
                userAccessToken=sleep.get('userAccessToken'),
                summaryId=sleep.get('summaryId'),
                calendarDate=sleep.get('calendarDate'),
                durationInSeconds=sleep.get('durationInSeconds'),
                overallSleepScorevalue=sleep.get('overallSleepScore').get('value'),
                overallSleepScorequalifierKey=sleep.get('overallSleepScore').get('qualifierKey'),
            )
            # save the instance
            instance.save()
            # before calling the function what if both sleep and daily have new data at the same time
            # how will that be handled
            
    except Exception as e:
        # handle the exception
        print(f'Error saving data: {e}') 

# the function Does the data analysis before trying to alter the recommendation list

#return multiplicity 
    #1 if activity is in range
    #0.1-0.9: maybe 0.7: if activity level is already high you don't want to suggest the user to do more of the activity
    #1.1-1.9: maybe 1.3: if activity level is low you want to suggest the user to do more of the activity
def dataAnalysisDaily(curr_obj_data): 
    reason = "Based on your available activity data, "
    dict_ActivityMultiplicity ={ 'exercise':None, 'food':None, 'stress':None, 'general':1, 'sleep':None}

    # logic to do the Analysis

    
    #STEPS and CALORIES Analysis
    if((curr_obj_data.steps==None or curr_obj_data.steps==0) and (curr_obj_data.activeKilocalories==0 or curr_obj_data.activeKilocalories==None)):
        reason = reason + "it appears that your calorie intake and step count have not been measured. To gain a more comprehensive understanding of your activity and nutrition, it is recommended that you track these metrics consistently. "
    else:
        if(curr_obj_data.activeKilocalories >= 300 or (curr_obj_data.steps>= 2000 and curr_obj_data.steps<=5000)):
            dict_ActivityMultiplicity['exercise']=0.9
            dict_ActivityMultiplicity['food']=1.1
            #print(curr_obj_data.activeKilocalories, curr_obj_data.steps)
            reason = reason + "it appears that you have engaged in a sufficient amount of exercise for the day. It is recommended that you now focus on consuming a well-balanced and nutritious diet to support your physical activity and overall health. "
        elif(curr_obj_data.activeKilocalories >= 500 or curr_obj_data.steps> 5000 ):
            dict_ActivityMultiplicity['exercise']=0.7
            dict_ActivityMultiplicity['food']=1.3
            #print(curr_obj_data.activeKilocalories, curr_obj_data.steps)
            reason = reason + "it appears that you have engaged in high levels of exercise. To fully reap the benefits of your exercise, it is recommended that you consume a well-balanced and nutritious diet. Adequate nutrition can help support your physical activity and overall health. "
        else:
            dict_ActivityMultiplicity['exercise']=1.3
            dict_ActivityMultiplicity['food']=0.9
            print(curr_obj_data.activeKilocalories, curr_obj_data.steps)
            reason = reason + "it appears that you have not engaged in a substantial amount of physical activity today. It is recommended that you consider incorporating more physical activity into your daily routine for optimal health and well-being. "

    # STRESS Analysis 
    dictStressQualifiers = {'stressfull':1.3, 'unknown':1, 'balanced': 1} 
    if(curr_obj_data.stressQualifier == "unknown"):
        reason = reason + "Also, your stress levels have not been measured. Tracking your stress levels can provide valuable insights into your overall well-being and can help inform potential lifestyle adjustments. It is recommended that you consider incorporating stress tracking into your routine. "
    else:
        reason = reason + "Your stress level is analysed as " + curr_obj_data.stressQualifier + ". "
    dict_ActivityMultiplicity['stress']=dictStressQualifiers[curr_obj_data.stressQualifier]

    return dict_ActivityMultiplicity, reason



def dataAnalysisSleep(curr_obj_data):
    filter= models.SleepData.objects.filter(is_active=True, userId = curr_obj_data.userId,userAccessToken=curr_obj_data.userAccessToken,calendarDate=curr_obj_data.calendarDate)
    reason = ""
    sleep=1
    if(filter.exists()):
        if(filter.first().durationInSeconds >= 25200):
            if(filter.first().overallSleepScorequalifierKey != "unknown"):
                reason = reason + "You had enough sleep and the quality of sleep is " +  filter.first().overallSleepScorequalifierKey + ". "
                sleep= 1.5
            else:
                reason = reason + "You had enough sleep. "
                sleep=1
        else:
            reason = reason + "Also you should take rest as you had less than 7 hours of sleep. "
            sleep=2
    else:
        reason = reason + "Sleep is not measured. "
        sleep=1
    
    return sleep, reason


#think about how to return the reason?
# the analysis function is called only when there is new data in the table, this is made sure by making th call analysis in dataToSleep/dataToDaily after a new instance is saved.    
# what are the five activity types? exercise, food, stress and general

def dataAnalysis(curr_obj_data, _type):
    if(_type=='daily'):
        dict, reason = dataAnalysisDaily(curr_obj_data)
        sleep, sleepreason = dataAnalysisSleep(curr_obj_data)
        reason = reason + sleepreason
        dict['sleep']=sleep
        print(reason, dict.keys(), dict.values())
    #communicate to recommendation system
    
    # create 1-5/0.1-1.9 scale for each activity and then increase or decrease the multiplicty of the type accordingly
    # Analyse the current day's data to come up with a activity type to increse/decrease the prominance



# Set the schedule for the task to run every 2 hours
# app.conf.beat_schedule = {
#     'collect_garmin_data': {
#         'task': 'your_project_name.tasks.collect_garmin_data',
#         'schedule': timedelta(hours=2),
#     },
# }