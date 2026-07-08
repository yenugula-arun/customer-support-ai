import { useState } from "react";
import {
  createTicket,
  uploadAttachment
} from "../services/api";

function CreateTicket() {

  const [subject, setSubject] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [file, setFile] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const fileToBase64 = (file) => {

    return new Promise((resolve, reject) => {

      const reader = new FileReader();

      reader.readAsDataURL(file);

      reader.onload = () => {

        resolve(
          reader.result.split(",")[1]
        );

      };

      reader.onerror = reject;

    });

  };

  const handleSubmit = async (e) => {

    e.preventDefault();

    setLoading(true);

    try {

      let attachmentKey = null;

      if (file) {

        const base64 =
          await fileToBase64(file);

        const uploadResponse =
          await uploadAttachment({

            fileName: file.name,

            fileContent: base64

          });

        attachmentKey =
          uploadResponse.data.fileKey;

      }

      await createTicket({

        subject,

        message,

        attachmentKey

      });

      alert(
        "Ticket created successfully."
      );

      setSubject("");

      setMessage("");

      setFile(null);

    } catch (error) {

      console.error(error);

      alert("Failed to create ticket.");

    }

    setLoading(false);

  };

  return (

    <div className="max-w-3xl mx-auto">

      <div className="bg-white rounded-xl shadow-lg p-8">

        <h2 className="text-3xl font-bold mb-2">

          Create Support Ticket

        </h2>

        <p className="text-gray-500 mb-8">

          Describe your issue and our AI assistant will automatically classify and route your ticket.

        </p>

        <form
          onSubmit={handleSubmit}
          className="space-y-6"
        >

          <div>

            <label className="font-semibold">

              Subject

            </label>

            <input
              type="text"
              value={subject}
              onChange={(e) =>
                setSubject(
                  e.target.value
                )
              }
              className="w-full border rounded-lg p-3 mt-2"
              placeholder="Example: Unable to access my account"
              required
            />

          </div>

          <div>

            <label className="font-semibold">

              Describe your issue

            </label>

            <textarea
              rows="6"
              value={message}
              onChange={(e) =>
                setMessage(
                  e.target.value
                )
              }
              className="w-full border rounded-lg p-3 mt-2"
              placeholder="Please provide as much detail as possible..."
              required
            />

          </div>

          <div>

            <label className="font-semibold">

              Attachment (Optional)

            </label>

            <input
              type="file"
              className="mt-2"
              onChange={(e) =>
                setFile(
                  e.target.files[0]
                )
              }
            />

            {

              file && (

                <p className="mt-2 text-sm text-green-600">

                  Selected:

                  {" "}

                  {file.name}

                </p>

              )

            }

          </div>

          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >

            {

              loading
                ? "Creating..."
                : "Create Ticket"

            }

          </button>

        </form>

      </div>

    </div>

  );

}

export default CreateTicket;