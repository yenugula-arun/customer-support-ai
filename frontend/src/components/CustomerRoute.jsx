import { Navigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

function CustomerRoute({ children }) {

  const {

    loading,

    role

  } = useAuth();

  if (loading) {

    return <div>Loading...</div>;

  }

  if (role !== "Customer") {

    return <Navigate to="/dashboard" replace />;

  }

  return children;

}

export default CustomerRoute;