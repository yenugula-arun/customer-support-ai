import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getTickets } from "../services/api";

import TicketCard from "../components/TicketCard";
import SearchBar from "../components/SearchBar";

import { useAuth } from "../context/AuthContext";

function Tickets() {

  const navigate = useNavigate();

  const { role, user } = useAuth();

  const [tickets, setTickets] = useState([]);

  const [filteredTickets, setFilteredTickets] = useState([]);

  const [search, setSearch] = useState("");

  const [statusFilter, setStatusFilter] = useState("");

  const [priorityFilter, setPriorityFilter] = useState("");

  const [approvalFilter, setApprovalFilter] = useState("");

  useEffect(() => {

    loadTickets();

  }, []);

  useEffect(() => {

    let filtered = [...tickets];

    // Customer should only see their own tickets
    if (role === "Customer") {

      filtered = filtered.filter(

        ticket =>

          ticket.customerEmail === user?.email

      );

    }

    // Search

    filtered = filtered.filter(ticket =>

      ticket.subject?.toLowerCase().includes(search.toLowerCase()) ||

      ticket.category?.toLowerCase().includes(search.toLowerCase()) ||

      ticket.customerEmail?.toLowerCase().includes(search.toLowerCase())

    );

    // Status

    if (statusFilter) {

      filtered = filtered.filter(

        ticket => ticket.status === statusFilter

      );

    }

    // Priority

    if (priorityFilter) {

      filtered = filtered.filter(

        ticket => ticket.priority === priorityFilter

      );

    }

    // Approval

    if (approvalFilter) {

      filtered = filtered.filter(

        ticket =>

          ticket.approvalStatus === approvalFilter

      );

    }

    setFilteredTickets(filtered);

  }, [

    search,

    tickets,

    role,

    user,

    statusFilter,

    priorityFilter,

    approvalFilter

  ]);

  const loadTickets = async () => {

    try {

      const response = await getTickets();

      setTickets(response.data);

    } catch (error) {

      console.error(error);

    }

  };

  return (

    <div>

      <div className="flex justify-between items-center mb-8">

        <div>

          <h1 className="text-3xl font-bold">

            {

              role === "Admin"

                ? "All Tickets"

                : "My Tickets"

            }

          </h1>

          <p className="text-gray-500">

            {

              role === "Admin"

                ? "Manage all customer tickets"

                : "View your submitted tickets"

            }

          </p>

        </div>

        {

          role === "Customer" &&

          <button

            onClick={() =>

              navigate("/create-ticket")

            }

            className="bg-blue-600 text-white px-5 py-3 rounded-xl hover:bg-blue-700"

          >

            + New Ticket

          </button>

        }

      </div>

      <SearchBar

        value={search}

        onChange={setSearch}

      />

      <div className="flex gap-4 my-6">

        <select

          value={statusFilter}

          onChange={(e) =>

            setStatusFilter(e.target.value)

          }

          className="border rounded-lg p-2"

        >

          <option value="">

            All Status

          </option>

          <option value="OPEN">

            OPEN

          </option>

          <option value="IN_PROGRESS">

            IN PROGRESS

          </option>

          <option value="CLOSED">

            CLOSED

          </option>

        </select>

        <select

          value={priorityFilter}

          onChange={(e) =>

            setPriorityFilter(e.target.value)

          }

          className="border rounded-lg p-2"

        >

          <option value="">

            All Priority

          </option>

          <option value="High">

            High

          </option>

          <option value="Medium">

            Medium

          </option>

          <option value="Low">

            Low

          </option>

        </select>

        <select

          value={approvalFilter}

          onChange={(e) =>

            setApprovalFilter(e.target.value)

          }

          className="border rounded-lg p-2"

        >

          <option value="">

            All Approval

          </option>

          <option value="PENDING">

            Pending

          </option>

          <option value="APPROVED">

            Approved

          </option>

          <option value="REJECTED">

            Rejected

          </option>

        </select>

      </div>

      {

        filteredTickets.length === 0

        ?

        (

          <div className="text-center text-gray-500 mt-20">

            No tickets found.

          </div>

        )

        :

        (

          <div className="grid gap-5">

            {

              filteredTickets.map(ticket => (

                <TicketCard

                  key={ticket.ticketId}

                  ticket={ticket}

                  onSelect={(ticketId) =>

                    navigate(

                      `/tickets/${ticketId}`

                    )

                  }

                />

              ))

            }

          </div>

        )

      }

    </div>

  );

}

export default Tickets;