import {
  createContext,
  useContext,
  useEffect,
  useState
} from "react";

import {
  currentUser,
  logout
} from "../services/auth";

const AuthContext = createContext();

export function AuthProvider({ children }) {

  const [user, setUser] = useState(null);

  const [role, setRole] = useState("");

  const [loading, setLoading] = useState(true);

  useEffect(() => {

    loadUser();

  }, []);

  const loadUser = async () => {

    try {

      const cognitoUser =
        await currentUser();

      setUser({

        ...cognitoUser,

        email: cognitoUser.signInDetails?.loginId

        });

      const token =
        localStorage.getItem("idToken");

      if (token) {

        const payload = JSON.parse(

          atob(token.split(".")[1])

        );

        const groups =
          payload["cognito:groups"];

        if (groups) {

          setRole(

            Array.isArray(groups)

              ? groups[0]

              : groups

          );

        } else {

          setRole("Customer");

        }

      }

    } catch {

      setUser(null);

    }

    setLoading(false);

  };

  const signOut = async () => {

    await logout();

    setUser(null);

    window.location.href = "/";

  };

  return (

    <AuthContext.Provider

      value={{

        user,

        role,

        loading,

        signOut,

        refreshUser: loadUser

      }}

    >

      {children}

    </AuthContext.Provider>

  );

}

export function useAuth() {

  return useContext(AuthContext);

}