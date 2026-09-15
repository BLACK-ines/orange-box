from .models import Notification


def notifications_context(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(recipient=request.user, status='unread').order_by('-date')
        return {
            'unread_notifications': unread,
            'unread_count': unread.count()
        }
    return {'unread_notifications': [], 'unread_count': 0}