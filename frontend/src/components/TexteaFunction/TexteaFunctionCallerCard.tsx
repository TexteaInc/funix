import {
  Button,
  Card,
  CardContent,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import React from "react";
import SendIcon from "@mui/icons-material/Send";
import { localApiURL } from "../../shared";

export interface TexteaFunctionCallerCardProps {
  functionName: string;
  functionParams: any;
}

export interface TexteaFunctionCallerCardState {
  form: any;
  customized: string[];
  responseStr: string;
}

export default class TexteaFunctionCallerCard extends React.Component<
  TexteaFunctionCallerCardProps,
  TexteaFunctionCallerCardState
> {
  constructor(props: TexteaFunctionCallerCardProps) {
    super(props);
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleExampleInputChange = this.handleExampleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount() {
    this.setState({
      form: {},
      customized: [],
    });
  }

  componentDidUpdate(prevProps: TexteaFunctionCallerCardProps) {
    if (prevProps !== this.props) {
      this.setState({
        form: {},
        customized: [],
      });
    }
  }

  handleInputChange(event: any) {
    const target = event.target;
    const value = target.type === "checkbox" ? target.checked : target.value;
    const name = target.name;

    this.setState((prevState) => ({
      form: {
        ...prevState.form,
        [name]: value,
      },
    }));
  }

  handleExampleInputChange(event: any) {
    const target = event.target;
    let value = target.type === "checkbox" ? target.checked : target.value;
    const name = target.name;

    if (target.value === ".customize") {
      this.setState((prevState) => ({
        customized: [...prevState.customized, name],
      }));
      if (value === ".customize") {
        value = "";
      }
    } else if (target.value === "") {
      this.setState((prevState) => ({
        customized: [...prevState.customized.filter((x) => x !== name)],
      }));
    }

    this.setState((prevState) => ({
      form: {
        ...prevState.form,
        [name]: value,
      },
    }));
  }

  async handleSubmit(event: any) {
    event.preventDefault();
    const data = new FormData(event.target);
    const response = await fetch(
      new URL(this.props.functionParams?.path, localApiURL),
      {
        method: "POST",
        body: data,
      }
    );
    this.setState({ responseStr: await response.text() });
  }

  getFunctionParamsRows(decoratedParams: any) {
    if (!decoratedParams) return "null";
    const rows = Object.keys(decoratedParams)?.map((argName: string) => (
      <Grid
        container
        item
        spacing={1}
        key={`row-${argName}`}
        alignItems="center"
      >
        <Grid item xs="auto">
          <Typography variant="body1">{argName}:</Typography>
        </Grid>
        <Grid item xs>
          {this.getInputField(argName, decoratedParams[argName])}
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

  iterateCandidatesForSelectMenuItems(
    element: any,
    argName: string,
    argType: string
  ) {
    const supportedBasicTypes = ["int", "float", "str"];
    let elementStr: string;
    if (supportedBasicTypes.includes(argType)) {
      elementStr = element.toString();
    } else {
      elementStr = JSON.stringify(element, null, 1);
    }
    return (
      <MenuItem value={elementStr} key={`select-${argName}-${elementStr}`}>
        {elementStr}
      </MenuItem>
    );
  }

  getInputField(argName: string, argParams: any) {
    if (argParams.hasOwnProperty("whitelist")) {
      const menuItems = argParams["whitelist"].map((element: any) =>
        this.iterateCandidatesForSelectMenuItems(
          element,
          argName,
          argParams["type"]
        )
      );
      return (
        <FormControl fullWidth>
          <InputLabel>{argParams["type"]}</InputLabel>
          <Select
            name={argName}
            value={this.state.form[argName] ?? ""}
            label={argParams["type"]}
            onChange={this.handleInputChange}
          >
            <MenuItem value="">
              <em>None</em>
            </MenuItem>
            {menuItems}
          </Select>
        </FormControl>
      );
    } else if (argParams.hasOwnProperty("example")) {
      if (this.state.customized.includes(argName)) {
        return (
          <FormControl fullWidth>
            <TextField
              name={argName}
              value={this.state.form[argName] ?? ""}
              label={argParams["type"]}
              onChange={this.handleExampleInputChange}
              type="search"
            />
          </FormControl>
        );
      } else {
        const menuItems = argParams["example"].map((element: any) =>
          this.iterateCandidatesForSelectMenuItems(
            element,
            argName,
            argParams["type"]
          )
        );
        return (
          <FormControl fullWidth>
            <InputLabel>{argParams["type"]}</InputLabel>
            <Select
              name={argName}
              value={this.state.form[argName] ?? ""}
              label={argParams["type"]}
              onChange={this.handleExampleInputChange}
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {menuItems}
              <MenuItem value=".customize">
                <em>Customize…</em>
              </MenuItem>
            </Select>
          </FormControl>
        );
      }
    } else {
      return (
        <FormControl fullWidth>
          <TextField
            name={argName}
            value={this.state.form[argName] ?? ""}
            label={argParams["type"]}
            onChange={this.handleInputChange}
          />
        </FormControl>
      );
    }
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
