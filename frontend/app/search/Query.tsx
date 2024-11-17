import React, { useEffect } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { useDestination } from "../state/destinationState";
import { router } from "expo-router";
import { updateLocationState } from "./constLocation";

interface QueryProps {
  query: {
    coordinates: number[];
    queryId: String;
    locationName: String;
    cityName: String;
    Distance: String;
  };
}

const Query: React.FC<QueryProps> = ({ query }) => {
  const { destination, updateDestination } = useDestination();

  // Log the updated destination whenever it changes
  useEffect(() => {
    console.log("Updated Destination:", destination);
  }, [destination]);

  const navigateToRoute = () => {
    router.push({
      pathname: "/",
      params: {
        
      },
    });
  };

  return (
    <View className="mt-6">
      <View className="bg-grey-1 h-0.5 w-full" />
      <Pressable
        onPress={() => {
          console.log(`Selected: ${query.locationName}`);
          console.log("Destination beforehand", query.coordinates);
          updateDestination(query.coordinates);
          navigateToRoute();
          updateLocationState(query.coordinates);
          // navigation.goBack();
          // Update the destination
        }}
        className="mt-6 pl-6"
      >
        <View className="flex-row items-center justify-between mx-2">
          <Text className="text-white font-Geo_extralight text-2xl">
            {query.locationName}
          </Text>
          <Text className="text-grey-3 mr-2 mt-1 font-Geo_extralight text-sm">
            {query.Distance}
          </Text>
        </View>

        <Text className="text-grey-3 ml-2 mt-1 font-Geo_extralight text-sm">
          {query.cityName}
        </Text>
      </Pressable>
    </View>
  );
};

export default Query;
