export function getUserRole() {

  const token = localStorage.getItem("idToken");

  if (!token) return null;

  const payload = JSON.parse(

    atob(token.split(".")[1])

  );

  const groups = payload["cognito:groups"];

  if (!groups) return "Customer";

  return Array.isArray(groups)

    ? groups[0]

    : groups;

}