import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import ErrorBoundary from "./components/ErrorBoundary";

console.log("[Boot] main.tsx starting...");

createRoot(document.getElementById("root")!).render(<App />);
