import {
  Button,
  Card,
  CardContent,
  Divider,
  Grid,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import React from "react";
import SendIcon from "@mui/icons-material/Send";
import { baseURL } from "./TexteaFunction";

export interface TexteaFunctionCallerCardProps {
  functionName: string;
  functionParams: any;
}

export interface TexteaFunctionCallerCardState {
  responseStr: string;
}

export default class TexteaFunctionCallerCard extends React.Component<
  TexteaFunctionCallerCardProps,
  TexteaFunctionCallerCardState
> {
  constructor(props: TexteaFunctionCallerCardProps) {
    super(props);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  async handleSubmit(event: any) {
    event.preventDefault();
    const data = new FormData(event.target);
    const response = await fetch(
      new URL(this.props.functionParams?.path, baseURL),
      {
        method: "POST",
        body: data,
      }
    );
    this.setState({ responseStr: await response.text() });
  }

  getFunctionParamsRows(decoratedParams: any) {
    if (!decoratedParams) return "null";
    const rows = Object.keys(decoratedParams)?.map((key: string) => (
      <Grid container item spacing={1} key={key} alignItems="center">
        <Grid item xs="auto">
          <Typography variant="body1">{key}:</Typography>
        </Grid>
        <Grid item xs>
          <code>{this.getInputField(key, decoratedParams[key])}</code>
        </Grid>
      </Grid>
    ));
    return (
      <form onSubmit={this.handleSubmit}>
        <Stack spacing={1}>
          <Grid container rowSpacing={1}>
            {rows}
          </Grid>
          <Divider />
          <Button type="submit" variant="contained" endIcon={<SendIcon />}>
            Send
          </Button>
        </Stack>
      </form>
    );
  }

  getInputField(argName: string, argParams: any) {
    return <TextField name={argName} label={argParams["type"]} />;
  }

  getResponse() {
    return (
      <Stack>
        <Typography variant="h6">Last Response</Typography>
        <Typography variant="body1">
          <pre>{this.state?.responseStr ?? "null"}</pre>
        </Typography>
      </Stack>
    );
  }

  render() {
    return (
      <Card>
        <CardContent>
          <Stack spacing={1}>
            <Typography variant="h4">{this.props.functionName}</Typography>
            <Divider />
            {this.getFunctionParamsRows(
              this.props.functionParams?.decorated_params
            )}
            <Divider />
            {this.getResponse()}
          </Stack>
        </CardContent>
      </Card>
    );
  }
}
