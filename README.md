BJW IP Tracker
==========

Description
-----------
This Python script tracks and analyzes IP addresses using multiple data sources:
- Ping test to check if the IP responds
- ip-api.com for ISP, organization, location, timezone, and zip code
- ipinfo.io for hostname, ASN, location details
- ipwho.is for continent, country, region, city, ISP, and domain organization
- ProtonVPN API check for VPN affiliation
- Pastebin search for occurrences of the IP address
- Location confidence analysis comparing results from different APIs
- Map generation of IP location using Folium


Setup
-----
1. Install Python 3 if not already installed.
2. Place `useragents.txt` in the same directory as the script. This file should contain one User-Agent string per line.

Usage
-----
1. Run the script:
   ```
   python3.10 bjw_ip_tracker.py
   ```
2. Enter a valid IP address when prompted.
3. View the results printed in the console.
4. If a map is generated, open `world_map.html` in your browser to see the IP location.

Configuration
-------------
- `USER_AGENTS_FILE`: Path to `useragents.txt`.
- `MAP_PATH`: Path where the HTML map will be saved (`world_map.html` by default).

License
-------
GNU General Public License v3.0
