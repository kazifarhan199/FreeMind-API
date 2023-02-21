from . import models

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
        dailiesList=data['dailies']
        for day in dailiesList:
            filter= models.DailyData.objects.filter(is_active=True, userId = day.get('userId'),userAccessToken=day.get('userAccessToken'),calendarDate=day.get('calendarDate'))
            if(filter.exists()):

                for i in filter:
                    i.is_active=False
                    i.save()
            #create a instance in the DB
            instance = models.DailyData.objects.create(
                
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
        for sleep in sleepList:
            filter= models.SleepData.objects.filter(is_active=True, userId = sleep.get('userId'),userAccessToken=sleep.get('userAccessToken'),calendarDate=sleep.get('calendarDate'))
            if(filter.exists()):

                for i in filter:
                    i.is_active=False
                    i.save()
            # Create a instance in the db
            instance = models.SleepData.objects.create(               
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
    reason = ""
    dict_ActivityMultiplicity ={ 'exercise':None, 'food':None, 'stress':None, 'general':1, 'sleep':None}

    # logic to do the Analysis

    
    #STEPS and CALORIES Analysis
    if((curr_obj_data.steps==None or curr_obj_data.steps==0) and (curr_obj_data.activeKilocalories==0 or curr_obj_data.activeKilocalories==None)):
        reason = reason + "Your calories and steps have not been measured. "
    else:
        if(curr_obj_data.activeKilocalories >= 300 or (curr_obj_data.steps>= 2000 and curr_obj_data.steps<=5000)):
            dict_ActivityMultiplicity['exercise']=0.9
            dict_ActivityMultiplicity['food']=1.1
            reason = reason + "You have done enough exercise for the day, consume nutritous food. "
        elif(curr_obj_data.activeKilocalories >= 500 or curr_obj_data.steps> 5000 ):
            dict_ActivityMultiplicity['exercise']=0.7
            dict_ActivityMultiplicity['food']=1.3
            reason = reason + "You have perfored high levels of exercise, consume nutriouse food to gain the benefit of exercising "

    # STRESS Analysis 
    dictStressQualifiers = {'stressfull':1.3, 'unknown':1, 'balanced': 1} 
    if(curr_obj_data.stressQualifier == "unknown"):
        reason = reason + "Stress is not measured, please make sure the watch is on your wrist all the time to ensure right measurements. "
    else:
        reason = reason + "Your stress level is analysed as " + curr_obj_data.stressQualifier + ". "
    dict_ActivityMultiplicity['stress']=dictStressQualifiers[curr_obj_data.stressQualifier]

    return dict_ActivityMultiplicity, reason



def dataAnalysisSleep(curr_obj_data):
    filter= models.SleepData.objects.filter(is_active=True, userId = curr_obj_data.userId,userAccessToken=curr_obj_data.userAccessToken,calendarDate=curr_obj_data.calendarDate)
    reason = ""
    if(filter.exists()):
        if(filter.first().durationInSeconds >= 25200):
            if(filter.first().overallSleepScorequalifierKey != "unknown"):
                reason = reason + "You had enough sleep and the quality of sleep is " +  filter.first().overallSleepScorequalifierKey + ". "
            else:
                reason = reason + "You had enough sleep. "
        else:
            reason = reason + "Also you should take rest as you had less than 7 hours of sleep. "
    else:
        reason = reason + "Sleep is not measured. "
    
    return reason


#think about how to return the reason?
# the analysis function is called only when there is new data in the table, this is made sure by making th call analysis in dataToSleep/dataToDaily after a new instance is saved.    
# what are the five activity types? exercise, food, stress and general

def dataAnalysis(curr_obj_data, _type):
    if(_type=='daily'):
        dict, reason = dataAnalysisDaily(curr_obj_data)
        reason = reason + dataAnalysisSleep(curr_obj_data)
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