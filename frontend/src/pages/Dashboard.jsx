import { useEffect, useState } from "react";

import DashboardCard from "../components/DashboardCard";

import { getTickets } from "../services/api";

import { useAuth } from "../context/AuthContext";

function Dashboard() {

  const { role, user } = useAuth();

  const [stats, setStats] = useState({

    total: 0,

    open: 0,

    pending: 0,

    completed: 0,

    highPriority: 0

  });

  const [recentTickets, setRecentTickets] = useState([]);

  useEffect(() => {

    loadDashboard();

  }, []);

  const loadDashboard = async () => {

    try {

      const response = await getTickets();

      let tickets = response.data;

      // Customer should only see their own tickets
      if (role === "Customer") {

        tickets = tickets.filter(

          ticket =>

            ticket.customerEmail ===

            user?.email

        );

      }

      setRecentTickets(

        tickets.slice(0, 5)

      );

      setStats({

        total: tickets.length,

        open: tickets.filter(

          ticket => ticket.status === "OPEN"

        ).length,

        pending: tickets.filter(

          ticket =>

            ticket.approvalStatus === "PENDING"

        ).length,

        completed: tickets.filter(

          ticket => ticket.status === "CLOSED"

        ).length,

        highPriority: tickets.filter(

          ticket =>

            ticket.priority === "High"

        ).length

      });

    } catch (error) {

      console.error(error);

    }

  };

  return (

    <div>

      <h2 className="text-3xl font-bold mb-8">

        {

          role === "Admin"

            ? "Support Team Dashboard"

            : "Customer Dashboard"

        }

      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">

        <DashboardCard

          title={

            role === "Admin"

              ? "Total Tickets"

              : "My Tickets"

          }

          value={stats.total}

          className="bg-blue-600"

        />

        <DashboardCard

          title="Open"

          value={stats.open}

          className="bg-green-600"

        />

        <DashboardCard

          title="Pending Approval"

          value={stats.pending}

          className="bg-orange-500"

        />

        <DashboardCard

          title="Resolved"

          value={stats.completed}

          className="bg-purple-600"

        />

        {

          role === "Admin" &&

          <DashboardCard

            title="High Priority"

            value={stats.highPriority}

            className="bg-red-600"

          />

        }

      </div>

      <div className="mt-10">

        <h3 className="text-2xl font-semibold mb-4">

          {

            role === "Admin"

              ? "Recent Tickets"

              : "My Recent Tickets"

          }

        </h3>

        <div className="bg-white rounded-xl shadow">

          <table className="w-full">

            <thead className="bg-gray-100">

              <tr>

                <th className="text-left p-4">

                  Subject

                </th>

                <th className="text-left p-4">

                  Category

                </th>

                <th className="text-left p-4">

                  Priority

                </th>

                <th className="text-left p-4">

                  Status

                </th>

              </tr>

            </thead>

            <tbody>

              {

                recentTickets.map(ticket => (

                  <tr

                    key={ticket.ticketId}

                    className="border-t hover:bg-gray-50"

                  >

                    <td className="p-4">

                      {ticket.subject}

                    </td>

                    <td className="p-4">

                      {ticket.category}

                    </td>

                    <td className="p-4">

                      {ticket.priority}

                    </td>

                    <td className="p-4">

                      {ticket.status}

                    </td>

                  </tr>

                ))

              }

            </tbody>

          </table>

        </div>

      </div>

    </div>

  );

}

export default Dashboard;