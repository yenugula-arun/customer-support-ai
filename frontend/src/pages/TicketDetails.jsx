import { useEffect, useState } from "react";
import {
  useNavigate,
  useParams
} from "react-router-dom";

import {
  getTicket,
  deleteTicket,
  updateTicket,
  approveTicket,
  rejectTicket
} from "../services/api";

import { useAuth } from "../context/AuthContext";



function TicketDetails() {

  const navigate = useNavigate();

  const { ticketId } = useParams();

  const [ticket, setTicket] =
    useState(null);
  
  const { role } = useAuth();

  const [status, setStatus] = useState("");

  const [assignedTo, setAssignedTo] = useState("");

  const [saving, setSaving] = useState(false);

  const [draftResponse, setDraftResponse] = useState("");


  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    loadTicket();

  }, []);

  const loadTicket = async () => {

    try {

      const response =
        await getTicket(ticketId);

      setTicket(response.data);

      setStatus(response.data.status);

      setAssignedTo(response.data.assignedTo);

      setDraftResponse(
          response.data.draftResponse || ""
      );

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

    }

  };


  const handleUpdate = async () => {

    try {

      setSaving(true);

      await updateTicket(

        ticket.ticketId,

        {

          ...ticket,

          status,

          assignedTo

        }

      );

      alert("Ticket updated successfully.");

      await loadTicket();

    }

    catch(error){

      console.error(error);

      alert("Failed to update ticket.");

    }

    finally{

      setSaving(false);

    }

  };
  

  const handleSaveDraft = async () => {

    try {

        setSaving(true);

        await updateTicket(
            ticket.ticketId,
            {
                draftResponse
            }
        );

        alert("Draft saved successfully.");

        await loadTicket();

    } catch (error) {

        console.error(error);

        alert("Failed to save draft.");

    } finally {

        setSaving(false);

    }

};


  const handleDelete = async () => {

    const confirmed =

      window.confirm(

        "Are you sure you want to delete this ticket?"

      );

    if (!confirmed)

      return;

    try {

      await deleteTicket(

        ticket.ticketId

      );

      alert(

        "Ticket deleted successfully."

      );

      navigate("/tickets");

    } catch (error) {

      console.error(error);

      alert(

        "Failed to delete ticket."

      );

    }

  };

  const handleApprove = async () => {

    try {

      await approveTicket(ticket.ticketId);

      alert("Ticket approved successfully.");

      await loadTicket();

    }

    catch (error) {

      console.error(error);

      alert("Approval failed.");

    }

  };

const handleReject = async () => {

  try {

    await rejectTicket(ticket.ticketId);

    alert("Ticket rejected.");

    await loadTicket();

  }

  catch (error) {

    console.error(error);

    alert("Reject failed.");

  }

};

  if (loading) {

    return (

      <div className="text-center mt-20">

        Loading...

      </div>

    );

  }

  if (!ticket) {

    return (

      <div className="text-center mt-20">

        Ticket not found.

      </div>

    );

  }

  return (

    <div className="max-w-6xl mx-auto">

      <div className="bg-white rounded-xl shadow-lg p-8">

        <div className="flex justify-between items-start">

          <div>

            <h1 className="text-3xl font-bold">

              {ticket.subject}

            </h1>

            <p className="text-gray-500 mt-2">

              Ticket ID : {ticket.ticketId}

            </p>

          </div>

          <div className="flex gap-3">

            <button

              onClick={()=>

                navigate("/tickets")

              }

              className="bg-gray-200 px-4 py-2 rounded-lg"

            >

              Back

            </button>

            {

            role==="Admin"

            &&


            <button

              onClick={handleDelete}

              className="bg-red-600 text-white px-4 py-2 rounded-lg"

            >

              Delete

            </button>
          }

          </div>

        </div>

      {
        role === "Admin" && (
          <>
            <hr className="my-8" />

            <h2 className="text-2xl font-bold mb-6">
              Admin Actions
            </h2>

            <div className="grid grid-cols-2 gap-6">

              <div>
                <label className="font-semibold">
                  Status
                </label>

                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  className="w-full border rounded-lg p-3 mt-2"
                >
                  <option>OPEN</option>
                  <option>IN_PROGRESS</option>
                  <option>RESOLVED</option>
                  <option>CLOSED</option>
                </select>
              </div>

              <div>
                <label className="font-semibold">
                  Assigned Team
                </label>

                <input
                  value={assignedTo}
                  onChange={(e) => setAssignedTo(e.target.value)}
                  className="w-full border rounded-lg p-3 mt-2"
                />
              </div>

            </div>

            <button
              onClick={handleUpdate}
              disabled={saving}
              className="mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg"
            >
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </>
        )
      }

      <hr className="my-8"/>

        {
          role === "Admin" &&
          ticket.approvalStatus === "PENDING" &&

          <div className="mt-8 border rounded-xl p-6 bg-yellow-50">

            <h3 className="text-xl font-semibold mb-4">
              Approval Required
            </h3>

            <div className="flex gap-4">
              <button
                onClick={handleApprove}
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
              >
                Approve
                </button>

                <button
                  onClick={handleReject}
                  className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700"
                >
                  Reject
                </button>

              </div>

            </div>

          }

        <div className="grid grid-cols-2 gap-6">
        
                <div>

          <h3 className="font-semibold">

            Customer

          </h3>

          <p>{ticket.customerEmail}</p>

        </div>

        <div>

          <h3 className="font-semibold">

            Category

          </h3>

          <p>{ticket.category}</p>

        </div>

        <div>

          <h3 className="font-semibold">

            Priority

          </h3>

          <p>{ticket.priority}</p>

        </div>

        <div>

          <h3 className="font-semibold">

            Status

          </h3>

          <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full">

            {status}

          </span>

        </div>

        <div>

          <h3 className="font-semibold">

            AI Status

          </h3>

          <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full">

            {ticket.aiStatus || "Pending"}

          </span>

        </div>

        <div>

          <h3 className="font-semibold">

            Approval Status

          </h3>

          <span className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full">

            {ticket.approvalStatus || "Not Required"}

          </span>

        </div>

        <div>

          <h3 className="font-semibold">

            Sentiment

          </h3>

          <p>{ticket.sentiment}</p>

        </div>

        <div>

          <h3 className="font-semibold">

            Language

          </h3>

          <p>{ticket.language}</p>

        </div>

        <div>

          <h3 className="font-semibold">

            Assigned Team

          </h3>

          <p>{assignedTo}</p>

        </div>

        <div>

          <h3 className="font-semibold">

            Tool Invoked

          </h3>

          <p>{ticket.toolInvoked || "None"}</p>

        </div>

      </div>

      <hr className="my-8"/>

      <div>

        <h3 className="font-semibold mb-3">

          Customer Message

        </h3>
            <div className="bg-gray-50 rounded-lg p-5">

              {ticket.message}

            </div>

      </div>

      <hr className="my-8"/>
      <div>

            <h3 className="font-semibold mb-3">
                Draft Response
            </h3>

            {
                role === "Admin" &&
                ticket.approvalStatus === "PENDING" ? (

                    <>
                        <textarea
                            value={draftResponse}
                            onChange={(e) =>
                                setDraftResponse(e.target.value)
                            }
                            rows={8}
                            className="w-full border rounded-lg p-4"
                        />

                        <button
                            onClick={handleSaveDraft}
                            disabled={
                                saving ||
                                draftResponse === ticket.draftResponse
                            }
                            className="mt-4 bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                        >
                            {saving
                                ? "Saving..."
                                : "Save Draft Response"}
                        </button>
                    </>

                ) : (

                    ticket.draftResponse && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-5 whitespace-pre-wrap">
                            {draftResponse}
                        </div>
                    )

                )
            }

        </div>

      {

        ticket.suggestedResolution &&

        <>

          <hr className="my-8"/>

          <div>

            <h3 className="font-semibold mb-3">

              AI Suggested Resolution

            </h3>

            <div className="bg-green-50 border border-green-200 rounded-lg p-5">

              {ticket.suggestedResolution}

            </div>

          </div>

        </>

      }

      {

        ticket.finalResponse &&

        <>

          <hr className="my-8"/>

          <div>

            <h3 className="font-semibold mb-3">

              Final Response

            </h3>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-5">

              {ticket.finalResponse}

            </div>

          </div>

        </>

      }

      {

        ticket.attachmentKey &&

        <>

          <hr className="my-8"/>

          <div>

            <h3 className="font-semibold mb-3">

              Attachment

            </h3>

            <a

              href={`https://csai-ticket-attachments.s3.amazonaws.com/${ticket.attachmentKey}`}

              target="_blank"

              rel="noreferrer"

              className="text-blue-600 hover:underline"

            >

              Download Attachment

            </a>

          </div>

        </>

      }

      </div>

    </div>

  );

}

export default TicketDetails;