import { useAuth } from "../context/AuthContext";

function Profile() {

  const {

    user,

    role,

    signOut

  } = useAuth();

  return (

    <div className="max-w-3xl mx-auto">

      <div className="bg-white rounded-xl shadow-lg p-8">

        <div className="flex items-center gap-6">

          <div className="w-24 h-24 rounded-full bg-blue-600 text-white flex items-center justify-center text-4xl font-bold">

            {

              user?.signInDetails?.loginId

                ?.charAt(0)

                ?.toUpperCase()

            }

          </div>

          <div>

            <h1 className="text-3xl font-bold">

              My Profile

            </h1>

            <p className="text-gray-500">

              Customer Support AI Portal

            </p>

          </div>

        </div>

        <hr className="my-8"/>

        <div className="grid grid-cols-2 gap-8">

          <div>

            <h3 className="font-semibold">

              Email

            </h3>

            <p className="text-gray-600">

              {user?.signInDetails?.loginId}

            </p>

          </div>

          <div>

            <h3 className="font-semibold">

              Role

            </h3>

            <span className="inline-block mt-2 px-4 py-1 rounded-full bg-green-100 text-green-700">

              {role}

            </span>

          </div>

          <div>

            <h3 className="font-semibold">

              User ID

            </h3>

            <p className="text-gray-600 break-all">

              {user?.userId}

            </p>

          </div>

          <div>

            <h3 className="font-semibold">

              Username

            </h3>

            <p className="text-gray-600">

              {user?.username}

            </p>

          </div>

        </div>

        <hr className="my-8"/>

        <button

          onClick={signOut}

          className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg"

        >

          Logout

        </button>

      </div>

    </div>

  );

}

export default Profile;