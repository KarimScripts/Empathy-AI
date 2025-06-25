import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import LoginPage from "./LoginPage";
import ChatPage from "./ChatPage";
import useToken from "./useToken";
import "./index.css";

function App() {
  const { token, setToken, removeToken } = useToken();

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route
          path="/login"
          element={
            !token ? <LoginPage setToken={setToken} /> : <Navigate to="/chat" />
          }
        />
        <Route
          path="/chat"
          element={
            token ? (
              <ChatPage removeToken={removeToken} />
            ) : (
              <Navigate to="/login" />
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
