import { Card, CardMedia } from "@mui/material";

export default function OutputImages(props: { images: string[] | string }) {
  const images = Array.isArray(props.images) ? props.images : [props.images];

  return (
    <>
      {images.map((image, index) => (
        <Card
          key={index}
          sx={{
            width: "100%",
            height: "auto",
            maxWidth: "100%",
            maxHeight: "100%",
          }}
        >
          <CardMedia component="img" image={image} />
        </Card>
      ))}
    </>
  );
}
