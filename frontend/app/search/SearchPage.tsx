import {
  View,
  TextInput,
  Text,
  Pressable,
  Image,
  FlatList,
  ActivityIndicator,
} from "react-native";
import React, { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import CustomHeader from "../../components/CustomHeader";
import { router, Stack } from "expo-router";
import { icons } from "@/constants/icon";
import Query from "./Query";
import axios from "axios";
import { useLocation } from "../state/locationState";
import { useDestination } from "../state/destinationState"; // Import the destination hook
import calculateDistance from "../function/distance";

const SearchPage = () => {
  const [userType, setUserType] = useState<string>("f");
  const [queryData, setQueryData] = useState<any[]>([]); // Store fetched query data
  const [loading, setLoading] = useState<boolean>(false); // Track loading state
  const currentLocation = useLocation(); // Use the location hook at the top level
  const { destination, updateDestination } = useDestination(); // Use the destination hook

  const handleSearch = async (text: string) => {
    if (!text || !currentLocation) return; // Ensure location is available before proceeding

    setLoading(true);
    console.log("Sending request to the server...");

    try {
      const response = await axios.get(
        `https://api.mapbox.com/search/searchbox/v1/suggest?access_token=pk.eyJ1IjoiamFtZXNpaS1iIiwiYSI6ImNtM2VuZWxsdzBka3YycnF1d2V5eTdmZmMifQ.p8ymCgGRd3MY4vbRyKGMVw&q=${text}&session_token=sk.eyJ1IjoiamFtZXNpaS1iIiwiYSI6ImNtM2VuZ3Y0bDBjeXkybHF4eTFsZHRvZ2QifQ.OOUwqNuwojaj09Y5Z7fI2Q`
      );

      const suggestions = response.data.suggestions;
      console.log("All suggestion names:");

      const locationData = await Promise.all(
        suggestions.map(async (suggestion: { mapbox_id: any; place_formatted: any; name: any; }) => {
          const mapboxID = suggestion.mapbox_id;

          // Fetch location details using the mapbox ID
          const locationResponse = await axios.get(
            `https://api.mapbox.com/search/searchbox/v1/retrieve/${mapboxID}?session_token=sk.eyJ1IjoiamFtZXNpaS1iIiwiYSI6ImNtM2VuZ3Y0bDBjeXkybHF4eTFsZHRvZ2QifQ.OOUwqNuwojaj09Y5Z7fI2Q&access_token=pk.eyJ1IjoiamFtZXNpaS1iIiwiYSI6ImNtM2VuZWxsdzBka3YycnF1d2V5eTdmZmMifQ.p8ymCgGRd3MY4vbRyKGMVw`
          );

          const location = locationResponse.data.features[0];
          const [longitude, latitude] = location.geometry.coordinates;

          // Calculate distance from current location
          const [currentLongitude, currentLatitude] = currentLocation;
          const distance = calculateDistance(
            currentLatitude,
            currentLongitude,
            latitude,
            longitude
          );

          return {
            locationName: suggestion.name,
            cityName: suggestion.place_formatted,
            coordinates: [longitude, latitude], // Include coordinates for later use
            Distance: `${distance.toFixed(2)} km`,
          };
        })
      );

      // Sort by distance
      const sortedLocationData = locationData.sort((a, b) => {
        const distanceA = parseFloat(a.Distance.split(" ")[0]);
        const distanceB = parseFloat(b.Distance.split(" ")[0]);
        return distanceA - distanceB; // Sort in ascending order
      });

      setQueryData(sortedLocationData); // Update state with sorted location data
    } catch (error) {
      console.error("Error received:", error);
    } finally {
      setLoading(false);
      console.log("Request process completed.");
    }
  };

  return (
    <SafeAreaView className="bg-dark-bg flex-1">
      <Stack.Screen options={{ headerShown: false }} />
      <CustomHeader />

      <View>
        {/* Search bar */}
        <View className="absolute top-4 w-full items-center">
          <Pressable
            onPress={() => {
              console.log("press location button");
              router.push({
                pathname: "/search/SearchPage",
              });
            }}
            className="flex-row items-center justify-between bg-grey-1 rounded-full px-2 py-2 w-11/12 max-w-lg"
          >
            {/* TextInput for Search */}
            <TextInput
              className="text-white text-left text-2xl font-Geo_thin ml-4 flex-1 py-1"
              placeholder="Search Locations"
              placeholderTextColor="#A3A3A3"
              onChangeText={(text) => handleSearch(text)} // Trigger search
            />
            <Image className="mr-4" source={icons.search} />
          </Pressable>
        </View>
      </View>

      <View className="flex-1 mt-20">
        <View className="bg-dark-bg flex-1 pt-4">
          <Text className="text-white text-left text-4xl pl-8 pt-6 font-GeoA_extralight">
            Possible Matches
          </Text>

          {/* Show loading indicator or data */}
          {loading ? (
            <ActivityIndicator size="large" color="#fff" />
          ) : (
            <FlatList
              data={queryData}
              keyExtractor={(item, index) => `${item.locationName}-${index}`} // Unique key
              renderItem={({ item }) => (
                <Query query={item} />
              )}
            />
          )}
        </View>
      </View>
    </SafeAreaView>
  );
};

export default SearchPage;
