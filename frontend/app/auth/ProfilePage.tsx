import { View, Text, Pressable, Image } from 'react-native';
import React from 'react';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router, Stack } from 'expo-router';
import CustomHeader from '@/components/CustomHeader';
import { icons } from '@/constants/icon';

const ProfilePage = () => {
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
        User Profile
      </Text>

      <View className="flex-1 items-center mt-10">
        <Image
          source={icons.dummyUserIcon}
          className="h-36 w-36 rounded-full"
          resizeMode="contain"
        />
        <Text className="text-white text-left text-3xl px-8 pt-6 font-GeoA_medium">
          Neural Pirates
        </Text>

        {/* Divider bar */}
        <View className="bg-grey-1 h-0.5 w-full mt-12" />

        <Text
          className="text-white text-left text-2xl py-6 font-GeoA_medium"
          onPress={() => console.log('logout')}
        >
          Logout
        </Text>

        <View className="bg-grey-1 h-0.5 w-full" />
      </View>
    </SafeAreaView>
  );
};

export default ProfilePage;