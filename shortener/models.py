from django.db import models

# Create your models here.


from mongoengine import Document, StringField, DateTimeField
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
    created_at = DateTimeField(default=datetime.utcnow)