import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";

console.log("[BOOT] main.tsx START");

// Minimal test to see if React loads
const TestApp = () => {
  console.log("[BOOT] TestApp rendering");
  return (
    <div style={{ padding: "20px", background: "lightblue", minHeight: "100vh" }}>
      <h1 style={{ color: "black" }}>🔥 React läuft!</h1>
      <p style={{ color: "black" }}>Wenn du das siehst, funktioniert React.</p>
    </div>
  );
};

console.log("[BOOT] Creating root");
const root = createRoot(document.getElementById("root")!);
console.log("[BOOT] Rendering TestApp");
root.render(
  <StrictMode>
    <TestApp />
  </StrictMode>
);
console.log("[BOOT] Render complete");
