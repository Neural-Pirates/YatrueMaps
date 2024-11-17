/** @type {import('tailwindcss').Config} */
module.exports = {
  // NOTE: Update this to include the paths to all of your component files.
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        'green': "#77F700",
        'blue': "#00B1F7",
        'dark-bg': "#121212",
        'grey' : {
          "1": "#313131",
          "2": "#585858",
          "3": "#5C5C5C",
          "4": "#191919",
          "text1": "#A3A3A3",
        }
      },
      fontFamily: {
        Geo_thin: ["Geologica-Thin"],
        Geo_extralight: ["Geologica-ExtraLight"],
        Geo_light: ["Geologica-Light"],
        Geo_regular: ["Geologica-Regular"],
        Geo_medium: ["Geologica-Medium"],
        Geo_semibold: ["Geologica-SemiBold"],
        Geo_bold: ["Geologica-Bold"],
        Geo_extrabold: ["Geologica-ExtraBold"],
        Geo_black: ["Geologica-Black"],

        GeoA_thin: ["Geologica-Auto-Thin"],
        GeoA_extralight: ["Geologica-Auto-ExtraLight"],
        GeoA_light: ["Geologica-Auto-Light"],
        GeoA_regular: ["Geologica-Auto-Regular"],
        GeoA_medium: ["Geologica-Auto-Medium"],
        GeoA_semibold: ["Geologica-Auto-SemiBold"],
        GeoA_bold: ["Geologica-Auto-Bold"],
        GeoA_extrabold: ["Geologica-Auto-ExtraBold"],
        GeoA_black: ["Geologica-Auto-Black"],
      },
    },
  },
  plugins: [],
};
