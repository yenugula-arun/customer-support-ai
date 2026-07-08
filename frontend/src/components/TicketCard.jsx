import { getUserRole } from "../utils/auth";

function TicketCard({

  ticket,

  onSelect

}) {

  const role = getUserRole();

  const priorityColor = {

    High: "bg-red-100 text-red-700",

    Medium: "bg-yellow-100 text-yellow-700",

    Low: "bg-green-100 text-green-700",

    high: "bg-red-100 text-red-700",

    medium: "bg-yellow-100 text-yellow-700",

    low: "bg-green-100 text-green-700"

  };

  const statusColor = {

    OPEN: "bg-blue-100 text-blue-700",

    IN_PROGRESS: "bg-yellow-100 text-yellow-700",

    RESOLVED: "bg-green-100 text-green-700",

    COMPLETED: "bg-green-100 text-green-700",

    CLOSED: "bg-gray-200 text-gray-700"

  };

  console.log(ticket);

  return (

    <div

      onClick={() => onSelect(ticket.ticketId)}

      className="bg-white rounded-xl shadow hover:shadow-lg cursor-pointer p-6 transition"

    >

      <div className="flex justify-between items-start">

        <h3 className="font-bold text-lg">

          {ticket.subject}

        </h3>

        <span

          className={`px-3 py-1 rounded-full text-sm font-semibold ${priorityColor[ticket.priority]}`}

        >

          {ticket.priority}

        </span>

      </div>

      <div className="mt-4 text-gray-600 space-y-2">

        {

          role === "Admin" && (

            <p>

              <b>Customer:</b>{" "}

              {ticket.customerEmail}

            </p>

          )

        }

        <p>

          <b>Category:</b>{" "}

          {ticket.category}

        </p>

      </div>

      <div className="flex justify-between items-center mt-5">

        <span

          className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColor[ticket.status] || "bg-gray-100 text-gray-700"}`}

        >

          {ticket.status}

        </span>

        <div className="text-right text-sm text-gray-500">

          <div>

            {

              ticket.createdAt

                ? new Date(ticket.createdAt).toLocaleDateString(

                    "en-IN",

                    {

                      day: "2-digit",

                      month: "short",

                      year: "numeric"

                    }

                  )

                : "-"

            }

          </div>

          <div className="text-xs">

            {

              ticket.createdAt

                ? new Date(ticket.createdAt).toLocaleTimeString(

                    "en-IN",

                    {

                      hour: "2-digit",

                      minute: "2-digit",

                      second: "2-digit",

                      hour12: true

                    }

                  )

                : ""

            }

          </div>

        </div>

      </div>

    </div>

  );

}

export default TicketCard;