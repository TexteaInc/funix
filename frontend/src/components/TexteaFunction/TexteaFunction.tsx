import React from "react";
import { Stack } from "@mui/material";
import TexteaFunctionInfoCard from "./TexteaFunctionInfoCard";
import TexteaFunctionCallerCard from "./TexteaFunctionCallerCard";
import { API_URL } from "../../shared";

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

  async updateState() {
    const response = await fetch(
      new URL(`/param/${this.props.functionName}`, API_URL),
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

  async componentDidMount() {
    await this.updateState();
  }

  async componentDidUpdate(prevProps: TexteaFunctionProps) {
    if (prevProps !== this.props) {
      this.setState({
        error: null,
        isLoaded: false,
      });
      await this.updateState();
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
