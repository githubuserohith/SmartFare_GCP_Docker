# import requests

# # Define the latitude and longitude
# latitude = 19.9719
# longitude = 74.5937

# # API endpoint URL
# url = f"https://api.geoapify.com/v1/geocode/reverse?lat={latitude}&lon={longitude}&apiKey=e94b687d30ed43cb8d1b70568bf97e21"

# # Send GET request to the API endpoint
# resp = requests.get(url)

# # Check if the request was successful
# if resp.status_code == 200:
#     # Parse JSON response
#     data = resp.json()
#     # Extract location information
#     address = data.get('features')[0].get('properties').get('address')
#     city = data.get('features')[0].get('properties').get('city')
#     country = data.get('features')[0].get('properties').get('country')
#     # Print the location details
#     print("Address:", address)
#     print("City:", city)
#     print("Country:", country)
# else:
#     print("Failed to retrieve location information. Status code:", resp.status_code)

from geopy.geocoders import Nominatim

# calling the nominatim tool
geoLoc = Nominatim(user_agent="GetPrayagraj")

# passing the coordinates
locname = geoLoc.reverse("12.9719, 77.5937")

# printing the address/location name
print(locname.address)

# import geocoder
# g = geocoder.ip('me')
# print(g.latlng)