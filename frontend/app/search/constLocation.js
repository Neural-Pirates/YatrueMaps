let locationState = {
    coordinates: null, // Initial value
  };
  
  export const getLocationState = () => locationState;
  
  export const updateLocationState = (coordinates) => {
    locationState.coordinates = coordinates;
    console.log("Location updated:", locationState.coordinates);
  };