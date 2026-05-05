
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primaryDark: "#010D00",
        backgroundLight: "#F2F2F2",
        neutralGray: "#A6A6A6",
        darkGray: "#595959",
        appBlack: "#0D0D0D",
      },
      borderRadius: {
        app: "20px",
      },
      boxShadow: {
        card: "0 14px 40px rgba(13, 13, 13, 0.08)",
      },
    },
  },
  plugins: [],
};
