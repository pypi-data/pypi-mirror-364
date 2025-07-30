# Heathcliff
A Command line Interface for pulling data from ArcGIS REST servers concurrently

# Installation
```bash
$ pip install heathcliff
```

TODO: Aliasing the command

# Usage
```bash
$ heathcliff 'https://<server>/MapServer/0' './out/*'

Using service name <Service Name>
Extracting Features:  100%|████████████████████████████████████████| 7/7 [00:14<00:36,  7.34s/it]
Building geojson: 100%|████████████████████████████████████████| 338/338 [00:13<00:00, 24.28it/s]

$ head ./out/<Service Name>.geojson
{"type": "FeatureCollection", "features": [{"type": "Feature", "id": 1, "geometry": {"type": "Polygon", "coordinates": [...
...
```
