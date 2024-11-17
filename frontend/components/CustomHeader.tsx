import { View, Text, Pressable, Image } from "react-native";
import React from "react";
import { icons } from "../constants/icon";
import { router } from "expo-router";

const CustomHeader = () => {
  const UserLogin = () => {
    router.push({
      pathname: "/auth/Login",
    });
  };

  return (
    <View className="flex-row items-center justify-between px-8 py-2 bg-dark-bg z-40">
      {/* Logo section */}
      <Pressable
        className="flex-row items-center"
        onPress={() => router.back()}
      >
        <Image
          source={icons.yatrueLogoText}
          className="h-14"
          resizeMode="contain"
        />
      </Pressable>

      {/* Login/SignUp section */}
      <Pressable
        className="flex-row items-center h-14"
        onPress={() => {
          router.push('/auth/ProfilePage')
        }}
      >

        <Image
          source={icons.dummyUserIcon}
          className="h-14 rounded-full"
          resizeMode="contain"
        />
      </Pressable>
    </View>
  );
};

export default CustomHeader;
