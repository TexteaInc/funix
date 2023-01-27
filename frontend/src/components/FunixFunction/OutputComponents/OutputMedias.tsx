import { Card, CardMedia } from "@mui/material";

export default function OutputMedias(props: {
  medias: string[] | string;
  type: string;
  backend: string;
}) {
  const medias = Array.isArray(props.medias) ? props.medias : [props.medias];
  const imagesType = ["ImagesType", "images"];
  const videosType = ["VideosType", "videos"];

  const component =
    imagesType.indexOf(props.type) !== -1
      ? "img"
      : videosType.indexOf(props.type) !== -1
      ? "video"
      : "audio";

  return (
    <>
      {medias.map((media, index) => {
        const relativeMedia = media.startsWith("/files/")
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
