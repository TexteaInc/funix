import React from "react";
import "./App.css";
import TexteaFunction from "./components/TexteaFunction";

function App() {
  document.title = "PyDataFront";
  return (
    <div className="App">
      <TexteaFunction functionName="test" />
    </div>
  );
}

export default App;
