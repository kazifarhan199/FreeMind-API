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
            #doing a create or update so that if you receive same day data it can just be updated istead of creating a new record
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
            #dataAnalysis(fromDaily=True)
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
            #doing a create or update so that if you receive same day data it can just be updated istead of creating a new record
            # Create or retrieve the instance from the db
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
            #dataAnalysis(fromDaily=False)
    except Exception as e:
        # handle the exception
        print(f'Error saving data: {e}') 

# the function Does the data analysis before trying to alter the recommendation list
'''
def dataAnalysisDaily():
    # what are the five activity types? exercise, food, 
    activityType=Null
    # logic to do the analysis
    return activityType

def dataAnalysisSleep():
    activityType=Null
    # logic to do the analysis
    for sleep return Rest/Sleep if user need to rest otherwise Null
    return activityType
    
def dataAnalysis(fromDaily=True):
    
    if(fromDaily):
        # see if current day's data has null feilds for all, otherwise call the daily Analysis
        dataAnalysisDaily()
    else:
        # see if current day's data has null feilds for all, otherwise call the sleep Analysis
        dataAnalysisSleep()
    # setup a trigger to do analysis when there's new data in DB

    # Analyse the current day's data to come up with a activity type to increse/decrease the prominance

'''

# Set the schedule for the task to run every 2 hours
# app.conf.beat_schedule = {
#     'collect_garmin_data': {
#         'task': 'your_project_name.tasks.collect_garmin_data',
#         'schedule': timedelta(hours=2),
#     },
# }