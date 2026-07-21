import { useEffect, useState } from "react";

import { getTickets } from "../services/api";

import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

function Analytics() {

  const [tickets, setTickets] = useState([]);

  useEffect(() => {

    loadTickets();

  }, []);

  const loadTickets = async () => {

    try {

      const response = await getTickets();

      setTickets(response.data);

    } catch (error) {

      console.error(error);

    }

  };

  const countBy = (field) => {

    const counts = {};

    tickets.forEach(ticket => {

      const value = ticket[field];

      const key = value
        ? value.toString().trim().toUpperCase()
        : "UNKNOWN";

      counts[key] = (counts[key] || 0) + 1;

    });

    return Object.keys(counts).map(key => ({

      name: key,

      value: counts[key]

    }));

  };

  const categoryData = countBy("category");

  const priorityData = countBy("priority");

  const statusData = countBy("status");

  const sentimentData = countBy("sentiment");

  const toolData = countBy("toolInvoked");

  const COLORS = [

    "#3B82F6",

    "#10B981",

    "#F59E0B",

    "#EF4444",

    "#8B5CF6",

    "#EC4899"

  ];

  return (

    <div>

      <h1 className="text-3xl font-bold mb-8">

        Analytics Dashboard

      </h1>

      <div className="grid grid-cols-4 gap-6 mb-10">

        <div className="bg-blue-600 text-white rounded-xl p-6 shadow">

          <h2>Total Tickets</h2>

          <p className="text-4xl font-bold mt-3">

            {tickets.length}

          </p>

        </div>

        <div className="bg-green-600 text-white rounded-xl p-6 shadow">

          <h2>Open</h2>

          <p className="text-4xl font-bold mt-3">

            {

              tickets.filter(

                t => t.status === "OPEN"

              ).length

            }

          </p>

        </div>

        <div className="bg-orange-500 text-white rounded-xl p-6 shadow">

          <h2>Pending Approval</h2>

          <p className="text-4xl font-bold mt-3">

            {

              tickets.filter(

                t => t.approvalStatus === "PENDING"

              ).length

            }

          </p>

        </div>

        <div className="bg-purple-600 text-white rounded-xl p-6 shadow">

          <h2>Resolved</h2>

          <p className="text-4xl font-bold mt-3">

            {

              tickets.filter(

                t =>

                  t.status === "RESOLVED" ||

                  t.status === "CLOSED"

              ).length

            }

          </p>

        </div>

      </div>

      <div className="grid grid-cols-2 gap-8">

        <div className="bg-white rounded-xl shadow p-6">

          <h2 className="text-xl font-semibold mb-4">

            Tickets by Category

          </h2>

          <ResponsiveContainer width="100%" height={300}>

            <PieChart>

              <Pie

                data={categoryData}

                dataKey="value"

                nameKey="name"

                outerRadius={100}

                label

              >

                {

                  categoryData.map((entry,index)=>(

                    <Cell

                      key={index}

                      fill={COLORS[index % COLORS.length]}

                    />

                  ))

                }

              </Pie>

              <Tooltip/>

              <Legend/>

            </PieChart>

          </ResponsiveContainer>

        </div>

        <div className="bg-white rounded-xl shadow p-6">

          <h2 className="text-xl font-semibold mb-4">

            Priority Distribution

          </h2>

          <ResponsiveContainer width="100%" height={300}>

            <BarChart data={priorityData}>

              <XAxis dataKey="name"/>

              <YAxis/>

              <Tooltip/>

              <Legend/>

              <Bar

                dataKey="value"

                fill="#3B82F6"

              />

            </BarChart>

          </ResponsiveContainer>

        </div>

        <div className="bg-white rounded-xl shadow p-6">

          <h2 className="text-xl font-semibold mb-4">

            Ticket Status

          </h2>

          <ResponsiveContainer width="100%" height={300}>

            <PieChart>

              <Pie

                data={statusData}

                dataKey="value"

                nameKey="name"

                outerRadius={100}

                label

              >

                {

                  statusData.map((entry,index)=>(

                    <Cell

                      key={index}

                      fill={COLORS[index % COLORS.length]}

                    />

                  ))

                }

              </Pie>

              <Tooltip/>

              <Legend/>

            </PieChart>

          </ResponsiveContainer>

        </div>

        <div className="bg-white rounded-xl shadow p-6">

          <h2 className="text-xl font-semibold mb-4">

            Sentiment Analysis

          </h2>

          <ResponsiveContainer width="100%" height={300}>

            <BarChart data={sentimentData}>

              <XAxis dataKey="name"/>

              <YAxis/>

              <Tooltip/>

              <Legend/>

              <Bar

                dataKey="value"

                fill="#10B981"

              />

            </BarChart>

          </ResponsiveContainer>

        </div>

        <div className="bg-white rounded-xl shadow p-6 col-span-2">

          <h2 className="text-xl font-semibold mb-4">

            AI Tool Usage

          </h2>

          <ResponsiveContainer width="100%" height={350}>

            <PieChart>

              <Pie

                data={toolData}

                dataKey="value"

                nameKey="name"

                outerRadius={120}

                label

              >

                {

                  toolData.map((entry,index)=>(

                    <Cell

                      key={index}

                      fill={COLORS[index % COLORS.length]}

                    />

                  ))

                }

              </Pie>

              <Tooltip/>

              <Legend/>

            </PieChart>

          </ResponsiveContainer>

        </div>

      </div>

    </div>

  );

}

export default Analytics;