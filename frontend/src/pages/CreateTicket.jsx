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

            <label className="block font-semibold mb-3">
              Attachment (Optional)
            </label>

            <input
              id="attachment"
              type="file"
              className="hidden"
              onChange={(e) => {
                if (e.target.files.length > 0) {
                  setFile(e.target.files[0]);
                }
              }}
            />

            {!file ? (

              <label
                htmlFor="attachment"
                className="flex flex-col items-center justify-center w-full p-8 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-blue-600 hover:bg-blue-50 transition"
              >

                <div className="text-5xl mb-3">
                  📎
                </div>

                <p className="font-semibold text-gray-700">
                  Click to choose a file
                </p>

                <p className="text-sm text-gray-500 mt-1">
                  Upload screenshots, PDFs, invoices or any supporting document.
                </p>

              </label>

            ) : (

              <div className="border rounded-xl p-4 bg-gray-50">

                <div className="flex justify-between items-center">

                  <div>

                    <p className="font-semibold text-green-700">
                      ✅ {file.name}
                    </p>

                    <p className="text-sm text-gray-500 mt-1">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>

                  </div>

                  <div className="flex gap-2">

                    <label
                      htmlFor="attachment"
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700"
                    >
                      Change
                    </label>

                    <button
                      type="button"
                      onClick={() => {

                        setFile(null);

                        document.getElementById("attachment").value = "";

                      }}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                      Remove
                    </button>

                  </div>

                </div>

              </div>

            )}

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