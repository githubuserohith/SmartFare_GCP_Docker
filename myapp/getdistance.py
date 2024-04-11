import geopy.distance

coords_1 = (12.9187392,77.6492451)
coords_2 = (12.9781494,77.5510754)

print (geopy.distance.geodesic(coords_1, coords_2).km)
