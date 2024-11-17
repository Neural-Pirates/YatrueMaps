import posts from './data/threads.json';

import React, { useMemo, useRef, useCallback, useState } from "react";
import { Text, View, Image, Pressable } from "react-native";
import { icons } from "../constants/icon";
import { SafeAreaView } from "react-native-safe-area-context";
import CustomHeader from "../components/CustomHeader";
import BottomSheet from "@gorhom/bottom-sheet";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { useRouter } from "expo-router";
import HomeMaps from "./maps/homeMaps";
import PITA from "./bottomsheet/PITA";
import EYR from "./bottomsheet/EYR";
import { getRecentThread } from './posts/create/create';

export default function Index() {
  
  const router = useRouter();
  // hooks
  const pitaSheetRef = useRef<BottomSheet>(null);
  const eyrSheetRef = useRef<BottomSheet>(null);

  // Initial snap points for PITA and EYR
  const [pitaSnapPoints, setPitaSnapPoints] = useState(["33%", "100%"]);
  const [eyrSnapPoints, setEyrSnapPoints] = useState(["33%"]);

  const bottomSheetSnapAdjust = () => {
    // Check if PITA is open at 33%, and toggle the snap points for EYR
    if (pitaSnapPoints[0] === "33%") {
      // If PITA is at 33%, close PITA and open EYR at 33%
      setPitaSnapPoints(["1%"]); // Close PITA
      setEyrSnapPoints(["33%"]); // Open EYR at 33%
      eyrSheetRef.current?.expand();
    } else {
      // If PITA is not at 33%, it might be at 100%, so toggle it back to 33%
      if (pitaSnapPoints[1] === "100%") {
        setPitaSnapPoints(["33%", "100%"]); // Reset PITA to 33% and 100%
        pitaSheetRef.current?.expand();
      } else {
        // If PITA is at 1%, open it at 33%
        setPitaSnapPoints(["33%", "100%"]);
        pitaSheetRef.current?.expand();
      }
      eyrSheetRef.current?.close(); // Close EYR
    }
  };



  return (
    <SafeAreaView className="flex-1 bg-dark-bg">
      <CustomHeader />

      <GestureHandlerRootView style={{ flex: 1 }}>
        {/* map (its an image for now)*/}
        <View className="flex-1 items-center justify-start">
          <View className="w-full h-4/6">
            <HomeMaps />
            {/* search bar */}
            <View className="absolute top-2 w-full items-center">
              <Pressable
                onPress={() =>
                  router.push({
                    pathname: "/search/SearchPage",
                  })
                }
                className="flex-row items-center justify-between bg-grey-1 rounded-full px-2 py-2"
              >
                {/* TextInput for Search */}
                <Text className="text-grey-text1 text-left text-2xl font-Geo_thin ml-4 mr-44 py-1">
                  Search Locations
                </Text>
                <Image
                  className="mr-4"
                  source={icons.search}
                />
              </Pressable>
            </View>

            {/* Buttons overlay */}
            <View className="absolute top-24 right-4">
              {/* Location Button */}
              <Pressable
                onPress={() =>
                  console.log("location button")}
                className="w-16 h-16 bg-grey-1 rounded-full items-center justify-center mb-5"
              >
                <Image source={icons.centeredmap} />
              </Pressable>

              {/* Direction Button */}
              <Pressable
                onPress={bottomSheetSnapAdjust}
                className="w-16 h-16 bg-grey-1 rounded-full items-center justify-center mb-5"
              >
                <Image source={icons.directions} />
              </Pressable>

              {/* Add Button */}
              <Pressable
                onPress={() => {

                  router.push({
                    pathname: "./posts/create/CreatePage",
                  })



                }}
                className="w-16 h-16 bg-grey-1 rounded-full items-center justify-center mb-5"
              >
                <Image source={icons.create} />
              </Pressable>
            </View>
          </View>
        </View>

        {/* bottom sheet for popular posts*/}
        <EYR
          snapPoints={eyrSnapPoints}
          sheetRef={eyrSheetRef}
        />
        <PITA
          posts={[...getRecentThread(), ...posts]}
          title="Popular In the Area"
          snapPoints={pitaSnapPoints}
          sheetRef={pitaSheetRef}
          contentContainerStyle={{ backgroundColor: "#121212" }}
        />


      </GestureHandlerRootView>
    </SafeAreaView>
  );
}
