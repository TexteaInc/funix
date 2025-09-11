import { WidgetProps } from "@rjsf/utils";
import React, { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardMedia,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from "@mui/material";
import { KetcherEditor } from "./components";
import { ChemEditorValue } from "./hooks";
import renderSvg from "../../shared/indigo-render";

interface ChemEditorProps {
  widget: WidgetProps;
  popup?: boolean;
}

const SimpleRenderBox = (props: { data: string | null }) => {
  return (
    <Card
      variant="outlined"
      elevation={0}
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        width: "100%",
        height: "200px",
      }}
    >
      {props.data ? (
        <CardMedia
          component="img"
          image={renderSvg(props.data)}
          alt="Chemistry"
          sx={{
            maxWidth: "100%",
            width: "auto",
            height: "200px",
          }}
        />
      ) : (
        <Typography variant="body1">No data</Typography>
      )}
    </Card>
  );
};

const ChemEditor: React.FC<ChemEditorProps> = React.memo((props) => {
  const [popUpKet, setPopUpKet] = useState<ChemEditorValue | null>(null);
  const [popUpOpen, setPopUpOpen] = useState(false);
  const [popUpKetTemp, setPopUpKetTemp] = useState<ChemEditorValue | null>(
    null,
  );

  const initialValue = props.widget.value ?? props.widget.formData ?? null;

  const handleChange = (newValue: ChemEditorValue) => {
    props.widget.onChange(newValue);
    setPopUpKet(newValue);
  };

  if (props.popup) {
    return (
      <Box
        sx={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          gap: 1,
        }}
      >
        <SimpleRenderBox data={popUpKet?.ket ?? null} />
        <Button
          onClick={() => setPopUpOpen(true)}
          sx={{ width: "100%" }}
          variant="contained"
        >
          Open Editor
        </Button>
        <Dialog
          open={popUpOpen}
          onClose={() => setPopUpOpen(false)}
          fullWidth
          maxWidth="xl"
        >
          <DialogTitle>Editor</DialogTitle>
          <DialogContent>
            <KetcherEditor
              initialValue={initialValue}
              onChange={(value) => setPopUpKetTemp(value)}
              height="80vh"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setPopUpOpen(false)}>Cancel</Button>
            <Button
              disabled={popUpKetTemp === null}
              onClick={() => {
                setPopUpOpen(false);
                if (popUpKetTemp !== null) {
                  handleChange(popUpKetTemp);
                  setPopUpKetTemp(null);
                }
              }}
            >
              Confirm
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    );
  }

  return <KetcherEditor initialValue={initialValue} onChange={handleChange} />;
});

export default ChemEditor;
