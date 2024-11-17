import React, { useState } from "react";
import { View, Text, Pressable, Image } from "react-native";
import { useRouter } from "expo-router";
import { icons } from "../../constants/icon";

// Define the post properties
interface PostProps {
  post: {
    postId: string;
    username: string;
    time: string;
    title: string;
    image?: string;
    textContent: string;
    upvoteCount: number;
    downVoteCount?: number;
    commentCount: number;
    comments?: { replies?: any[] }[];
  };
}

const Post: React.FC<PostProps> = ({ post }) => {
  const [upvote, setUpvote] = useState<number>(post.upvoteCount);
  const [downVote, setDownVote] = useState<number>(post.downVoteCount || 0);
  const [hasUpvoted, setHasUpvoted] = useState<boolean>(false);
  const [hasDownvoted, setHasDownvoted] = useState<boolean>(false);
  const router = useRouter();

  const navigateToDetails = () => {
    router.push({
      pathname: "/posts/PostDetails",
      params: {
        postId: post.postId,
        username: post.username,
        time: post.time,
        title: post.title,
        image: post.image,
        textContent: post.textContent,
        upvoteCount: post.upvoteCount,
        commentCount: post.commentCount,
        comments: JSON.stringify(post.comments),
      },
    });
  };

  const handleUpvote = () => {
    if (!hasUpvoted) {
      setUpvote(upvote + 1);
      setHasUpvoted(true);
      if (hasDownvoted) {
        setDownVote(downVote - 1); // Remove downvote if user switches to upvote
        setHasDownvoted(false);
      }
    } else {
      setUpvote(upvote - 1);
      setHasUpvoted(false);
    }
  };

  const handleDownvote = () => {
    if (!hasDownvoted) {
      setDownVote(downVote + 1);
      setHasDownvoted(true);
      if (hasUpvoted) {
        setUpvote(upvote - 1); // Remove upvote if user switches to downvote
        setHasUpvoted(false);
      }
    } else {
      setDownVote(downVote - 1);
      setHasDownvoted(false);
    }
  };

  return (
    <Pressable onPress={navigateToDetails} className="mt-6">
      {/* Divider bar */}
      <View className="bg-grey-1 h-0.5" />

      {/* Post content */}
      <View className="pl-8 pt-4">
        {/* User avatar, username, and time */}
        <View className="flex-row items-center">
          <Image source={icons.dummyUserIcon} className="rounded-full" />
          <Text className="text-white ml-2 font-Geo_extralight text-lg">{post.username}</Text>
          <Text className="text-grey-text1 ml-2 font-Geo_extralight text-sm">•</Text>
          <Text className="text-grey-text1 ml-2 font-Geo_extralight text-lg">{post.time}</Text>
        </View>

        {/* Post title with wrapping */}
        <View className="my-5">
          <Text
            className="text-white font-Geo_regular text-2xl"
            numberOfLines={2}
            ellipsizeMode="tail"
            style={{ flexWrap: "wrap", flexShrink: 1 }}
          >
            {post.title}
          </Text>
        </View>

        {/* Upvote / Downvote and Comment Section */}
        <View className="flex-row">
          <View className="flex-row items-center border-2 rounded-full px-4 py-1 border-grey-3">
            <Pressable onPress={handleUpvote}>
              <Image source={icons.upvote} />
            </Pressable>
            <Text className="text-white ml-2 font-Geo_regular text-xl">{upvote}</Text>
            <View className="ml-3 border border-grey-3 h-8" />
            <Pressable onPress={handleDownvote} className="ml-3">
              <Image source={icons.downvote} />
            </Pressable>
          </View>

          <View className="flex-row items-center border-2 rounded-full px-4 py-1.5 border-grey-3 ml-2">
            <Pressable onPress={() => console.log("Commented!")}>
              <Image source={icons.comment} />
            </Pressable>
            <Text className="text-white ml-3 font-Geo_regular text-xl">{post.commentCount}</Text>
          </View>
        </View>
      </View>
    </Pressable>
  );
};

export default Post;
