import React from "react";
const baseURL = "http://localhost:4010";

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
    const res = await fetch(
      new URL(`/param/${this.props.functionName}`, baseURL),
      {
        method: "GET",
      }
    );
    try {
      const functionParams = await res.json();
      console.log(functionParams);
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
      <div>
        <div className="TexteaFunctionDebugInfo">
          <p style={{ fontWeight: "bold" }}>Debug Info</p>
          <p>
            Function Name:&nbsp;
            <code>{this.props.functionName}</code>
          </p>
          <p>
            Function Param:&nbsp;
            <code>
              {JSON.stringify(this.state.functionParams, null, 1) ?? "null"}
            </code>
          </p>
        </div>
      </div>
    );
  }
}
