from django.db import models

# Create your models here.


from mongoengine import Document, StringField, DateTimeField,BooleanField,IntField
from datetime import datetime
import shortuuid



class ShortURL(Document):
    short_id = StringField(
        required=True,
        unique=True,
        max_length=10,
        default=lambda: shortuuid.ShortUUID().random(length=4)
    )
    original_url = StringField(required=True)
    created_at = DateTimeField(default=datetime.now())
    expires_at = DateTimeField(null=True)  # Optional expiry
    password = StringField(null=True)      # Optional password
    one_time = BooleanField(default=False) # One-time use
    hit_count = IntField(default=0)
    first_hit = DateTimeField(null=True)
    last_hit = DateTimeField(null=True)
    
class URLAccessLog(Document):
    short_url = StringField(required=True)
    accessed_at = DateTimeField(default=datetime.now())
    ip_address = StringField()
    referer = StringField()
    country = StringField()
    region = StringField()
    city = StringField()
    browser = StringField()
    device = StringField()