import axios from "axios";

const api = axios.create({

  baseURL: import.meta.env.VITE_API_URL

});

api.interceptors.request.use((config) => {

  const token = localStorage.getItem("idToken");

  if (token) {

    config.headers.Authorization = token;

  }

  return config;

});

// ----------------------
// Ticket APIs
// ----------------------

export const createTicket = (data) => {

  return api.post("/tickets", data);

};

export const getTickets = () => {

  return api.get("/tickets");

};

export const getTicket = (ticketId) => {

  return api.get(`/tickets/${ticketId}`);

};

export const updateTicket = (ticketId, data) => {

  return api.put(`/tickets/${ticketId}`, data);

};

export const deleteTicket = (ticketId) => {

  return api.delete(`/tickets/${ticketId}`);

};

// ----------------------
// Upload Attachment
// ----------------------

export const uploadAttachment = (data) => {

  return api.post(
    "/upload",
    data
  );

};




export const approveTicket = (ticketId) => {
  return api.get(`/approve?ticketId=${ticketId}&action=approve`);
};

export const rejectTicket = (ticketId) => {
  return api.get(`/reject?ticketId=${ticketId}&action=reject`);
};

export default api;