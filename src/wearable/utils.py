from . import models

import datetime
from dateutil import tz


from recommendations.models import SenderWearableRecommendation

from django.contrib.auth import get_user_model

User=get_user_model()

# saving raw daily data from garmin (can be used to refer back to, if need be)     
def save_garmin_daily_data_to_db(data):
    # Create or update the data in the database
    # try:
        # Create or retrieve the instance from the db
        instance = models.GarminDailyData.objects.create(
                data=data
            )
        # save the instance
        instance.save()
    # except Exception as e:
    #     # handle the exception
    #     print(f'Error saving data: {e}')    


# saving raw stress data from garmin (can be used to refer back to, if need be)
def save_garmin_stress_data_to_db(data):
    # Create or update the data in the database
    # try:
        # Create or retrieve the instance from the db
        instance = models.GarminStressData.objects.create(
                data=data
            )
        # save the instance
        instance.save()
    # except Exception as e:
    #     # handle the exception
    #     print(f'Error saving data: {e}')    

# saving raw sleep data from garmin (can be used to refer back to, if need be)
def save_garmin_sleep_data_to_db(data):
    # Create or update the data in the database
    # try:
        # Create or retrieve the instance from the db
        instance = models.GarminSleepData.objects.create(
                data=data
            )
        # save the instance
        instance.save()
    # except Exception as e:
    #     # handle the exception
    #     print(f'Error saving data: {e}')    

def dateToday():
     pass


# saving daily data from garmin (just the columns needed instead of all the data)
def dataToDailies(data):
    
    # try:
        # Create or retrieve the instance from the db
        #  data = {'dailies': [ {'userId': ... } { } { } ]} 
        today=datetime.datetime.today()-datetime.timedelta(hours=6)
        today=today.date()
        print(today)
        dailiesList=data['dailies']
        #print(dailiesList==None)
        #print(dailiesList)
        filter=models.DailyData.objects.filter(is_active=True,garminUserId = dailiesList[0].get('userId'),userAccessToken=dailiesList[0].get('userAccessToken'))
        for i in filter:
            i.is_active=False
            i.save()
        for day in dailiesList:
            # filter= models.DailyData.objects.filter(is_active=True, garminUserId = day.get('userId'),userAccessToken=day.get('userAccessToken'),calendarDate=day.get('calendarDate'))
            # if(filter.exists()):

            #     for i in filter:
            #         i.is_active=False
            #         i.save()
            #create a instance in the DB
            #print(str(today))
            #print(str(day.get('calendarDate')))
            #print(True if (str(today)==str(day.get('calendarDate'))) else False)
            instance = models.DailyData.objects.create(
                
                is_active= True if (str(today)==str(day.get('calendarDate'))) else False,
                garminUserId = day.get('userId'),
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
        filter=models.DailyData.objects.filter(is_active=True,garminUserId = dailiesList[0].get('userId'),userAccessToken=dailiesList[0].get('userAccessToken'))
        for day in filter:
            print(day.garminUserId, day.calendarDate)
            if (str(today)==str(day.calendarDate)):
                print("OBJECT")
                print(day.garminUserId, day.calendarDate)
                print("OBJECT DONE")
                analysis= dataAnalysis(day, _type='daily')
                print(analysis)
                break
            #print(day.calendarDate)
        #filter= models.DailyData.objects.filter(is_active=True, userId = day.get('userId'),userAccessToken=day.get('userAccessToken'),calendarDate=day.get('calendarDate'))
        # if(filter):
        #     #for curr_obj in filter:
        #     print("OBJECT")
        #     print(filter.garminUserId, filter.calendarDate)
        #     print("OBJECT DONE")
        #     dataAnalysis(filter, _type='daily')
            
            
    # except Exception as e:
    #     # handle the exception
    #     print(f'Error saving data: {e}') 

# saving sleep data from garmin (just the columns needed instead of all the data)
def dataToSleep(data):
    
    # try:
        sleepList=data['sleeps']
        today=datetime.date.today()
        for sleep in sleepList:
            filter= models.SleepData.objects.filter(is_active=True, garminUserId = sleep.get('userId'),userAccessToken=sleep.get('userAccessToken'),calendarDate=sleep.get('calendarDate'))
            if(filter.exists()):

                for i in filter:
                    i.is_active=False
                    i.save()
            # Create a instance in the db
            instance = models.SleepData.objects.create( 
                is_active= True if (str(today)==str(sleep.get('calendarDate'))) else False,              
                garminUserId = sleep.get('userId'),
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
            
    # except Exception as e:
    #     # handle the exception
    #     print(f'Error saving data: {e}') 

# the function Does the data analysis before trying to alter the recommendation list

#return multiplicity 
    #1 if activity is in range
    #0.1-0.9: maybe 0.7: if activity level is already high you don't want to suggest the user to do more of the activity
    #1.1-1.9: maybe 1.3: if activity level is low you want to suggest the user to do more of the activity
def dataAnalysisDaily(curr_obj_data): 
    reason = "\nAnalysis of the Day: \n"
    dict_ActivityMultiplicity ={ 'exercise':None, 'food':None, 'stress':None, 'optimal_count':0, 'sleep':None}

    # logic to do the Analysis

    #STEPS and CALORIES Analysis
    if((curr_obj_data.steps==None or curr_obj_data.steps==0) and (curr_obj_data.activeKilocalories==0 or curr_obj_data.activeKilocalories==None)):
        reason = reason + "\n"+f"{'Exercise':<10}"+":\t Not measured"
    else:
        if (curr_obj_data.activeKilocalories > 500):
             curr_obj_data.activeKilocalories = curr_obj_data.activeKilocalories*0.75
        
        if((curr_obj_data.activeKilocalories >= 300 and curr_obj_data.activeKilocalories <= 500) or (curr_obj_data.steps>= 5000 and curr_obj_data.steps<=10000)):
            dict_ActivityMultiplicity['optimal_count']+=1

            #dict_ActivityMultiplicity['exercise']=1 
            #dict_ActivityMultiplicity['food']=1.3
            dict_ActivityMultiplicity['exercise']=1 
            dict_ActivityMultiplicity['food']=1.1
            #dict_ActivityMultiplicity['exercise']=1 
            #dict_ActivityMultiplicity['food']=1.05
            #print(curr_obj_data.activeKilocalories, curr_obj_data.steps)
            reason = reason + "\n"+f"{'Exercise':<10}"+":\t \U0001F7E2"
        elif(curr_obj_data.activeKilocalories > 500 or curr_obj_data.steps> 10000 ):
            dict_ActivityMultiplicity['optimal_count']+=1

            #dict_ActivityMultiplicity['exercise']=0.7
            #dict_ActivityMultiplicity['food']=1.5
            dict_ActivityMultiplicity['exercise']=0.8
            dict_ActivityMultiplicity['food']=1.3
            #dict_ActivityMultiplicity['exercise']=0.9
            #dict_ActivityMultiplicity['food']=1.1
            #print(curr_obj_data.activeKilocalories, curr_obj_data.steps)
            reason = reason + "\n"+f"{'Exercise':<10}"+":\t \U0001F7E2"
        else:
            #dict_ActivityMultiplicity['exercise']=1.5
            #dict_ActivityMultiplicity['food']=0.9
            dict_ActivityMultiplicity['exercise']=1.3
            dict_ActivityMultiplicity['food']=1
            #dict_ActivityMultiplicity['exercise']=1.1
            #dict_ActivityMultiplicity['food']=1
            print(curr_obj_data.activeKilocalories, curr_obj_data.steps)
            reason = reason + "\n"+f"{'Exercise':<10}"+":\t \U0001F534"

    # STRESS Analysis 
    #dictStressQualifiers = {'stressful':1.5, 'unknown':1, 'balanced': 1.3, 'calm':0.9} -- don't use this
    #dictStressQualifiers = {'stressful':1.5, 'unknown':1.3, 'balanced': 1, 'calm':0.7}
    dictStressQualifiers = {'stressful':1.3, 'unknown':1.1, 'balanced': 1, 'calm':0.8}
    dictStressEmojis = {'stressful': "\U0001F92F", 'unknown':"\U0001F937", 'balanced': "\U0001F7E2", 'calm':"\U0001F7E2"}
    #dictStressQualifiers = {'stressful':1.1, 'unknown':1.05, 'balanced': 1, 'calm':0.9}
    
    if(curr_obj_data.stressQualifier == "balanced" or curr_obj_data.stressQualifier == "calm"):
        dict_ActivityMultiplicity['optimal_count']+=1
    
    
    if(not curr_obj_data.stressQualifier or curr_obj_data.stressQualifier == "unknown"):
        dict_ActivityMultiplicity['stress']=dictStressQualifiers.get(curr_obj_data.stressQualifier)
        reason = reason + "\n"+f"{'Stress':<12}"+":\t Not measured/ Not enough Data"
    else:
        reason = reason + "\n"+f"{'Stress':<12}"+":\t " + dictStressEmojis.get(curr_obj_data.stressQualifier) + " Analysis: "+ curr_obj_data.stressQualifier
        dict_ActivityMultiplicity['stress']=dictStressQualifiers.get(curr_obj_data.stressQualifier)

    return dict_ActivityMultiplicity, reason



def dataAnalysisSleep(curr_obj_data):
    filter= models.SleepData.objects.filter(is_active=True, garminUserId = curr_obj_data.garminUserId,userAccessToken=curr_obj_data.userAccessToken,calendarDate=curr_obj_data.calendarDate)
    reason = ""
    sleep=1
    if(filter.exists()):
        if(filter.first().durationInSeconds >= 25200):
            if(filter.first().overallSleepScorequalifierKey != "unknown"):
                reason = reason + "\n"+f"{'Sleep':<12}"+":\t \U0001F7E2 Analysis: " +  filter.first().overallSleepScorequalifierKey + ". "
                #sleep= 1.5 
                #sleep= 1.3
                #sleep= 1.1
                sleep=1
            else:
                reason = reason + "\n"+f"{'Sleep':<12}"+":\t \U0001F7E2"
                #sleep=1.5
                #sleep=1.3
                #sleep=1.1
                sleep=1
        else:
            reason = reason + "\n"+f"{'Sleep':<12}"+":\t \U0001F534"
            #sleep=2
            sleep=1.5
            #sleep=1.3
    else:
        reason = reason + "\n"+f"{'Sleep':<12}"+":\t Not Measured "
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
        
        if(sleep==1):
            dict['optimal_count']+=1
        
        #if(sleep==2 and dict['stress']):
        if(sleep==1.5 and dict['stress']!='unknown'):
        #if(sleep==1.3 and dict['stress']):
            dict['stress']=dict['stress']+0.2 #round 1&2
            #dict['stress']=dict['stress']+0.05
        #elif(sleep==2 ):
        elif(sleep==1.5 and dict['stress']=='unknown'):
        #elif(sleep==1.3 ):
            dict['stress']=1.2 #round 1&2
            #dict['stress']=1.05
        dict['sleep']=sleep

        dict['sleep']=round(dict['sleep'], 2)
        dict['stress']=round(dict['stress'], 2)
        dict['exercise']=round(dict['exercise'], 2)
        dict['food']=round(dict['food'], 2)

        print(reason, dict.keys(), dict.values())

        SenderWearableRecommendation.objects.create( 
            reason = reason,
            sleep = dict['sleep'],
            stress = dict['stress'],
            food = dict['food'],
            exercise = dict['exercise'],
            optimal = True if(dict['optimal_count']==3) else False,
            user= models.UserIdMap.objects.get(garminUserId=curr_obj_data.garminUserId).user,
        )

        return True

       
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