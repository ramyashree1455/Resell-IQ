// Ramya's marketplace: its own page (open /market.html) so it never edits the AI app's files.
import React from "react";
import ReactDOM from "react-dom/client";
import MarketApp from "./MarketApp";
import "../styles.css";      // shared look from the main app
import "./market.css";       // a few marketplace-only extras

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <MarketApp />
  </React.StrictMode>
);
