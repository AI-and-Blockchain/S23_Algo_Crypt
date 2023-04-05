import Logo from "./ac_logo.png";
import axios from 'axios';
import React, {useState, useEffect} from 'react';



export default function (props) {
    let [authMode, setAuthMode] = useState("signin");
    let [algorandAddress, setAlgorandAddress] = useState("");
    let [password, setPassword] = useState("");
    let [privateKey, setPrivateKey] = useState("");

  
    const changeAuthMode = () => {
      setAuthMode(authMode === "signin" ? "signup" : "signin");
    };
  
    const handleAlgorandAddressChange = (event) => {
      setAlgorandAddress(event.target.value);
    }
  
    const handlePasswordChange = (event) => {
      setPassword(event.target.value);
    }

    const handlePrivateKeyChange = (event) => {
      setPrivateKey(event.target.value);
    }
  
   
    const handleLogin = (event) => {
        event.preventDefault();
        const url = "http://127.0.0.1:8000/login";
        
        axios.post(url, { algorand_address: algorandAddress, password: password })
          .then(response => {
            console.log(response.data);
          })
          .catch(error => {
            console.error(error);
          });
      };

    const handleSignup = (event) => {
        event.preventDefault();
        const url = "http://127.0.0.1:8000/signup";
        axios.post(url, { algorand_address: algorandAddress, password: password, private_key: privateKey })
          .then(response => {
            console.log(response.data);
          })
          .catch(error => {
            console.error(error);
          });
      };

    
    

  if (authMode === "signin") {
    return (
      <div className="Auth-form-container">
        <img src={Logo} alt="Logo" style={{ width: "25%", border: "4px solid #007bff" }} />
        <form className="Auth-form" onSubmit={handleLogin}>
          <div className="Auth-form-content">
            <h3 className="Auth-form-title">Sign In</h3>
            <div className="text-center">
              Not registered yet?{" "}
              <span className="link-primary" onClick={changeAuthMode}>
                Sign Up
              </span>
            </div>
            <div className="form-group mt-3">
              <label>Algorand Address</label>
              <input
                type="text"
                className="form-control mt-1"
                placeholder="Enter Algorand Address"
                value={algorandAddress}
                onChange={handleAlgorandAddressChange}
              />
            </div>
            <div className="form-group mt-3">
              <label>Password</label>
              <input
                type="password"
                className="form-control mt-1"
                placeholder="Enter password"
                value={password}
                onChange={handlePasswordChange}
              />
            </div>
            <div className="d-grid gap-2 mt-3">
              <button type="submit" className="btn btn-primary" style={{ backgroundColor: "#007bff", borderColor: "#007bff" }} 
              onClick={handleLogin}>
                Submit
              </button>
            </div>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div className="Auth-form-container">
      <img src={Logo} alt="Logo" style={{ width: "25%", border: "4px solid #007bff" }} />
      <form className="Auth-form" onSubmit={handleSignup} >
        <div className="Auth-form-content">
          <h3 className="Auth-form-title">Sign Up</h3>
          <div className="text-center">
            Already registered?{" "}
            <span className="link-primary" onClick={changeAuthMode}>
              Sign In
            </span>
          </div>
          <div className="form-group mt-3">
            <label>Algorand Address</label>
            <input
              type="text"
              className="form-control mt-1"
              placeholder="Algorand Address"
              value = {algorandAddress}
              onChange = {handleAlgorandAddressChange}
            />
          </div>
          <div className="form-group mt-3">
            <label>Password</label>
            <input
              type="password"
              className="form-control mt-1"
              placeholder="Password"
              value = {password}
              onChange = {handlePasswordChange}
            />
          </div>
          <div className="form-group mt-3">
            <label>Private Key</label>
            <input
              type="password"
              className="form-control mt-1"
              placeholder="Private Key"
              value = {privateKey}
              onChange = {handlePrivateKeyChange}
            />
          </div>
          <div className="d-grid gap-2 mt-3">
            <button type="submit" className="btn btn-primary" style={{ backgroundColor: "#007bff", borderColor: "#007bff" }}
            onClick={handleSignup}>
              Submit
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}