import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import DashboardLayout from "./layouts/DashboardLayout";

import Dashboard from "./pages/Dashboard";
import Tickets from "./pages/Tickets";
import CreateTicket from "./pages/CreateTicket";
import Profile from "./pages/Profile";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ConfirmSignup from "./pages/ConfirmSignup";
import PendingApprovals from "./pages/PendingApprovals";

import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";

import TicketDetails from "./pages/TicketDetails";

import Analytics from "./pages/Analytics";

function App() {

  return (

    <BrowserRouter>

      <Routes>

        {/* Authentication */}

        <Route
          path="/"
          element={<Login />}
        />

        <Route
          path="/signup"
          element={<Signup />}
        />

        <Route
          path="/confirm-signup"
          element={<ConfirmSignup />}
        />

        {/* Dashboard */}

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>

              <DashboardLayout>

                <Dashboard />

              </DashboardLayout>

            </ProtectedRoute>
          }
        />

        {/* Tickets */}

        <Route
          path="/tickets"
          element={
            <ProtectedRoute>

              <DashboardLayout>

                <Tickets />

              </DashboardLayout>

            </ProtectedRoute>
          }
        />

        <Route
          path="/tickets/:ticketId"
          element={
            <ProtectedRoute>

              <DashboardLayout>

                <TicketDetails />

              </DashboardLayout>

            </ProtectedRoute>
          }
        />

        {/* Customer Only */}

        <Route
          path="/create-ticket"
          element={
            <ProtectedRoute>

              <DashboardLayout>

                <CreateTicket />

              </DashboardLayout>

            </ProtectedRoute>
          }
        />

        {/* Admin Only */}

        <Route
          path="/pending-approvals"
          element={
            <ProtectedRoute>

              <AdminRoute>

                <DashboardLayout>

                  <PendingApprovals />

                </DashboardLayout>

              </AdminRoute>

            </ProtectedRoute>
          }
        />

        {/* Profile */}

        <Route
          path="/profile"
          element={
            <ProtectedRoute>

              <DashboardLayout>

                <Profile />

              </DashboardLayout>

            </ProtectedRoute>
          }
        />

        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <AdminRoute>
                <DashboardLayout>
                  <Analytics />
                </DashboardLayout>
              </AdminRoute>
            </ProtectedRoute>
          }
        />

      </Routes>

    </BrowserRouter>

  );

}

export default App;