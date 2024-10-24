# context_processors.py

from gym_app.models import Message

def unread_messages_processor(request):
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()
    else:
        unread_count = 0
    return {
        'unread_messages_count': unread_count,
    }
