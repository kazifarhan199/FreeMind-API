from .models import ScheduledGroupTaslk, SenderGroupRecommendation
from django.utils import timezone
from celery import shared_task

@shared_task()
def runScheduledTasks():
    all_tasks = ScheduledGroupTaslk.objects.filter(done_today=False)
    count = 0
    for task in all_tasks:
        print(task.time)
        print(timezone.now().time())
        print(task.time <= timezone.now().time())
        if task.time <= timezone.now().time():
            SenderGroupRecommendation.objects.create(group=task.group, tags="Automatic Schedued")
            count += 1
            task.done_today=True
            task.save()
    return count


@shared_task()
def  resetScheduledTasks():
    all_tasks = ScheduledGroupTaslk.objects.filter(done_today=True)
    count = 0
    for taslk in all_tasks:
        taslk.done_today = False
        taslk.save()
        count+=1
    return count
 