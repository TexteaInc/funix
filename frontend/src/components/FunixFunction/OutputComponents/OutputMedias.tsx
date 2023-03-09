import { Card, CardMedia } from "@mui/material";

export default function OutputMedias(props: {
  medias: string[] | string;
  type: string;
  backend: string;
}) {
  const medias = Array.isArray(props.medias) ? props.medias : [props.medias];

  const component =
    props.type.toLowerCase() === "images"
      ? "img"
      : props.type.toLowerCase() === "videos"
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
          >
            <CardMedia component={component} controls image={relativeMedia} />
          </Card>
        );
      })}
    </>
  );
}
