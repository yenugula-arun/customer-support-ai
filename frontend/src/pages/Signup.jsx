import { useState } from "react";

import { Link, useNavigate } from "react-router-dom";

import { register } from "../services/auth";

function Signup() {

  const navigate = useNavigate();

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const handleSignup = async (e) => {

  e.preventDefault();

  setError("");

  if (password !== confirmPassword) {

    setError("Passwords do not match.");

    return;

  }

  setLoading(true);

  try {

    await register(email, password);

    sessionStorage.setItem(
      "signupEmail",
      email
    );

    navigate("/confirm-signup");

  } catch (err) {

    console.error(err);

    setError(

      err.message ||

      "Signup failed."

    );

  } finally {

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

          Create your account

        </p>

        <form
          onSubmit={handleSignup}
          className="mt-8 space-y-5"
        >

          <div>

            <label className="block mb-2 font-medium">

              Email

            </label>

            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border rounded-lg px-4 py-3"
            />

          </div>

          <div>

            <label className="block mb-2 font-medium">

              Password

            </label>

            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border rounded-lg px-4 py-3"
            />

          </div>

          <div>

            <label className="block mb-2 font-medium">

              Confirm Password

            </label>

            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) =>
                setConfirmPassword(e.target.value)
              }
              className="w-full border rounded-lg px-4 py-3"
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
            className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700"
          >

            {

              loading

                ? "Creating Account..."

                : "Create Account"

            }

          </button>

        </form>

        <p className="text-center mt-6">

          Already have an account?

          <Link

            to="/"

            className="text-blue-600 ml-2"

          >

            Login

          </Link>

        </p>

      </div>

    </div>

  );

}

export default Signup;