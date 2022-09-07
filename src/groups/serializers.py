from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Groups, GroupsMember

User = get_user_model()


class GroupsMemberSerializer(serializers.ModelSerializer):
    userimage = serializers.SerializerMethodField('get_userimage', read_only=True)
    username = serializers.CharField(required=False)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    def get_userimage(self, obj):
        return obj.userimage
        

    def validate(self, valid_data):
        email = self.context['request'].data.get('email')
        if not email: raise serializers.ValidationError({"email": ["This field is required."]})

        gid = self.context['request'].GET.get('group')
        if not gid: raise serializers.ValidationError({"group": ["This field is required."]})

        user = None
        if User.objects.filter(email=email).exists(): user = User.objects.get(email=email)
        if User.objects.filter(username=email).exists(): user = User.objects.get(username=email)
        if user == None: raise serializers.ValidationError({"user": ["User not found."]})
        '''User present'''
        user = user
        instance_user = self.context['request'].user

        if not Groups.objects.filter(pk=gid).exists(): raise serializers.ValidationError({"group": ["Group does not exists."]})
        if not GroupsMember.objects.filter(user=instance_user, group=Groups.objects.get(pk=gid)).exists():
            '''User not present in group'''
            raise serializers.ValidationError({"user": ["User not part of group."]})

        group = GroupsMember.objects.get(user=instance_user, group=Groups.objects.get(pk=gid)).group

        if GroupsMember.objects.filter(user=user, group=group).exists():
            raise serializers.ValidationError({"user": ["User already present in the group."]})

        valid_data['group'] = group
        valid_data['user'] = user
        return super().validate(valid_data)

    class Meta:
        model = GroupsMember
        fields = ('username', 'userimage', 'email', 'user')


class GroupsSerializer(serializers.ModelSerializer):
    members = GroupsMemberSerializer(many=True, read_only=True)
    group_name = serializers.CharField()
    isin = serializers.SerializerMethodField('isIn')
    image_path = serializers.SerializerMethodField('get_image')
    
    def get_image(self, obj):
        return obj.image.url

    class Meta:
        model = Groups
        fields = ('group_name', 'members', 'user', 'id', 'isin', 'image', 'image_path', 'is_channel')

    def isIn(self, obj):
        user = self.context.get('request', None).user
        if GroupsMember.objects.filter(group=obj, user=user).exists():
            return True
        else:
            return False

    def create(self, valid_data):
        instance_user = self.context['request'].user
        return super().create(valid_data)


