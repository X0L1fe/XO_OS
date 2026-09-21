console.log('Craco config loaded');
module.exports = {
  style: {
    postcss: {
      plugins: [
        require("tailwindcss"),
        require("autoprefixer"),
      ],
    },
  },
  webpack: {
    alias: {
      // If you have any aliases, you can add them here
    },
  },
};