import React from "react";
import { Container } from "@mui/material";
import { TexteaFunctionList } from "./components/TexteaFunctionList";
import { TexteaFunctionSelected } from "./components/TexteaFunctionSelected";

function App() {
  return (
    <Container>
      <TexteaFunctionList />
      <TexteaFunctionSelected />
    </Container>
  );
}

export default App;
