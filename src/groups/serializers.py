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
        user = None
        if User.objects.filter(email=self.context['request'].data.get('email')).exists():
            user=User.objects.get(email=self.context['request'].data.get('email'))
    
        if User.objects.filter(username=self.context['request'].data.get('email')).exists():
            user=User.objects.get(username=self.context['request'].data.get('email'))
        if user == None:
            raise serializers.ValidationError({"user": ["User not found."]})

        valid_data['user'] = user

        email = self.context['request'].data.get('email')
        instance_user = self.context['request'].user
            
        group=GroupsMember.objects.filter(user=instance_user).first().group.id
        if not group:
            raise serializers.ValidationError({"group": ["This field is required."]})
        #

        if not email:
            raise serializers.ValidationError({"email": ["This field is required."]})
        
        user = None
        if not User.objects.filter(email=email).exists():
            if not User.objects.filter(username=email).exists():
                raise serializers.ValidationError({"email/username": ["User with this email does not exists."]})
            else:
                user = User.objects.get(username=email)
        else:
            user = User.objects.get(email=email)

        if not Groups.objects.filter(pk=group).exists():
            """Group does not exists"""
            raise serializers.ValidationError({"group": ["No group found."]})
        if not GroupsMember.objects.filter(user=instance_user, group_id=group).exists():
            """User who is add is not in group"""
            raise serializers.ValidationError({"group": ["Access denied."]})

        # Not allowing user to be added to multiple groups, just disable (SINGLEUSERCONSTRAINT)
        if GroupsMember.objects.filter(user=user).exists():
            if user == instance_user:
                raise serializers.ValidationError({"email": ["You are already in a group, please leave the group first."]})
            raise serializers.ValidationError({"email": ["User already in a group."]})
        #

        # Change to take group id from user (SINGLEUSERCONSTRAINT)
        valid_data['group'] = GroupsMember.objects.filter(user=instance_user).first().group
        #
        return super().validate(valid_data)

    class Meta:
        model = GroupsMember
        fields = ('username', 'userimage', 'email', 'user', )


class GroupsSerializer(serializers.ModelSerializer):
    members = GroupsMemberSerializer(many=True, read_only=True)
    group_name = serializers.CharField()
    isin = serializers.SerializerMethodField('isIn')

    class Meta:
        model = Groups
        fields = ('group_name', 'members', 'user', 'id', 'isin')

    def isIn(self, obj):
        user = self.context.get('request', None).user
        if GroupsMember.objects.filter(group=obj, user=user).exists():
            return True
        else:
            return False

    def create(self, valid_data):
        instance_user = self.context['request'].user
        if GroupsMember.objects.filter(user=valid_data['user']):
            """Allowing only one user in a single group (SINGLEUSERCONSTRAINT)"""
            if valid_data['user'] == instance_user:
                raise serializers.ValidationError({"email": ["You are already in a group, please leave the group first."]})
            raise serializers.ValidationError({"user": ["The user is already in a group."]})
        return super().create(valid_data)


