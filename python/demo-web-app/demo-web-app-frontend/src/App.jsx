import React from "react";
import "./App.css";

import ScanHashForm from "./ScanHashForm";
import ScanFileForm from "./ScanFileForm";
import ScanURLForm from "./ScanURLForm";

export default function App(props) {
  return (
    <>
      <nav className="navbar navbar-dark bg-primary">
        <div className="container">
          <span className="navbar-brand">🚀 Demo Web App for Atlant</span>
        </div>
      </nav>
      <div className="container">
        <div className="card my-3">
          <h5 className="card-header">Scan a File</h5>
          <div className="card-body">
            <ScanFileForm />
          </div>
        </div>
        <div className="card my-3">
          <h5 className="card-header">Scan a File Using its Hash</h5>
          <div className="card-body">
            <ScanHashForm />
          </div>
        </div>
        <div className="card my-3">
          <h5 className="card-header">Scan a URL</h5>
          <div className="card-body">
            <ScanURLForm />
          </div>
        </div>
      </div>
    </>
  );
}
