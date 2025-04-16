from rest_framework import serializers
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import requests

class ShortenURLSerializer(serializers.Serializer):
    url = serializers.CharField()
    
    def validate_url(self, value):
        
        # Built int Checker of URL ( which check syntax )
        validator = URLValidator()
        try:
            validator(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid URL format.")
        


        # Check URL returns 200
        try:
            response = requests.head(value, allow_redirects=True, timeout=5)
            if response.status_code != 200:
                raise serializers.ValidationError(
                    f"URL responded with status code {response.status_code}, not 200."
                )
        except requests.RequestException:
            raise serializers.ValidationError("URL is not reachable or timed out.")

        return value
