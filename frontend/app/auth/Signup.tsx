import { View, Text, Pressable, Image, TextInput } from "react-native";
import React from "react";
import { router, Stack } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import CustomHeader from "@/components/CustomHeader";
import { icons } from "@/constants/icon";

const Signup = () => {
  return (
    <SafeAreaView className="bg-dark-bg flex-1">
      <Stack.Screen options={{ headerShown: false }} />
      <CustomHeader />

      {/* Close button */}
      <Pressable
        className="py-4 px-8"
        onPress={() => router.back()}
      >
        <Image
          source={icons.cross}
          className=""
          resizeMode="contain"
        />
      </Pressable>

      <Text className="text-white text-left text-4xl pl-8 pt-6 font-GeoA_medium">
        Sign Up
      </Text>

      {/* username/email */}
      <View className="w-full items-center mt-4">
        <View className="flex-row items-center justify-between bg-grey-1 rounded-full px-2 py-2 mt-16 w-11/12 max-w-lg">
          <TextInput
            className="text-grey-text1 text-left text-2xl font-Geo_thin ml-4 flex-1 py-1"
            placeholder="Email Or Username"
            placeholderTextColor="#A3A3A3"
          />
        </View>
      </View>
      {/* password */}
      <View className="w-full items-center mt-6">
        <View className="flex-row items-center justify-between bg-grey-1 rounded-full px-2 py-2 w-11/12 max-w-lg">
          <TextInput
            className="text-grey-text1 text-left text-2xl font-Geo_thin ml-4 flex-1 py-1"
            placeholder="Password"
            placeholderTextColor="#A3A3A3"
          />
        </View>
      </View>

      <Text className="text-white text-left text-lg pl-8 pt-6 font-Geo_extralight">
        Returning User? &nbsp;
        <Text
          className="text-blue"
          onPress={() =>
            router.push({
              pathname: "/auth/Login",
            })
          }
        >
          Log In
        </Text>
      </Text>

      <View className="w-full items-center mt-14">
        <Pressable
          onPress={() =>
            router.push({
              pathname: "/search/SearchPage",
            })
          }
          className="flex-row items-center justify-center bg-green rounded-full px-2 py-2"
        >
          <Text className="text-dark-bg text-left text-2xl font-Geo_medium mx-32 py-1">
            Create Account
          </Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
};

export default Signup;
