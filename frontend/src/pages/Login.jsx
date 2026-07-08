import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

import { login, currentUser } from "../services/auth";
import { useAuth } from "../context/AuthContext";

function Login() {

  const navigate = useNavigate();

  const { refreshUser } = useAuth();

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  useEffect(() => {

    const checkUser = async () => {

      try {

        await currentUser();

        navigate("/dashboard", {

          replace: true

        });

      } catch {

      }

    };

    checkUser();

  }, [navigate]);

  const handleLogin = async (e) => {

    e.preventDefault();

    setError("");

    setLoading(true);

    try {

      await login(

        email,

        password

      );

      await refreshUser();

      navigate("/dashboard");

    } catch (err) {

      console.error(err);

      setError(

        err.message ||

        "Login failed"

      );

    }

    finally {

      setLoading(false);

    }

  };

  return (

    <div className="min-h-screen bg-gray-100 flex items-center justify-center">

      <div className="bg-white shadow-xl rounded-xl p-10 w-full max-w-md">

        <h1 className="text-3xl font-bold text-center text-blue-700">

          Customer Support AI

        </h1>

        <p className="text-center text-gray-500 mt-2">

          Sign in to continue

        </p>

        <form

          onSubmit={handleLogin}

          className="mt-8 space-y-5"

        >

          <div>

            <label className="block mb-2 font-medium">

              Email

            </label>

            <input

              type="email"

              value={email}

              onChange={(e)=>

                setEmail(e.target.value)

              }

              placeholder="Enter email"

              className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"

              required

            />

          </div>

          <div>

            <label className="block mb-2 font-medium">

              Password

            </label>

            <input

              type="password"

              value={password}

              onChange={(e)=>

                setPassword(e.target.value)

              }

              placeholder="Enter password"

              className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"

              required

            />

          </div>

          {

            error && (

              <div className="text-red-600">

                {error}

              </div>

            )

          }

          <button

            type="submit"

            disabled={loading}

            className="w-full bg-blue-700 text-white py-3 rounded-lg hover:bg-blue-800 transition"

          >

            {

              loading

                ? "Signing In..."

                : "Login"

            }

          </button>

        </form>

        <div className="mt-6 text-center">

          <p className="text-gray-600">

            Don't have an account?

          </p>

          <Link

            to="/signup"

            className="text-blue-700 font-semibold hover:underline"

          >

            Create Account

          </Link>

        </div>

      </div>

    </div>

  );

}

export default Login;