import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, signup } from "./api";
import "./LoginPage.css";

const LoginPage = ({ setToken }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState("");

  // State for sign-in form
  const [signInEmail, setSignInEmail] = useState("");
  const [signInPassword, setSignInPassword] = useState("");

  // State for sign-up form
  const [signUpName, setSignUpName] = useState("");
  const [signUpEmail, setSignUpEmail] = useState("");
  const [signUpPassword, setSignUpPassword] = useState("");

  const navigate = useNavigate();

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const response = await login(signInEmail, signInPassword);
      setToken(response.data.access_token);
      navigate("/chat");
    } catch (err) {
      setError("Failed to Sign In. Please check your credentials.");
      console.error(err);
    }
  };

  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await signup(signUpName, signUpEmail, signUpPassword);
      // Switch to sign-in view on successful sign-up
      setIsSignUp(false);
      // Optionally, pre-fill the login form
      setSignInEmail(signUpEmail);
      setSignInPassword("");
      alert("Sign Up successful! Please Sign In.");
    } catch (err) {
      setError("Failed to Sign Up. Please try another email.");
      console.error(err);
    }
  };

  return (
    <div className="login-page-wrapper">
      <div className={`cont ${isSignUp ? "s--signup" : ""}`}>
        <div className="form sign-in">
          <form onSubmit={handleLoginSubmit}>
            <h2>Welcome Back</h2>
            <label>
              <span>Email</span>
              <input
                type="email"
                value={signInEmail}
                onChange={(e) => setSignInEmail(e.target.value)}
                required
              />
            </label>
            <label>
              <span>Password</span>
              <input
                type="password"
                value={signInPassword}
                onChange={(e) => setSignInPassword(e.target.value)}
                required
              />
            </label>
            <p className="forgot-pass">Forgot password?</p>
            {error && !isSignUp && (
              <p
                style={{ color: "red", textAlign: "center", marginTop: "10px" }}
              >
                {error}
              </p>
            )}
            <button type="submit" className="submit">
              Sign In
            </button>
          </form>
        </div>
        <div className="sub-cont">
          <div className="img">
            <div className="img__text m--up">
              <h3>Don't have an account? Please Sign Up!</h3>
            </div>
            <div className="img__text m--in">
              <h3>If you already have an account, just Sign In.</h3>
            </div>
            <div className="img__btn" onClick={() => setIsSignUp(!isSignUp)}>
              <span className="m--up">Sign Up</span>
              <span className="m--in">Sign In</span>
            </div>
          </div>
          <div className="form sign-up">
            <form onSubmit={handleSignupSubmit}>
              <h2>Create your Account</h2>
              <label>
                <span>Name</span>
                <input
                  type="text"
                  value={signUpName}
                  onChange={(e) => setSignUpName(e.target.value)}
                  required
                />
              </label>
              <label>
                <span>Email</span>
                <input
                  type="email"
                  value={signUpEmail}
                  onChange={(e) => setSignUpEmail(e.target.value)}
                  required
                />
              </label>
              <label>
                <span>Password</span>
                <input
                  type="password"
                  value={signUpPassword}
                  onChange={(e) => setSignUpPassword(e.target.value)}
                  required
                />
              </label>
              {error && isSignUp && (
                <p
                  style={{
                    color: "red",
                    textAlign: "center",
                    marginTop: "10px",
                  }}
                >
                  {error}
                </p>
              )}
              <button type="submit" className="submit">
                Sign Up
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
