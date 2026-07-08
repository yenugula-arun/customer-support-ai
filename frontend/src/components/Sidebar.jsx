import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

function Sidebar() {

  const {

    role

  } = useAuth();

  return (

    <aside className="w-64 bg-blue-900 text-white">

      <div className="text-2xl font-bold p-6 border-b border-blue-800">

        Customer Support AI

      </div>

      <nav className="flex flex-col p-4 gap-3">

        <Link

          className="hover:bg-blue-700 rounded p-3"

          to="/dashboard"

        >

          Dashboard

        </Link>

        {

          role === "Admin"

          &&

          <>

            <Link

              className="hover:bg-blue-700 rounded p-3"

              to="/tickets"

            >

              All Tickets

            </Link>

            <Link

              className="hover:bg-blue-700 rounded p-3"

              to="/pending-approvals"

            >

              Pending Approvals

            </Link>

            <Link

              className="hover:bg-blue-700 rounded p-3"

              to="/analytics"

            >

              Analytics

            </Link>

          </>

        }

        {

          role === "Customer"

          &&

          <>

            <Link

              className="hover:bg-blue-700 rounded p-3"

              to="/tickets"

            >

              My Tickets

            </Link>

            <Link

              className="hover:bg-blue-700 rounded p-3"

              to="/create-ticket"

            >

              Create Ticket

            </Link>

          </>

        }

        <Link

          className="hover:bg-blue-700 rounded p-3"

          to="/profile"

        >

          Profile

        </Link>

      </nav>

    </aside>

  );

}

export default Sidebar;