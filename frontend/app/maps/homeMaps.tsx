import React, { useEffect, useRef, useState } from 'react';
import Mapbox, { Camera, LineLayer, MapView, PointAnnotation, ShapeSource } from '@rnmapbox/maps';
import route from '../data/route.json'
import { ActivityIndicator, StyleSheet, View, Image } from 'react-native';


interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: Array<{
    type: 'Feature';
    properties: any;
    geometry: any;
  }>;
}
import { useLocation } from '../state/locationState';
import { useDestination } from '../state/destinationState';
import { getLocationState } from '../search/constLocation';
import { icons } from '@/constants/icon';

const styles = StyleSheet.create({
  page: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#F5FCFF"
  },
  map: {
    flex: 1
  },
  marker: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: 'red'
  },
  destinationMarker: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: 'blue'
  },
  mapBox: {},
  loader: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center'
  }
});

let coordinatesList: any[] = [];

for (const data of route) {
  coordinatesList.push([data['lat'], data['long']]);
  console.log(data['lat'], data['long'], 'datac console');
}

console.log(coordinatesList, 'coordinatesList');


function HomeMaps() {
  const location = getLocationState();

  useEffect(() => {
    console.log("Current Global Coordinates:", location.coordinates);
  }, []);

  Mapbox.setAccessToken('pk.eyJ1IjoiamFtZXNpaS1iIiwiYSI6ImNtM2VuZWxsdzBka3YycnF1d2V5eTdmZmMifQ.p8ymCgGRd3MY4vbRyKGMVw');

  const currentLocation = useLocation();
  const { destination } = useDestination();
  const [routeGeoJSON, setRouteGeoJSON] = useState<GeoJSONFeatureCollection | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const camera = useRef<Camera>(null);

  const calculateBounds = (geoJSON: GeoJSONFeatureCollection) => {
    const coordinates = geoJSON.features[0].geometry.coordinates;
    let minLng = Infinity;
    let maxLng = -Infinity;
    let minLat = Infinity;
    let maxLat = -Infinity;

    coordinates.forEach((coord: [number, number]) => {
      const [lng, lat] = coord;
      minLng = Math.min(minLng, lng);
      maxLng = Math.max(maxLng, lng);
      minLat = Math.min(minLat, lat);
      maxLat = Math.max(maxLat, lat);
    });

    return [[minLng, minLat], [maxLng, maxLat]];
  };

  useEffect(() => {
    const fetchRoute = async () => {
      console.log('current, destination', currentLocation, destination);

      if (!destination) { return; }
      setIsLoading(true);

      try {
        if (!location?.coordinates || !currentLocation) {
          return;
        }

        const url = `https://api.mapbox.com/directions/v5/mapbox/driving/${currentLocation[0]},${currentLocation[1]};${location.coordinates[0]},${location.coordinates[1]}?overview=full&geometries=geojson&access_token=pk.eyJ1IjoiamFtZXNpaS1iIiwiYSI6ImNtM2VuZWxsdzBka3YycnF1d2V5eTdmZmMifQ.p8ymCgGRd3MY4vbRyKGMVw`;
        // console.log('Request URL:', url);

        const response = await fetch(url);
        console.log(response.body);

        if (!response.ok) {
          throw new Error(`API request failed with status ${response.status}`);
        }

        const data = await response.json();
        // console.log('API response:', data);

        if (data.routes && data.routes.length > 0 && data.routes[0].geometry) {
          const lineStringGeoJSON: GeoJSONFeatureCollection = {
            type: 'FeatureCollection',
            features: [
              { type: 'Feature', properties: {}, geometry: data.routes[0].geometry },
            ],
          };
          setRouteGeoJSON(lineStringGeoJSON);
        } else {
          console.log('No valid route data found in response:', data);
        }
      } catch (error) {
        console.error('Failed to fetch route:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRoute();
  }, [currentLocation, destination]);

  useEffect(() => {
    if (routeGeoJSON) {
      const bounds = calculateBounds(routeGeoJSON);
      if (camera.current) {
        camera.current.fitBounds(bounds[0], bounds[1], {
          paddingTop: 50,
          paddingBottom: 50,
          paddingLeft: 50,
          paddingRight: 50
        });
      }
    }
  }, [routeGeoJSON]);

  return (
    <View style={{ flex: 1 }}>
      <MapView
        style={styles.map}
        localizeLabels
        attributionEnabled={false}
        styleURL={Mapbox.StyleURL.Street}
        logoEnabled={false}
      >
        {currentLocation && <Camera ref={camera} centerCoordinate={currentLocation} zoomLevel={9} />}
        {currentLocation && !location.coordinates && (
          <PointAnnotation id="currentLocation" coordinate={currentLocation}>
            <View style={styles.marker} />
          </PointAnnotation>
        )}
        {destination && location.coordinates && (
          <PointAnnotation id="destination" coordinate={location.coordinates}>
            <View style={styles.destinationMarker} />
          </PointAnnotation>
        )}
        {routeGeoJSON && (
          <ShapeSource id="routeLine" shape={routeGeoJSON}>
            <LineLayer
              id="lines"
              style={{
                lineColor: 'brown',
                lineWidth: 5,
              }}
            />
          </ShapeSource>
        )}

        {coordinatesList.map((coordinate, index) => (
          <PointAnnotation key={`marker-${index}`} id={`marker-${index}`} coordinate={coordinate}>
            <View style={styles.marker} />
            <Image source={icons.discussionMarker} />

          </PointAnnotation>
        ))}
      </MapView>

      {isLoading && (
        <View style={styles.loader}>
          <ActivityIndicator size="large" color="#007AFF" />
        </View>
      )}
    </View>
  );
};

export default HomeMaps;
