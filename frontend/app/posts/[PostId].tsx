import { View, Text, Image, Pressable, FlatList } from "react-native";
import React from "react";
import { Stack, useLocalSearchParams, useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { icons } from "@/constants/icon";
import CustomHeader from "@/components/CustomHeader";
import Comment from "./Comment";

interface CommentProps {
  commentId: string;
  username: string;
  time: string;
  text: string;
  upvoteCount: number;
  label?: boolean;
  replies?: CommentProps[];
}

export default function PostDetails() {
  const router = useRouter();
  const params = useLocalSearchParams();

  // Parse the comments JSON string
  const comments: CommentProps[] = params.comments ? JSON.parse(params.comments as string) : [];

  return (
    <SafeAreaView className="bg-dark-bg flex-1">
      <Stack.Screen options={{ headerShown: false }} />
      <CustomHeader />

      <View className="flex-1">
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

        {/* Post content */}
        <View className="px-8 pt-4">
          <View className="flex-row items-center">
            <Image
              source={icons.dummyUserIcon}
              className="rounded-full"
            />
            <Text className="text-white ml-2 font-Geo_extralight text-lg">
              {params.username}
            </Text>
            <Text className="text-grey-text1 ml-2 font-Geo_extralight text-sm">•</Text>
            <Text className="text-grey-text1 ml-2 font-Geo_extralight text-lg">
              {params.time}
            </Text>
          </View>

          <View>
            <Text className="text-white font-Geo_regular text-2xl mt-4">
              {params.title}
            </Text>
            <Text className="text-white font-Geo_extralight text-xl mt-4">
              {params.textContent}
            </Text>
          </View>

          {/* Upvote / Downvote and Comment Section */}
          <View className="flex-row my-5">
            <View className="flex-row items-center border-2 rounded-full px-4 py-1 border-grey-3">
              <Pressable onPress={() => console.log("Upvoted!")}>
                <Image source={icons.upvote} />
              </Pressable>
              <Text className="text-white ml-2 font-Geo_regular text-xl">
                {params.upvoteCount}
              </Text>
            </View>
            <View className="flex-row items-center border-2 rounded-full px-4 py-1.5 border-grey-3 ml-2">
              <Pressable onPress={() => console.log("Commented!")}>
                <Image source={icons.comment} />
              </Pressable>
              <Text className="text-white ml-3 font-Geo_regular text-xl">
                {params.commentCount}
              </Text>
            </View>
          </View>
        </View>

        {/* Divider bar */}
        <View className="bg-grey-1 h-0.5 mb-5" />

        {/* Comments Section */}
        <View className="bg-black flex-1 pt-4">
          <FlatList
            data={comments}
            keyExtractor={(item) => item.commentId}
            renderItem={({ item }) => <Comment comment={item} />}
          />
        </View>
      </View>
    </SafeAreaView>
  );
}
