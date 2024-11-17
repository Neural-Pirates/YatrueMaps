import React from "react";
import { Text, Image, View, Pressable } from "react-native";
import BottomSheet from "@gorhom/bottom-sheet";
import { router } from "expo-router";
import { icons } from "@/constants/icon";

interface EYRProps {
  snapPoints: string[]; // Snap points for the BottomSheet
  sheetRef: React.RefObject<BottomSheet>; // Ref for BottomSheet
}

const EYR: React.FC<EYRProps> = ({ snapPoints, sheetRef }) => {
  return (
    <BottomSheet
      ref={sheetRef}
      snapPoints={snapPoints}
      enableDynamicSizing={false}
      style={{ marginTop: -40 }}
      backgroundStyle={{ backgroundColor: "#121212" }}
      handleIndicatorStyle={{
        backgroundColor: "#585858",
        width: "45%",
        marginTop: 10,
      }}
    >
      <Text className="text-white text-left text-4xl pl-8 pt-6 font-Geo_medium">
        Enter Your Route
      </Text>
      <View className="items-center mt-6">
        {/* your location */}
        <View className="flex-row items-center">
          <Image
            className="mr-4"
            source={icons.routeStart}
          />
          <View className="flex-row items-center justify-between bg-grey-1 rounded-full px-2 py-1">
              {/* TextInput for Search */}
              <Text className="text-white text-left text-2xl font-Geo_thin ml-4 mr-44 py-1">
                Your Location
              </Text>
          </View>
        </View>

        {/* destination */}
        <View className="flex-row items-center mt-6">
          <Image
            className="mr-4"
            source={icons.routeDestination}
          />
          <View className="items-center">
            <Pressable
              onPress={() =>
                router.push({
                  pathname: "/search/SearchPage",
                })
              }
              className="flex-row items-center justify-between bg-grey-1 rounded-full px-2 py-1"
            >
              {/* TextInput for Search */}
              <Text className="text-grey-text1 text-left text-2xl font-Geo_thin ml-4 mr-44 py-1">
                Destination? &nbsp;
              </Text>
            </Pressable>
          </View>
        </View>
      </View>
    </BottomSheet>
  );
};

export default EYR;
