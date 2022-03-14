from django.conf import settings
from twilio.rest import Client


def sendMessage(phone, message):
    account_sid = settings.ACCOUNT_SID
    auth_token = settings.AUTH_TOKEN
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=settings.SENDER_PHONE,
        to='+91'+phone)


def get_distance(coord1, coord2):
    import geopy.distance
    return geopy.distance.distance(coord1, coord2).km
