from user_agents import parse
import requests

def get_client_ip(request):
    xff=request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0] if xff else request.META.get("REMOTE_ADDR")

def parse_user_agent(ua_string):
    ua=parse(ua_string)
    return {
        "browser": ua.browser.family,
        "device": "Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "Desktop"
    }
    
def geo_lookup(ip):
    try:
        ip_info = requests.get(f'https://ipinfo.io/{ip}/json').json()
        return {
        "city" : ip_info.get('city', 'Unknown'),
        "region" : ip_info.get('region', 'Unknown'),
        "country" : ip_info.get('country', 'Unknown'),
        "loc" : ip_info.get('loc', 'Unknown')  # Latitude,Longitude
        }
    except:
        return {"country": None, "region": None, "city": None,"loc":None}