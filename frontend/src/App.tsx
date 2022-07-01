import React from "react";
import { Container } from "@mui/material";
import { TexteaFunctionList } from "./components/TexteaFunctionList";
import { TexteaFunctionPreview } from "./components/TexteaFunctionPreview";

function App() {
  return (
    <Container>
      <TexteaFunctionList />
      <TexteaFunctionPreview />
    </Container>
  );
}

export default App;
