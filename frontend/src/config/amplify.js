import { Amplify } from "aws-amplify";

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: "us-east-1_SC2CeNSNP",
      userPoolClientId: "1mkg3l7u8kvt8iqti3f8b3gus3",
    },
  },
});