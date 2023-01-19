import { Card, CardMedia } from "@mui/material";

export default function OutputAudios(props: { audios: string[] | string }) {
  const audios = Array.isArray(props.audios) ? props.audios : [props.audios];

  return (
    <>
      {audios.map((audio, index) => (
        <Card
          key={index}
          sx={{
            width: "100%",
            height: "auto",
            maxWidth: "100%",
            maxHeight: "100%",
          }}
        >
          <CardMedia component="audio" controls image={audio} />
        </Card>
      ))}
    </>
  );
}
