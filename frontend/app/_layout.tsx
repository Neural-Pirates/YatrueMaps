import { SplashScreen, Stack } from "expo-router";
import { useFonts } from "expo-font";
import { useEffect } from "react";

import "../global.css";

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [fontsLoaded, error] = useFonts({
    "Geologica-Black": require("../assets/fonts/Geologica-Black.ttf"),
    "Geologica-Auto-Black": require("../assets/fonts/Geologica_Auto-Black.ttf"),
    "Geologica-Bold": require("../assets/fonts/Geologica-Bold.ttf"),
    "Geologica-ExtraBold": require("../assets/fonts/Geologica-ExtraBold.ttf"),
    "Geologica-ExtraLight": require("../assets/fonts/Geologica-ExtraLight.ttf"),
    "Geologica-Light": require("../assets/fonts/Geologica-Light.ttf"),
    "Geologica-Medium": require("../assets/fonts/Geologica-Medium.ttf"),
    "Geologica-Regular": require("../assets/fonts/Geologica-Regular.ttf"),
    "Geologica-SemiBold": require("../assets/fonts/Geologica-SemiBold.ttf"),
    "Geologica-Thin": require("../assets/fonts/Geologica-Thin.ttf"),

    "Geologica-Auto-Bold": require("../assets/fonts/Geologica_Auto-Bold.ttf"),
    "Geologica-Auto-ExtraBold": require("../assets/fonts/Geologica_Auto-ExtraBold.ttf"),
    "Geologica-Auto-ExtraLight": require("../assets/fonts/Geologica_Auto-ExtraLight.ttf"),
    "Geologica-Auto-Light": require("../assets/fonts/Geologica_Auto-Light.ttf"),
    "Geologica-Auto-Medium": require("../assets/fonts/Geologica_Auto-Medium.ttf"),
    "Geologica-Auto-Regular": require("../assets/fonts/Geologica_Auto-Regular.ttf"),
    "Geologica-Auto-SemiBold": require("../assets/fonts/Geologica_Auto-SemiBold.ttf"),
    "Geologica-Auto-Thin": require("../assets/fonts/Geologica_Auto-Thin.ttf"),
  });

  useEffect(() => {
    if (error) throw error;

    if (fontsLoaded) SplashScreen.hideAsync();
  }, [fontsLoaded, error]);

  if (!fontsLoaded && !error) return null;

  return (
    <Stack>
      <Stack.Screen
        name="index"
        options={{ headerShown: false }}
      />
    </Stack>
  );
}
