function calculateDistance(
    currentLatitude: number,
    currentLongitude: number,
    latitude: number,
    longitude: number
  ): number {
    const toRadians = (degrees: number) => (degrees * Math.PI) / 180;
  
    const earthRadiusKm = 6371; // Earth's radius in kilometers
  
    const dLat = toRadians(latitude - currentLatitude);
    const dLon = toRadians(longitude - currentLongitude);
  
    const lat1 = toRadians(currentLatitude);
    const lat2 = toRadians(latitude);
  
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.sin(dLon / 2) * Math.sin(dLon / 2) * Math.cos(lat1) * Math.cos(lat2);
  
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  
    return earthRadiusKm * c;
  }

  export default calculateDistance;