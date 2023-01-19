from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import signals

from posts.models import PostComment, Post
from groups.models import Groups
from configuration.models import POST_RECOMMENDATION_TYPE_LIST

User = get_user_model()

# Cure models
class Labels(models.Model):
    name = models.TextField()
    type = models.CharField(max_length=200)
    reason = models.TextField()
    link = models.CharField(max_length=400)
    is_label = models.BooleanField(default=True)
    is_coupuled = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}, {self.type}'

    class Meta:
        unique_together = ('name', 'type', 'reason')


class Ratings(models.Model):
    label = models.ForeignKey(Labels, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)
    datetime = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    rating = models.IntegerField(
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
     )
    is_label = models.BooleanField(default=True) 

    def __str__(self):
        return f'{self.label}, {self.user}'


# Recommendation Sender models
#   These models will send a recomemdantion when created
class SenderGroupRecommendation(models.Model):
    group = models.ForeignKey(Groups, models.CASCADE, null=True, blank=True)
    tags = models.CharField(max_length=300)
    date_time = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return str(self.group) + " ==> " + str(self.tags)

class SenderPostRecommendation(models.Model):
    post = models.ForeignKey(Post, models.CASCADE)
    tags = models.CharField(max_length=300)
    date_time = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return str(self.post.user) + " ==> " + str(self.tags)


# Tracking models
class TrackerPostRecommendation(models.Model):
    user = models.ForeignKey(User, models.CASCADE)

    nlp_raw_outputs = models.TextField(max_length=300)
    nlp_classification = models.TextField(max_length=100)
    sender = models.ForeignKey(SenderPostRecommendation, models.CASCADE)

    estimated_couple_ratings = models.TextField()
    estimated_rating_for_context_dic = models.TextField()

    estimated_raw_ratings_withoutcontext = models.TextField()
    estimated_final_recommendation_list = models.TextField()
    
    recommended = models.ForeignKey(Labels, models.CASCADE)
    comment = models.ForeignKey(PostComment, models.CASCADE)

    date_time = models.DateTimeField(auto_now_add=True)

    recommendation_type = models.CharField(max_length=100, choices=POST_RECOMMENDATION_TYPE_LIST)


    def __str__(self):
        return str(self.user) +  " == " + str(self.nlp_classification) + " ==> " + str(self.recommended) + " ==> " + str(self.sender.tags)


class TrackerGroupRecommendation(models.Model):
    group = models.ForeignKey(Groups, models.CASCADE)
    recommended = models.ForeignKey(Labels, models.CASCADE)
    sender = models.ForeignKey(SenderGroupRecommendation, models.CASCADE)

    recommendation_tree = models.TextField()
    recommendation_scores = models.TextField()

    post = models.ForeignKey(Post, models.CASCADE)

    date_time = models.DateTimeField(auto_now_add=True)

    recommendation_type = models.CharField(max_length=100, choices=POST_RECOMMENDATION_TYPE_LIST)


    def __str__(self):
        return str(self.group) + " ==> " + str(self.recommended) + " ==> " + str(self.sender.tags)


from .signals import sendGroupRecommendationsSignal ,sendPostRecommendationsSignal
signals.post_save.connect(sendGroupRecommendationsSignal, sender=SenderGroupRecommendation)
signals.post_save.connect(sendPostRecommendationsSignal, sender=SenderPostRecommendation)