import { View, Image, Text, Pressable, TextInput } from "react-native";
import path from "path";
import React from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { icons } from "@/constants/icon";
import { router, Stack } from "expo-router";
import CustomHeader from "@/components/CustomHeader";
import { setRecentThread } from "./create";
const CreatePage = () => {
  const [title, setTitle] = React.useState("");
  const [body, setBody] = React.useState("");

  const [time, setTime] = React.useState("");




  return (
    <SafeAreaView className="bg-dark-bg flex-1">
      <Stack.Screen options={{ headerShown: false }} />
      <CustomHeader />

      <View className="flex-row items-center justify-between mx-8">
        {/* Close button */}
        <Pressable
          className="py-4"
          onPress={() => router.back()}
        >
          <Image
            source={icons.cross}
            className=""
            resizeMode="contain"
          />
        </Pressable>
        <View className="items-center">
          <Pressable
            onPress={() => {
              const threadData = {
                postId:
                  Math.floor(Math.random() * 1000000),
                username: "Anonymous",
                time: 'now',
                title: title,
                image: "null",
                textContent: body,
                upvoteCount: 0,
                lat: 27.8560849,
                long: 84.5547724,
                commentCount: 0,
                comments: []
              };
              setRecentThread(threadData)

              alert("Post Created Successfully")
              router.push('/')
              //handle post here


            }
            }
            className="flex-row items-center justify-between bg-green rounded-full px-2 py-1"
          >
            <Text className="text-medium text-left text-lg font-Geo_semibold mx-4">
              Post
            </Text>
          </Pressable>
        </View>
      </View>
      <View className="flex-row mt-5 mx-8">
        <TextInput
          className="text-white text-left text-4xl font-Geo_semibold flex-1 py-1"
          placeholder="Title"
          onChangeText={(text) => setTitle(text)}
          placeholderTextColor="#A3A3A3"
        />
      </View>
      <View className="flex-row mt-5 mx-8">
        <TextInput
          className="text-white text-left text-2xl font-Geo_regular flex-1 py-1"
          placeholder="Body Text"
          placeholderTextColor="#A3A3A3"
          onChangeText={(text) => setBody(text)}

        />
      </View>
    </SafeAreaView>
  );
};

export default CreatePage;
