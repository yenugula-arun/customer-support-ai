import { useAuth } from "../context/AuthContext";

function Navbar() {

  const {

    user,

    role,

    signOut

  } = useAuth();

  return (

    <header className="bg-white shadow px-8 py-4 flex justify-between items-center">

      <div>

        <h1 className="text-2xl font-bold text-blue-700">

          Customer Support AI

        </h1>

        <p className="text-gray-500 text-sm">

          Intelligent Ticket Management System

        </p>

      </div>

      <div className="flex items-center gap-6">

        <div className="text-right">

          <h2 className="font-semibold">

            👋 Welcome

          </h2>

          <p className="text-gray-600">

            {user?.signInDetails?.loginId || "User"}

          </p>

          <span className="inline-block mt-1 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-xs">

            {role}

          </span>

        </div>

        <button

          onClick={signOut}

          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg"

        >

          Logout

        </button>

      </div>

    </header>

  );

}

export default Navbar;