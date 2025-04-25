from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from .serializers import ShortenURLSerializer
from django.http import HttpResponseForbidden, Http404
from .models import ShortURL,URLAccessLog
from django.conf import settings
from .utils import get_client_ip,parse_user_agent,geo_lookup
from datetime import datetime,timedelta
import shortuuid

BASE_URL = "http://localhost:8000"  

# /shorten
class ShortenURLView(APIView):
    def post(self, request):
        serializer = ShortenURLSerializer(data=request.data)
        if serializer.is_valid():
            data=serializer.validated_data
            short_id=data.get('custom_id') or shortuuid.uuid()[:4]
            original_url = data['url']
            existing = ShortURL.objects(original_url=original_url).first()
            
            if existing:
                short_url = request.build_absolute_uri(f"/{existing.short_id}")
                return Response({'short_url': short_url}, status=status.HTTP_200_OK)
            
            if ShortURL.objects(short_id=short_id).first():
                return Response({"error": "Custom ID already exists."}, status=400)
            
            if 'expires_in' in data:
                expires_at = datetime.now() + timedelta(seconds=data['expires_in'])
            else:
                expires_at=datetime.now() + timedelta(seconds=60) # defualt expires within a Minute

            # # Create new short URL if not found
            new_entry = ShortURL(
                short_id=short_id,
                expires_at=expires_at,
                password=data.get('password') or None,
                one_time=data.get('one_time', False),
                original_url=original_url
                )
            new_entry.save()
            
            short_url = request.build_absolute_uri(f"/{new_entry.short_id}")
            return Response({'short_url': short_url}, status=status.HTTP_201_CREATED)

            # If validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#/<ID>/
class redirect_to_original(APIView):
    def get(self,request, short_id):
        try:    
            url = ShortURL.objects(short_id=short_id).first()

            if not url:
                raise Http404("Short URL not found.")

            if url.expires_at and url.expires_at < datetime.now():
                return Response({"error": "URL has expired."}, status=410)

            if url.password:
                if request.GET.get('password') != url.password:
                    return HttpResponseForbidden("Password required or incorrect.")

            # log access
            ip = get_client_ip(request)
            geo = geo_lookup(ip)
            ua = parse_user_agent(request.META.get("HTTP_USER_AGENT", ""))

            URLAccessLog(
                short_url=short_id,
                ip_address=ip,
                referer=request.META.get("HTTP_REFERER"),
                country=geo["country"],
                region=geo["region"],
                city=geo["city"],
                browser=ua["browser"],
                device=ua["device"]
            ).save()

            url.hit_count += 1
            url.last_hit = datetime.now()
            if not url.first_hit:
                url.first_hit = datetime.now()
            url.save()

            redirect_url = url.original_url
            if url.one_time:
                url.delete()
                
                
            return redirect(url.original_url)
        except ShortURL.DoesNotExist:
            return Response({'error': 'Short URL not found'}, status=404)        
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=500)


# /info/<Id>/
class ShortURLInfoView(APIView):
    def get(self, request, short_id):
        try:
            url = ShortURL.objects.get(short_id=short_id)
            return Response({
                'original_url': url.original_url,
                'created_at':   url.created_at,
                
                "original_url": url.original_url,
                "created_at": url.created_at.isoformat(),
                "expires_at": url.expires_at.isoformat() if url.expires_at else None,
                "first_hit": url.first_hit.isoformat() if url.first_hit else None,
                "last_hit": url.last_hit.isoformat() if url.last_hit else None,
                "hit_count": url.hit_count
            })
        except ShortURL.DoesNotExist:
            return Response({'error': 'Short URL not found'}, status=404)
