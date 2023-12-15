import { Card, CardMedia } from "@mui/material";
import PDFViewer from "../../Common/PDFViewer";

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
    : props.type.toLowerCase().startsWith("application/pdf")
    ? "pdf"
    : "audio";

  return (
    <>
      {medias.map((media, index) => {
        const relativeMedia = media.startsWith("/file/")
          ? new URL(media, props.backend).toString()
          : media;

        const isPDF = component === "pdf" || relativeMedia.endsWith(".pdf");

        return (
          <Card
            key={index}
            sx={{
              width: "100%",
              height: "auto",
              maxWidth: "100%",
              maxHeight: "100%",
              minWidth: "65%",
            }}
            variant={props.outline ? "outlined" : "elevation"}
          >
            {isPDF ? (
              <PDFViewer pdf={relativeMedia} />
            ) : (
              <CardMedia
                component={component}
                controls
                image={relativeMedia}
                sx={{
                  minWidth: "500px",
                }}
              />
            )}
          </Card>
        );
      })}
    </>
  );
}
