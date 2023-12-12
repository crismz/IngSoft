import React from "react";
import ReactDOM from "react-dom/client";
import "./assets/fonts/fontgood.css";
import { RouterProvider } from "react-router-dom";
import router from "./routes.jsx";
import BackgroundContainer from "./components/BackgroundContainer/BackgroundContainer.jsx";
import "./main.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BackgroundContainer>
    <RouterProvider router={router} />
  </BackgroundContainer>
);
