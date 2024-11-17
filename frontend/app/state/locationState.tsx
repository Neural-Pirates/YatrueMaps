import { useEffect, useState } from 'react';
import * as Location from 'expo-location';

export function useLocation() {
  const [currentLocation, setCurrentLocation] = useState<number[] | null>(null);

  useEffect(() => {
    const getLocation = async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        const location = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });
        const { latitude, longitude } = location.coords;
        setCurrentLocation([longitude, latitude]);
        // setCurrentLocation([-122.42, 37.78])
        console.log('current location', currentLocation)
      } else {
        console.error('Permission to access location was denied');
      }
    };

    getLocation();
  }, []);

  return currentLocation;
}
