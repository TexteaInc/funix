import React from "react";
import "./App.css";
import TexteaFunction from "./components/TexteaFunction/TexteaFunction";
import { Stack } from "@mui/material";

function App() {
  document.title = "PyDataFront";
  return (
    <Stack spacing={2} className="App">
      <TexteaFunction functionName="test" />
      <TexteaFunction functionName="calc" />
    </Stack>
  );
}

export default App;
