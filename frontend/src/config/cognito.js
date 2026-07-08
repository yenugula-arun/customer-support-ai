import { CognitoUserPool } from "amazon-cognito-identity-js";

const poolData = {
  UserPoolId: "us-east-1_SC2CeNSNP",
  ClientId: "1mkg3l7u8kvt8iqti3f8b3gus3",
};

const UserPool = new CognitoUserPool(poolData);

export default UserPool;