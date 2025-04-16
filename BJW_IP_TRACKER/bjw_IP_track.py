import os
import re
import socket
import random
import requests
import folium
import sys
from pathlib import Path
from ScrapeSearchEngine.SearchEngine import Google

SCRIPT_DIR = Path(__file__).resolve().parent
USER_AGENTS_FILE = SCRIPT_DIR / "useragents.txt"
MAP_PATH = SCRIPT_DIR / "world_map.html"

def load_user_agents():
    try:
        with open(USER_AGENTS_FILE, "r") as file:
            return [ua.strip() for ua in file if ua.strip()]
    except Exception as e:
        print(f"[ERROR] Could not load user agents: {e}")
        return ["Mozilla/5.0"]

USER_AGENTS = load_user_agents()

def get_random_ua():
    return random.choice(USER_AGENTS)

def print_ip_api_details(ip):
    """
    Fetches detailed information from ip-api.com and prints it in a clean format.
    """
    api = "http://ip-api.com/json/"
    try:
        data = requests.get(api + ip).json()
        sys.stdout.flush()
        header = "=" * 40
        print(header)
        print("ip-api Detailed Information")
        print(header)
        print(f"[Victim]       : {data.get('query', 'N/A')}")
        print(f"[ISP]          : {data.get('isp', 'N/A')}")
        print(f"[Organization] : {data.get('org', 'N/A')}")
        print(f"[City]         : {data.get('city', 'N/A')}")
        print(f"[Region]       : {data.get('region', 'N/A')}")
        print(f"[Longitude]    : {data.get('lon', 'N/A')}")
        print(f"[Latitude]     : {data.get('lat', 'N/A')}")
        print(f"[Time zone]    : {data.get('timezone', 'N/A')}")
        print(f"[Zip code]     : {data.get('zip', 'N/A')}")
        print(header)
    except KeyboardInterrupt:
        print("Terminating, Bye")
        sys.exit(0)
    except requests.exceptions.ConnectionError:
        print("[~] Check your internet connection!")
        sys.exit(1)

class Pinger:
    @staticmethod
    def ping(ip):
        print("[+] Testing if the IP address responds...")
        #use system ping command based on OS
        command = f'ping -n 1 {ip} > nul' if os.name == "nt" else f'ping -c 1 {ip} > /dev/null 2>&1'
        response = os.system(command)
        if response == 0:
            print("[+] The IP address responds.\n")
        else:
            print("[-] The IP address does not respond.\n")

class IPApi:
    @staticmethod
    def get_data(ip):
        url = f"http://ip-api.com/json/{ip}"
        headers = {"User-Agent": get_random_ua()}
        response = requests.get(url, headers=headers)
        return response.json()

    @staticmethod
    def lookup(ip):
        data = IPApi.get_data(ip)
        output = (
            "Ip-api\n"
            f"  Organization : {data.get('org', 'N/A')}\n"
            f"  Country      : {data.get('country', 'N/A')}\n"
            f"  Region       : {data.get('regionName', 'N/A')}\n"
            f"  City         : {data.get('city', 'N/A')}\n"
        )
        return output, data.get('city', 'N/A')

class IPInfo:
    @staticmethod
    def get_data(ip):
        url = f"https://ipinfo.io/{ip}/json"
        headers = {"User-Agent": get_random_ua()}
        response = requests.get(url, headers=headers)
        return response.json()

    @staticmethod
    def look(ip):
        track = IPInfo.get_data(ip)
        loc = track.get('loc', '')
        if ',' in loc:
            lat, lon = loc.split(',')
        else:
            lat, lon = 'N/A', 'N/A'
        output = (
            "Ipinfo\n"
            f"  Hostname : {track.get('hostname', 'N/A')}\n"
            f"  A.S.     : {track.get('org', 'N/A')}\n"
            f"  Country  : {track.get('country', 'N/A')}\n"
            f"  Region   : {track.get('region', 'N/A')}\n"
            f"  City     : {track.get('city', 'N/A')}\n"
        )
        latlong = (
            "\n-------------------------------------------------------\n\n"
            f"  Latitude  : {lat}\n"
            f"  Longitude : {lon}\n"
        )
        return output, track.get('city', 'N/A'), latlong

    @staticmethod
    def coordinates(ip):
        data = IPInfo.get_data(ip)
        loc = data.get('loc', '')
        if ',' in loc:
            return loc.split(',')
        return 'N/A', 'N/A'

class IPWhois:
    @staticmethod
    def get_data(ip):
        url = f"http://ipwho.is/{ip}"
        headers = {"User-Agent": get_random_ua()}
        response = requests.get(url, headers=headers)
        return response.json()

    @staticmethod
    def lok(ip):
        data = IPWhois.get_data(ip)
        output = (
            "IpWhois\n"
            f"  Continent : {data.get('continent', 'N/A')}\n"
            f"  Country   : {data.get('country', 'N/A')}\n"
            f"  Region    : {data.get('region', 'N/A')}\n"
            f"  City      : {data.get('city', 'N/A')}\n\n"
            f"  I.S.P.    : {data.get('connection', {}).get('isp', 'N/A')}\n"
        )
        return output, data.get('city', 'N/A')

    @staticmethod
    def resolv_org(ip):
        data = IPWhois.get_data(ip)
        domain = data.get('connection', {}).get('domain', '')
        org = domain.split('.')[0] if domain else ''
        return f"{org.upper()}\n" if org else ""

class MapCreator:
    @staticmethod
    def create_map(latitude, longitude):
        map_world = folium.Map(location=[latitude, longitude], zoom_start=5)
        folium.Marker(location=[latitude, longitude], popup=f"{latitude}, {longitude}").add_to(map_world)
        return map_world

    @classmethod
    def point_placer(cls, ip):
        try:
            lat, lon = IPInfo.coordinates(ip)
            map_with_point = cls.create_map(float(lat), float(lon))
            map_with_point.save(str(MAP_PATH.resolve()))
            print("[+] Creating the map...")
            print(f"[+] Map created at path: {MAP_PATH.resolve()}")
        except Exception as e:
            print(f"[!] Error while creating the map: {e}")

class PastebinChecker:
    @staticmethod
    def check_link(link, ip, result_links):
        try:
            raw_link = link.replace("https://pastebin.com/", "https://pastebin.com/raw/")
            response = requests.get(raw_link)
            if ip.lower() in response.text.lower():
                result_links.append(raw_link)
        except Exception:
            print("[!] Your IP address may be rate-limited or banned. Retry later or change your IP.")

    @classmethod
    def dump(cls, ip):
        found_links = []
        search_query = f"site:pastebin.com \"{ip}\""
        try:
            print("[+] Searching Pastebin for IP...")
            _, google_links = Google(
                search=search_query,
                userAgent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/91.0.4472.124 Safari/537.36"
            )
            for link in google_links:
                cls.check_link(link, ip, found_links)
            if not found_links:
                print("\nPastebin | ❌ | The IP address provided does not appear in any paste.")
            else:
                print("\nPastebin | ✔️ | Found the following links:")
                for link in found_links:
                    print("└──", link)
            print()
        except Exception as e:
            print("[!] Error occurred during Pastebin search:", str(e))

class VPNChecker:
    @staticmethod
    def check(ip):
        url = "https://api.protonmail.ch/vpn/logicals"
        headers = {"User-Agent": get_random_ua()}
        try:
            response = requests.get(url, headers=headers)
            if ip in response.text:
                return "Proton   | ✔️ | This IP address is currently affiliated with ProtonVPN."
            else:
                return "Proton   | ❌ | This IP address is not currently affiliated with ProtonVPN."
        except Exception:
            return "[-] Proton rate limit or error occurred."


class IPProbability:
    def __init__(self, ip):
        self.ip = ip

    def loader(self):
        _, city_api = IPApi.lookup(self.ip)
        _, city_info, _ = IPInfo.look(self.ip)
        _, city_whois = IPWhois.lok(self.ip)
        return city_api.upper(), city_info.upper(), city_whois.upper()

    def compare_cities(self, city1, city2, city3):
        if city1 == city2 == city3:
            return "++ " + city1.lower()
        elif city1 != city2 == city3:
            return "+ " + city1.lower()
        else:
            return "- " + city1.lower()

    def probability(self):
        city_api, city_info, city_whois = self.loader()
        print("\n[+] Location Confidence Analysis")
        print("----------------------------------------")
        print(f"  ip-api     : {city_api}")
        print(f"  ipinfo     : {city_info}")
        print(f"  ipwho.is   : {city_whois}")
        print("----------------------------------------")
        print("Probabilities:")
        print(f"  {self.compare_cities(city_api, city_info, city_whois)}")
        print(f"  {self.compare_cities(city_info, city_api, city_whois)}")
        print(f"  {self.compare_cities(city_whois, city_api, city_info)}\n")
        print("[+] Location confidence analysis completed.\n")


def run_bjw_ip_tracker():
    while True:
        print("""
         =========================================================================================================================================
        |= .______          __  ____    __    ____  __  .______   .___________..______          ___       ______  __  ___  _______ .______       =|
        |= |   _  \        |  | \   \  /  \  /   / |  | |   _  \  |           ||   _  \        /   \     /      ||  |/  / |   ____||   _  \      =| 
        |= |  |_)  |       |  |  \   \/    \/   /  |  | |  |_)  | `---|  |----`|  |_)  |      /  ^  \   |  ,----'|  '  /  |  |__   |  |_)  |     =| 
        |= |   _  <  .--.  |  |   \            /   |  | |   ___/      |  |     |      /      /  /_\  \  |  |     |    <   |   __|  |      /      =|
        |= |  |_)  | |  `--'  |    \    /\    /    |  | |  |          |  |     |  |\  \----./  _____  \ |  `----.|  .  \  |  |____ |  |\  \----. =|
        |= |______/   \______/      \__/  \__/     |__| | _|          |__|     | _| `._____/__/     \__\ \______||__|\__\ |_______|| _| `._____| =|
         =========================================================================================================================================                                                                                                                                     
        """)
        
        ip_input = input("Enter an IP address or type 'exit' to exit: ").strip()
        if not ip_input:
            print("===========================")
            print("[-] No IP address provided.")
            print("===========================")
            continue
        if ip_input.lower() == "exit":
            print("==========")
            print("Exiting...")
            print("==========")
            sys.exit(0)
        if ip_input.lower() == "help":
            print("=========================================")
            print("Usage: Enter a valid IP address to track.")
            print("=========================================")
            continue

        ip = ip_input.split()[0]
        
        ip_regex = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_regex, ip):
            print("==============================")
            print("[-] Invalid IP address format.")
            print("==============================")
            continue
        
        print("\n========== IP Tracker ==========")
        print(f"Tracking IP: {ip}")
        print("================================\n")
        Pinger.ping(ip)
        print("Use a tool like SpiderCrawler to gather more information on vulnerabilities, open ports, and more.")
        vpn_status = VPNChecker.check(ip)
        print("\n=== ip-api Details ===")
        print_ip_api_details(ip)
        ipinfo_output, _, _ = IPInfo.look(ip)
        ipwhois_output, _ = IPWhois.lok(ip)
        ipapi_output, _ = IPApi.lookup(ip)
        org_data = IPWhois.resolv_org(ip) 
        print("\n=== Aggregated API Info ===")
        print(ipapi_output)
        print(ipwhois_output)
        if org_data:
            print("Organization (resolved):", org_data.strip())
        print(ipinfo_output)
        print("\n=== Supplementary Data ===")
        print("VPN Check:", vpn_status)
        PastebinChecker.dump(ip)
        IPProbability(ip).probability()
        print("=== Mapping IP Location ===")
        MapCreator.point_placer(ip)
        print("================================\n")
        print("[+] IP tracking completed.\n")

if __name__ == "__main__":
    run_bjw_ip_tracker()