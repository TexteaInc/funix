import React from "react";
import { Stack } from "@mui/material";
import TexteaFunctionInfoCard from "./TexteaFunctionInfoCard";
import TexteaFunctionCallerCard from "./TexteaFunctionCallerCard";

export const baseURL = "http://localhost:4010";

export interface TexteaFunctionProps {
  functionName: string;
}

export interface TexteaFunctionState {
  error: any;
  isLoaded: boolean;
  functionParams?: any;
}

export default class TexteaFunction extends React.Component<
  TexteaFunctionProps,
  TexteaFunctionState
> {
  constructor(props: TexteaFunctionProps) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
    };
  }

  async componentDidMount() {
    const response = await fetch(
      new URL(`/param/${this.props.functionName}`, baseURL),
      {
        method: "GET",
      }
    );
    try {
      const functionParams = await response.json();
      this.setState({
        isLoaded: true,
        functionParams,
      });
    } catch (error) {
      this.setState({
        isLoaded: true,
        error,
      });
    }
  }

  render() {
    return (
      <Stack spacing={2}>
        <TexteaFunctionInfoCard
          functionName={this.props.functionName}
          functionParams={this.state.functionParams}
        />
        <TexteaFunctionCallerCard
          functionName={this.props.functionName}
          functionParams={this.state.functionParams}
        />
      </Stack>
    );
  }
}
