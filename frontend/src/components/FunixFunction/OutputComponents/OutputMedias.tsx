import { CardMedia } from "@mui/material";

export default function OutputMedias(props: {
  medias: string[] | string;
  type: string;
}) {
  const medias = Array.isArray(props.medias) ? props.medias : [props.medias];

  const component =
    props.type === "ImagesType"
      ? "img"
      : props.type === "videosType"
      ? "video"
      : "audio";

  return (
    <>
      {medias.map((media, index) => (
        <CardMedia component={component} controls image={media} key={index} />
      ))}
    </>
  );
}
