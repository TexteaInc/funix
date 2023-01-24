import { Card, CardMedia } from "@mui/material";

export default function OutputMedias(props: {
  medias: string[] | string;
  type: string;
}) {
  const medias = Array.isArray(props.medias) ? props.medias : [props.medias];

  console.log(medias);

  const component =
    props.type === "ImagesType"
      ? "img"
      : props.type === "VideosType"
      ? "video"
      : "audio";

  return (
    <>
      {medias.map((media, index) => (
        <Card
          key={index}
          sx={{
            width: "100%",
            height: "auto",
            maxWidth: "100%",
            maxHeight: "100%",
          }}
        >
          <CardMedia component={component} controls image={media} />
        </Card>
      ))}
    </>
  );
}
