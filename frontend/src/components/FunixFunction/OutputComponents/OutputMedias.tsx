import { Card, CardMedia } from "@mui/material";

export default function OutputMedias(props: {
  medias: string[] | string;
  type: string;
  backend: string;
  outline?: boolean;
}) {
  const medias = Array.isArray(props.medias) ? props.medias : [props.medias];

  const component = props.type.toLowerCase().startsWith("image")
    ? "img"
    : props.type.toLowerCase().startsWith("video")
    ? "video"
    : "audio";

  return (
    <>
      {medias.map((media, index) => {
        const relativeMedia = media.startsWith("/file/")
          ? new URL(media, props.backend).toString()
          : media;

        return (
          <Card
            key={index}
            sx={{
              width: "100%",
              height: "auto",
              maxWidth: "100%",
              maxHeight: "100%",
            }}
            variant={props.outline ? "outlined" : "elevation"}
          >
            <CardMedia component={component} controls image={relativeMedia} />
          </Card>
        );
      })}
    </>
  );
}
