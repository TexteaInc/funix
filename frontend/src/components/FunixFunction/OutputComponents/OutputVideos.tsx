import { Card, CardMedia } from "@mui/material";

export default function OutputVideos(props: { videos: string[] | string }) {
  const videos = Array.isArray(props.videos) ? props.videos : [props.videos];

  return (
    <>
      {videos.map((video, index) => (
        <Card
          key={index}
          sx={{
            width: "100%",
            height: "auto",
            maxWidth: "100%",
            maxHeight: "100%",
          }}
        >
          <CardMedia component="video" controls image={video} />
        </Card>
      ))}
    </>
  );
}
