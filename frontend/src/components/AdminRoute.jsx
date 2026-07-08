import { Navigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

function AdminRoute({ children }) {

  const {

    loading,

    role

  } = useAuth();

  if (loading) {

    return <div>Loading...</div>;

  }

  if (role !== "Admin") {

    return <Navigate to="/dashboard" replace />;

  }

  return children;

}

export default AdminRoute;