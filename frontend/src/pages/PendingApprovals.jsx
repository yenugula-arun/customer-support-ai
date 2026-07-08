import { useEffect, useState } from "react";

import { Link } from "react-router-dom";

import { getTickets } from "../services/api";

function PendingApprovals() {

  const [tickets, setTickets] = useState([]);

  useEffect(() => {

    loadTickets();

  }, []);

  const loadTickets = async () => {

    try {

      const response = await getTickets();

      const pending = response.data.filter(

        ticket => ticket.approvalStatus === "PENDING"

      );

      setTickets(pending);

    } catch (error) {

      console.error(error);

    }

  };

  return (

    <div>

      <h2 className="text-3xl font-bold mb-8">

        Pending Approvals

      </h2>

      <div className="bg-white rounded-xl shadow">

        <table className="w-full">

          <thead className="bg-gray-100">

            <tr>

              <th className="text-left p-4">

                Ticket

              </th>

              <th className="text-left p-4">

                Customer

              </th>

              <th className="text-left p-4">

                Tool

              </th>

              <th className="text-left p-4">

                Priority

              </th>

              <th className="text-left p-4">

                Action

              </th>

            </tr>

          </thead>

          <tbody>

            {

              tickets.map(ticket => (

                <tr

                  key={ticket.ticketId}

                  className="border-t hover:bg-gray-50"

                >

                  <td className="p-4">

                    {ticket.subject}

                  </td>

                  <td className="p-4">

                    {ticket.customerEmail}

                  </td>

                  <td className="p-4">

                    {ticket.toolInvoked}

                  </td>

                  <td className="p-4">

                    {ticket.priority}

                  </td>

                  <td className="p-4">

                    <Link

                      to={`/tickets/${ticket.ticketId}`}

                      className="text-blue-600"

                    >

                      View

                    </Link>

                  </td>

                </tr>

              ))

            }

          </tbody>

        </table>

      </div>

    </div>

  );

}

export default PendingApprovals;