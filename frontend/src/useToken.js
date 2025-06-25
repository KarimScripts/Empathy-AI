import { useState } from "react";
import { setAuthToken } from "./api";

// Set the token for the initial load
const initialToken = sessionStorage.getItem("token");
if (initialToken) {
  setAuthToken(initialToken);
}

export default function useToken() {
  const [token, setToken] = useState(initialToken);

  const saveToken = (userToken) => {
    if (userToken) {
      sessionStorage.setItem("token", userToken);
    } else {
      sessionStorage.removeItem("token");
    }
    setAuthToken(userToken); // Set header on change
    setToken(userToken);
  };

  const removeToken = () => {
    sessionStorage.removeItem("token");
    setAuthToken(null); // Clear auth header
    setToken(null);
  };

  return {
    setToken: saveToken,
    token,
    removeToken,
  };
}
