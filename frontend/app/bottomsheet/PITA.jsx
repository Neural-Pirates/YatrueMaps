import React from "react";
import { Text, StyleSheet } from "react-native";
import BottomSheet, { BottomSheetFlatList } from "@gorhom/bottom-sheet";
import Post from "../posts/Post";

const PITA = ({
  posts,
  title,
  snapPoints,
  sheetRef,
  contentContainerStyle = { backgroundColor: "#121212" },
}) => {
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
      <Text className="text-white text-left text-4xl pl-8 pt-6 font-Geo_medium">{title}</Text>

      <BottomSheetFlatList
        data={posts}
        keyExtractor={(item) => item.postId}
        renderItem={({ item }) => <Post post={item} />}
        contentContainerStyle={contentContainerStyle}
      />
    </BottomSheet>
  );
};

export default PITA;
