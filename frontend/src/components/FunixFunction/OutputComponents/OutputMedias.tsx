import { Card, CardMedia } from "@mui/material";
import PDFViewer from "../../Common/PDFViewer";

type FileType = string | File;

export default function OutputMedias(props: {
  medias: FileType[] | FileType;
  type: string;
  backend: string;
  outline?: boolean;
}) {
  const medias = Array.isArray(props.medias) ? props.medias : [props.medias];

  const component =
    props.type.toLowerCase().startsWith("image") ||
    props.type.toLowerCase().startsWith("figure")
      ? "img"
      : props.type.toLowerCase().startsWith("video")
        ? "video"
        : props.type.toLowerCase().startsWith("application/pdf")
          ? "pdf"
          : "audio";

  return (
    <>
      {medias.map((media, index) => {
        const relativeMedia =
          typeof media === "string"
            ? media.startsWith("/file/")
              ? new URL(media, props.backend).toString()
              : media
            : URL.createObjectURL(media);

        const isPDF = component === "pdf" || relativeMedia.endsWith(".pdf");

        const sx = isPDF
          ? {
              width: "100%",
              height: "100%",
              overflow: "auto",
            }
          : {
              width: "100%",
              height: "auto",
              maxWidth: "100%",
              maxHeight: "100%",
            };

        return (
          <Card
            key={index}
            sx={sx}
            variant={props.outline ? "outlined" : "elevation"}
          >
            {isPDF ? (
              <PDFViewer pdf={relativeMedia} />
            ) : (
              <CardMedia component={component} controls image={relativeMedia} />
            )}
          </Card>
        );
      })}
    </>
  );
}
