from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
import logging
from push_notifications.models import MobileNotification
logger = logging.getLogger(__name__)

User = get_user_model()


class WebNotification:
    ''' Web socket based Notification'''

    def __init__(self):
        pass

    def send_notification_to_all(self, title, message):
        '''
        live_message will be sent to the all users
        '''
        
        logger.info('sending web notifcation  %s', title)
            
        try:
            
            messages = []
            for user in User.objects.all():
                messages.append(MobileNotification(recipient=user,
                                                title = title,
                                                message=message))
            MobileNotification.objects.bulk_create(messages)
        
        
            # Send message to room group
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "broadcast", {
                    "type": "user.message",
                    "event": "media_created",
                    "message": {
                        'title':title,
                        'message':message
                    }
                }
            )
        except Exception as e:
            logger.error('Error while sending web socket notification %s', e)
            pass
        
        
    def send_only_notification_to_user(self, users, title, message=None):
        '''
        live_message will be sent to selected users
        @users list of queryset
        @live_message message title
        '''
        
        logger.info('sending web notifcation to selected user %s', title)
                
        try:
            messages = []
            for user in users:
                messages.append(MobileNotification(recipient=user,
                                                title = title,
                                                message=message))
            MobileNotification.objects.bulk_create(messages)
            
            # Send message to group
            channel_layer = get_channel_layer()
            
            user_channels_groups = [ 'notification-to-{}'.format(user.email).replace('_','-').replace('@','').replace('+','') for user in users]
            
            for user_group_name in user_channels_groups:
                logger.info('user group name web socket notification name %s', user_group_name)

                async_to_sync(channel_layer.group_send)(
                    user_group_name, {
                        "type": "user.message",
                        "event": "media_created",
                        "message": {
                            'title':title,
                            'message':message
                        }
                    }
                )
        except Exception as e:
            logger.error('Error while sending web socket notification %s', e)
            pass
        