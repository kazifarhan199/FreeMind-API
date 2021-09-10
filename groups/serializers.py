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

    def is_valid(self):
        super().is_valid()
        email=self.context['request'].data.get('email')
        instance_user=self.context['request'].user
        # Change to take group id from user (SINGLEUSERCONSTRAINT)
        if not GroupsMember.objects.filter(user=instance_user).exists():
            raise serializers.ValidationError({"group": ["Access Denied."]})
        group=GroupsMember.objects.filter(user=instance_user).first().group.id
        if not group:
            raise serializers.ValidationError({"group": ["This field is required."]})
        #

        if not email:
            raise serializers.ValidationError({"email": ["This field is required."]})
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": ["User with this email does not exists."]})

        if not Groups.objects.filter(pk=group).exists():
            """Group does not exists"""
            raise serializers.ValidationError({"group": ["No group found."]})
        if not GroupsMember.objects.filter(user=instance_user, group_id=group).exists():
            """User who is add is not in group"""
            raise serializers.ValidationError({"group": ["Access denied."]})

        # Not allowing user to be added to multiple groups, just disable (SINGLEUSERCONSTRAINT)
        if GroupsMember.objects.filter(user=User.objects.get(email=email)).exists():
            if User.objects.get(email=email) == instance_user:
                raise serializers.ValidationError({"email": ["You are already in a group, please leave the group first."]})
            raise serializers.ValidationError({"email": ["User already in a group."]})
        #

        return True

    def validate(self, valid_data):
        user=User.objects.get(email=self.context['request'].data.get('email'))
        valid_data['user'] = user
        # Change to take group id from user (SINGLEUSERCONSTRAINT)
        valid_data['group'] = GroupsMember.objects.filter(user=self.context['request'].user).first().group
        #
        return super().validate(valid_data)

    class Meta:
        model = GroupsMember
        fields = ('username', 'userimage', 'email', 'user', )


class GroupsSerializer(serializers.ModelSerializer):
    members = GroupsMemberSerializer(many=True, read_only=True)
    name = serializers.CharField()

    class Meta:
        model = Groups
        fields = ('name', 'members', 'user', 'id', )

    def create(self, valid_data):
        instance_user = self.context['request'].user
        if GroupsMember.objects.filter(user=valid_data['user']):
            """Allowing only one user in a single group (SINGLEUSERCONSTRAINT)"""
            if valid_data['user'] == instance_user:
                raise serializers.ValidationError({"email": ["You are already in a group, please leave the group first."]})
            raise serializers.ValidationError({"user": ["The user is already in a group."]})
        return super().create(valid_data)