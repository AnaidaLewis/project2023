from rest_framework import serializers
from .models import UserWarrior, Notification


class SendRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=10)

    class Meta:
        fields = ['phone']



class NotificationSerializer(serializers.ModelSerializer):
    # user_name = serializers.SerializerMethodField()
    # user_notify_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'

    # def get_user_name(self,obj):
    #     return obj.user.first_name
    
    # def get_user_notify_name(self,obj):
    #     return obj.user_notify.first_name
    


class UserWarriorSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    warrior_name = serializers.SerializerMethodField()

    class Meta:
        model = UserWarrior
        fields = ['id','user_name', 'warrior_name','accept','reject']

    def get_user_name(self,obj):
        return obj.user.username
    
    def get_warrior_name(self,obj):
        return obj.warrior.username
    
# class CommunitySearchSerializer(serializers.Serializer):
#     # community = serializers.CharField(max_length=100)
#     latitude = serializers.CharField(max_length=100)
#     longitude = serializers.CharField(max_length=100)

#     class Meta:
#         fields = ['latitude','longitude']