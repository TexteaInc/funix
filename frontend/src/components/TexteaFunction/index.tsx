import React, { useCallback, useState } from "react";
import { callFunction, FunctionDetail, FunctionPreview } from "@textea/shared";
import {
  Autocomplete,
  Button,
  Card,
  CardContent,
  Divider,
  Grid,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import ReactJson from "react-json-view";
import useSWR from "swr";
import { localApiURL } from "../../shared";
import SendIcon from "@mui/icons-material/Send";

export type FunctionDetailProps = {
  preview: FunctionPreview;
};

export const TexteaFunction: React.FC<FunctionDetailProps> = ({ preview }) => {
  const { data: detail } = useSWR<FunctionDetail>(
    new URL(preview.path, localApiURL).toString()
  );
  const [form, setForm] = useState<Record<string, any>>({});
  const [response, setResponse] = useState<any | null>(null);

  const handleSubmit = useCallback(
    async (event: any) => {
      event.preventDefault();
      console.log("form", form);
      const response = await callFunction(
        new URL(detail!.callee, localApiURL),
        form
      );
      setResponse(response);
    },
    [form, detail]
  );

  if (!detail) {
    return <Typography>Cannot fetch function detail</Typography>;
  }
  return (
    <>
      <Card>
        <CardContent>
          <Typography variant="h5" component="div">
            {detail.name}
          </Typography>
          <Typography sx={{ mb: 1.5 }} color="text.secondary">
            {new URL(detail.callee, localApiURL).toString()}
          </Typography>
          <Divider />
          <Typography variant="body2">Param Preview</Typography>
          <ReactJson src={detail.params} collapsed />
          <Stack spacing={1}>
            <Typography variant="body1">Input your data</Typography>
            <Stack spacing={1}>
              {Object.entries(detail.params).map(([key, value]) => (
                <Grid container spacing={1} alignItems="center" key={key}>
                  <Grid item xs="auto">
                    <Typography variant="body1">{key}:</Typography>
                  </Grid>
                  <Grid item xs>
                    <Autocomplete
                      freeSolo
                      getOptionLabel={(label) =>
                        typeof label === "string"
                          ? label
                          : Array.isArray(label)
                          ? `[${label}]`
                          : String(label)
                      }
                      onInputChange={(event, v) => {
                        if (/List/.test(value.type)) {
                          setForm((form) => ({
                            ...form,
                            [key]: v.substring(1, v.length - 2).split(","),
                          }));
                        } else {
                          setForm((form) => ({
                            ...form,
                            [key]: value.type === "int" ? Number(v) : v,
                          }));
                        }
                      }}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          type={value.type === "int" ? "number" : "text"}
                          name={key}
                          label={value.type}
                        />
                      )}
                      options={value.whitelist ?? value.example ?? []}
                    />
                  </Grid>
                </Grid>
              ))}
            </Stack>
            <Button
              type="submit"
              onClick={handleSubmit}
              variant="contained"
              endIcon={<SendIcon />}
            >
              Submit
            </Button>
            <ReactJson src={response ?? {}} />
          </Stack>
        </CardContent>
      </Card>
    </>
  );
};
