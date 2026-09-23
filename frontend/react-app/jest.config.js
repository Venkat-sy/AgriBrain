module.exports = {
  testEnvironment: "jsdom",
  transform: {
    "^.+\\.(js|jsx)$": "babel-jest",
  },
  moduleFileExtensions: ["js", "jsx"],
  testPathIgnorePatterns: ["/cypress/"],
  // No custom setup required; rely on default environment.
};
