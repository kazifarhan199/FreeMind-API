from .models import GroupsMember

def add_creator_to_team(sender, instance, **kwargs):
    if not GroupsMember.objects.filter(user=instance.user, group=instance).exists(): 
        GroupsMember.objects.create(user=instance.user, group=instance)
