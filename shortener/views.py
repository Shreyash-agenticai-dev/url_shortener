from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from .serializers import ShortenURLSerializer
from .models import ShortURL
from django.conf import settings

BASE_URL = "http://localhost:8000"  

# /shorten
class ShortenURLView(APIView):
    def post(self, request):
        serializer = ShortenURLSerializer(data=request.data)
        if serializer.is_valid():
            original_url = serializer.validated_data['url']
            existing = ShortURL.objects(original_url=original_url).first()
            if existing:
                short_url = request.build_absolute_uri(f"/{existing.short_id}")
                return Response({'short_url': short_url}, status=status.HTTP_200_OK)

            # Create new short URL if not found
            new_entry = ShortURL(original_url=original_url)
            new_entry.save()

            short_url = request.build_absolute_uri(f"/{new_entry.short_id}")
            return Response({'short_url': short_url}, status=status.HTTP_201_CREATED)

            # If validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#/<ID>/
def redirect_to_original(request, short_id):
    try:
        url_obj = ShortURL.objects.get(short_id=short_id)
        return redirect(url_obj.original_url)
    except ShortURL.DoesNotExist:
        return Response({'error': 'Short URL not found'}, status=404)

# /info/<Id>/
class ShortURLInfoView(APIView):
    def get(self, request, short_id):
        try:
            url_obj = ShortURL.objects.get(short_id=short_id)
            return Response({
                'original_url': url_obj.original_url,
                'created_at': url_obj.created_at
            })
        except ShortURL.DoesNotExist:
            return Response({'error': 'Short URL not found'}, status=404)
