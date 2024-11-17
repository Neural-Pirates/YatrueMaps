// Comment.tsx
import React from "react";
import { View, Text, Image, FlatList, Pressable } from "react-native";
import { icons } from "@/constants/icon";

// Define the Comment interface
interface CommentProps {
  comment: {
    commentId: number;
    username: string;
    time: string;
    text: string;
    upvoteCount: number;
    label?: boolean; // Optional label property, like "In The Area"
    image?: string; // Optional image property for comments with an image
    replies?: CommentProps[]; // Array of replies for nested comments
  };
}

const Comment: React.FC<CommentProps> = ({ comment }) => (

  <>
    <View className="flex-row bg-dark-bg my-5 pl-6">
      {/* Divider bar */}
      <View className="bg-grey-1 w-0.5 h-full" />
      <View className=" p-4">
        {/* User avatar, username, and time */}
        <View className="flex-row items-center mt-2">
          <Image
            source={icons.dummyUserIcon}
            className="rounded-full"
          />
          <Text className="text-white ml-2 font-Geo_extralight text-lg">
            {comment.username}
          </Text>
          <Text className="text-grey-text1 ml-2 font-Geo_extralight text-sm">
            •
          </Text>
          <Text className="text-grey-text1 ml-2 font-Geo_extralight text-lg">
            {comment.time}
          </Text>

          {comment.label && (
            <View className="flex-row items-center ml-2 py-1 bg-green rounded-full">
              <Image
                source={icons.inTheArea}
                className="ml-2"
              />
              <Text className="text-grey-4 font-Geo_light text-sm px-2">
                In The Area
              </Text>
            </View>
          )}
        </View>

        {/* reply, upvote, downvote */}
        <View className="my-5">
          <Text className="text-white font-Geo_extralight text-lg">
            {comment.text}
          </Text>
        </View>

        <View className="flex-row items-center mt-2 border-grey-3">
          <Pressable onPress={() => console.log("Upvoted!")}>
            <Image source={icons.upvote} />
          </Pressable>
          <Text className="text-white ml-2 font-Geo_regular text-xl">
            {comment.upvoteCount}
          </Text>
          <Pressable
            className="ml-3"
            onPress={() => console.log("Downvoted!")}
          >
            <Image source={icons.downvote} />
          </Pressable>

          <Pressable
            className="ml-4 flex-row items-center"
            onPress={() => {console.log("reply");
              // Add your reply logic here
              // For example, you can navigate to a reply screen or open a reply input box
                // Add your reply logic here
                // For example, you can navigate to a reply screen or open a reply input box
                const [replyText, setReplyText] = React.useState("");
                const [replies, setReplies] = React.useState(comment.replies || []);

                const handleReply = () => {
                const newReply = {
                  commentId: Date.now(), // Generate a unique ID for the new reply
                  username: "currentUser", // Replace with the current user's username
                  time: new Date().toLocaleTimeString(),
                  text: replyText,
                  upvoteCount: 0,
                };
                setReplies([...replies, newReply]);
                setReplyText("");
                };

                return (
                <View>
                  <TextInput
                  value={replyText}
                  onChangeText={setReplyText}
                  placeholder="Write a reply..."
                  className="text-white bg-grey-2 p-2 rounded"
                  />
                  <Pressable onPress={handleReply}>
                  <Text className="text-white ml-2 font-Geo_regular text-xl">
                    Submit
                  </Text>
                  </Pressable>
                  <FlatList
                  data={replies}
                  keyExtractor={(item) => item.commentId.toString()}
                  renderItem={({ item }) => (
                    <Comment comment={item} /> // Recursive call to render nested replies
                  )}
                  />
                </View>
                );

            }}
          >
            <Image source={icons.reply} />
            <Text className="text-white ml-2 font-Geo_regular text-xl">
              Reply
            </Text>
          </Pressable>

        </View>

        {/* replies */}
        <View className="flex-1 mt-2">
          {/* Render Nested Replies if replies array is not empty */}
          {comment.replies && (
            <FlatList
              data={comment.replies}
              keyExtractor={(item) => item.commentId}
              renderItem={({ item }) => (
                <Comment comment={item} /> // Recursive call to render nested replies
              )}
            />
          )}
        </View>
      </View>
    </View>
  </>

);

export default Comment;
