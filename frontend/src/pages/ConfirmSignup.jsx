import { useState } from "react";

import {
  useNavigate,
  Link
} from "react-router-dom";

import {
  confirmRegistration,
  resendCode
} from "../services/auth";

function ConfirmSignup() {

  const navigate = useNavigate();

  const email =
    sessionStorage.getItem(
      "signupEmail"
    ) || "";

  const [code, setCode] = useState("");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [message, setMessage] = useState("");

  const handleConfirm = async (e) => {

    e.preventDefault();

    setLoading(true);

    setError("");

    try {

      await confirmRegistration(
        email,
        code
      );

      console.log("EMAIL =", email);
      console.log("CODE =", code);

      sessionStorage.removeItem(
        "signupEmail"
      );

      navigate("/");

    }

    catch (err) {

      console.error(err);

      setError(

        err.message ||

        "Verification failed."

      );

    }

    finally {

      setLoading(false);

    }

  };

  const handleResend = async () => {

    try {

      await resendCode(email);

      setMessage(

        "Verification code sent again."

      );

    }

    catch (err) {

      setError(

        err.message

      );

    }

  };

  return (

    <div className="min-h-screen bg-gray-100 flex items-center justify-center">

      <div className="bg-white shadow-xl rounded-xl p-10 w-full max-w-md">

        <h1 className="text-3xl font-bold text-center text-blue-700">

          Verify Account

        </h1>

        <p className="text-center text-gray-500 mt-2">

          Enter the verification code sent to

          <br />

          <strong>{email}</strong>

        </p>

        <form

          onSubmit={handleConfirm}

          className="mt-8 space-y-5"

        >

          <input

            type="text"

            placeholder="Verification Code"

            value={code}

            onChange={(e)=>

              setCode(e.target.value)

            }

            className="w-full border rounded-lg px-4 py-3"

            required

          />

          {

            error &&

            <div className="text-red-600">

              {error}

            </div>

          }

          {

            message &&

            <div className="text-green-600">

              {message}

            </div>

          }

          <button

            type="submit"

            disabled={loading}

            className="w-full bg-blue-700 text-white py-3 rounded-lg hover:bg-blue-800"

          >

            {

              loading

                ? "Verifying..."

                : "Verify Account"

            }

          </button>

        </form>

        <button

          onClick={handleResend}

          className="mt-4 text-blue-700 w-full"

        >

          Resend Code

        </button>

        <p className="text-center mt-6">

          <Link

            to="/"

            className="text-blue-700"

          >

            Back to Login

          </Link>

        </p>

      </div>

    </div>

  );

}

export default ConfirmSignup;