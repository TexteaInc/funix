import { Card, CardMedia } from "@mui/material";

export default function OutputPlotMedias(props: { media: string }) {
  return (
    <Card
      sx={{
        width: "fit-content",
      }}
    >
      <CardMedia
        component="img"
        image={props.media}
        sx={{
          maxWidth: "100%",
          maxHeight: "100%",
          width: "auto",
        }}
      />
    </Card>
  );
}
