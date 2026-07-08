import {
  signIn,
  signOut,
  signUp,
  confirmSignUp,
  resendSignUpCode,
  fetchAuthSession,
  getCurrentUser
} from "aws-amplify/auth";

export async function login(email, password) {

  try {

    await signIn({

      username: email,

      password,

      options: {

        authFlowType: "USER_PASSWORD_AUTH"

      }

    });

    const session = await fetchAuthSession();

    const idToken =
      session.tokens?.idToken?.toString();

    const accessToken =
      session.tokens?.accessToken?.toString();

    const refreshToken =
      session.tokens?.refreshToken?.toString();

    localStorage.setItem(
      "idToken",
      idToken
    );

    localStorage.setItem(
      "accessToken",
      accessToken
    );

    if (refreshToken) {

      localStorage.setItem(
        "refreshToken",
        refreshToken
      );

    }

    return session;

  } catch (error) {

    console.error(error);

    throw error;

  }

}

export async function register(
  email,
  password
) {

  try {

    return await signUp({

      username: email,

      password,

      options: {

        userAttributes: {

          email

        }

      }

    });

  } catch (error) {

    console.error(error);

    throw error;

  }

}

export async function confirmRegistration(
  email,
  code
) {

  try {

    return await confirmSignUp({

      username: email,

      confirmationCode: code

    });

  } catch (error) {

    console.error(error);

    throw error;

  }

}

export async function resendCode(
  email
) {

  try {

    return await resendSignUpCode({

      username: email

    });

  } catch (error) {

    console.error(error);

    throw error;

  }

}

export async function logout() {

  try {

    await signOut({

      global: true

    });

  } catch (error) {

    console.log(error);

  }

  localStorage.removeItem(
    "idToken"
  );

  localStorage.removeItem(
    "accessToken"
  );

  localStorage.removeItem(
    "refreshToken"
  );

}

export async function currentUser() {

  return await getCurrentUser();

}