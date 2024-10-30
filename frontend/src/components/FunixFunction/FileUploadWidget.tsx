import { DropzoneOptions, useDropzone } from "react-dropzone";
import React, { useCallback, useEffect, useLayoutEffect } from "react";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  ImageList,
  ImageListItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableFooter,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import {
  CameraAlt,
  Close,
  Delete,
  FileUpload,
  KeyboardVoice,
  Preview,
} from "@mui/icons-material";
import OutputMedias from "./OutputComponents/OutputMedias";
import { useAtom } from "jotai";
import { storeAtom } from "../../store";
import { enqueueSnackbar } from "notistack";
import FunixRecorder from "../../shared/media";
import { WidgetProps } from "@rjsf/utils";

interface FileUploadWidgetInterface {
  widget: WidgetProps;
  multiple: boolean;
  supportType: "image" | "audio" | "video" | "file";
  data?: any;
}

const fileToBase64 = (file: File) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });
};

const fileSizeToReadable = (size: number) => {
  const units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
  let l = 0;
  let n = size;
  while (n >= 1024) {
    n /= 1024;
    l++;
  }
  return `${n.toFixed(n < 10 && l > 0 ? 1 : 0)} ${units[l]}`;
};

const base64stringToFile = (base64: string) => {
  const byteString = window.atob(base64.split(",")[1]);
  const ab = new ArrayBuffer(byteString.length);
  const ia = new Uint8Array(ab);
  for (let i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }
  const fileBlob = new Blob([ab]);

  const fileType = base64.split(",")[0].split(":")[1].split(";")[0];
  return new File([fileBlob], "History back, no metadata keep.", {
    type: fileType,
  });
};

const CameraPreviewVideo = () => {
  useLayoutEffect(() => {
    const video = document.getElementById("videoPreview") as HTMLVideoElement;
    navigator.mediaDevices
      .getUserMedia({ video: true, audio: false })
      .then((stream) => {
        video.srcObject = stream;
        video.play().catch((err) => {
          console.log(err);
        });
      })
      .catch((err) => {
        console.log(err);
      });
  });
  return <video id="videoPreview" autoPlay muted />;
};

const FileUploadWidget = (props: FileUploadWidgetInterface) => {
  const [{ backHistory }] = useAtom(storeAtom);
  const [files, setFiles] = React.useState<File[]>([]);
  const [open, setOpen] = React.useState(false);
  const [cameraOpen, setCameraOpen] = React.useState(false);
  const [preview, setPreview] = React.useState<File | null>(null);
  const [previewType, setPreviewType] = React.useState<string>("");
  const [confirmOpen, setConfirmOpen] = React.useState(false);
  const [audioRecoding, setAudioRecording] = React.useState(false);
  const [webcamRecoding, setWebcamRecording] = React.useState(false);
  const [update, setUpdate] = React.useState(new Date().getTime());
  const supportMediaDevices = navigator.mediaDevices !== undefined;
  const funixRecorder = new FunixRecorder();

  let dropzoneConfig: DropzoneOptions = !props.multiple
    ? { multiple: false, maxFiles: 1, maxSize: 1024 * 1024 * 15 }
    : { multiple: true, maxFiles: 0, maxSize: 1024 * 1024 * 15 };

  switch (props.supportType) {
    case "image":
      dropzoneConfig = { ...dropzoneConfig, accept: { "image/*": [] } };
      break;
    case "audio":
      dropzoneConfig = { ...dropzoneConfig, accept: { "audio/*": [] } };
      break;
    case "video":
      dropzoneConfig = { ...dropzoneConfig, accept: { "video/*": [] } };
      break;
  }

  dropzoneConfig = {
    ...dropzoneConfig,
    onDrop: useCallback(
      (acceptedFiles: File[]) => {
        if (props.multiple) {
          if (files.length + acceptedFiles.length > 5) {
            enqueueSnackbar(
              "Files are limited to 5, use WebAPI to call this function",
              {
                variant: "warning",
              },
            );
          } else {
            setFiles([...files, ...acceptedFiles]);
          }
        } else {
          if (acceptedFiles.length > 0) {
            setFiles([...acceptedFiles]);
          }
        }
      },
      [files],
    ),
  };

  const { acceptedFiles, getRootProps, getInputProps, fileRejections } =
    useDropzone(dropzoneConfig);

  useEffect(() => {
    if (files.length > 0) {
      if (props.multiple) {
        Promise.all(files.map((file) => fileToBase64(file))).then((values) => {
          props.widget.onChange(values);
        });
      } else {
        fileToBase64(files[0]).then((value) => {
          props.widget.onChange(value);
        });
      }
    }
  }, [acceptedFiles, update]);

  useEffect(() => {
    fileRejections.forEach((file) => {
      if (file.file.size >= 1024 * 1024 * 15) {
        enqueueSnackbar(
          `${file.file.name} is bigger than 15MB, use WebAPI to call this function`,
          {
            variant: "warning",
          },
        );
      } else {
        enqueueSnackbar(
          `${file.file.name} is not a valid ${props.supportType}`,
          {
            variant: "warning",
          },
        );
      }
    });
  }, [fileRejections]);

  useEffect(() => {
    if (backHistory !== null && backHistory["input"] !== null) {
      setFiles([]);
      // ehh no, need somebody write better code please
      const data = backHistory["input"][props.widget.name];
      if (typeof data === "string") {
        setFiles([base64stringToFile(data)]);
      } else {
        const newFiles = (data as string[]).map((data) =>
          base64stringToFile(data),
        );
        setFiles(newFiles);
      }
    }
  }, [backHistory]);

  // window.addEventListener("funix-rollback-now", () => {
  //   if (
  //     props.data !== null &&
  //     typeof props.data !== "undefined" &&
  //     (typeof props.data === "object" && Array.isArray(props.data)
  //       ? props.data.length > 0
  //       : Object.keys(props.data).length > 0)
  //   ) {
  //     const backData = props.multiple
  //       ? (props.data as string[])
  //       : [props.data as string];
  //     setFiles([]);
  //     const newFiles = backData.map((data) => base64stringToFile(data));
  //     setFiles(newFiles);
  //   }
  // });

  const removeFile = (index: number) => {
    const newFiles = [...files];
    newFiles.splice(index, 1);
    setFiles(newFiles);
  };

  const removeAllFiles = () => {
    setFiles([]);
  };

  const fileString = props.multiple
    ? `${props.supportType}s`
    : props.supportType;

  return (
    <>
      <Dialog
        open={cameraOpen}
        onClose={() => setCameraOpen(false)}
        maxWidth="xl"
        fullWidth
      >
        <DialogTitle>Camera Preview</DialogTitle>
        <Button
          startIcon={<Close />}
          color="error"
          onClick={() => setCameraOpen(false)}
          sx={{
            position: "absolute",
            right: 8,
            top: 14,
          }}
        >
          Close
        </Button>
        <CameraPreviewVideo />
        <DialogActions>
          {(props.supportType === "file" || props.supportType === "image") && (
            <Button
              onClick={() => {
                const canvas = document.createElement("canvas");
                const video = document.getElementById(
                  "videoPreview",
                ) as HTMLVideoElement;
                const videoRect = video.getBoundingClientRect();
                canvas.width = videoRect.width;
                canvas.height = videoRect.height;
                canvas
                  .getContext("2d")
                  ?.drawImage(video, 0, 0, videoRect.width, videoRect.height);
                canvas.toBlob((blob) => {
                  if (blob) {
                    const now = new Date().getTime();
                    const file = new File([blob], `image-${now}.png`, {
                      type: "image/png",
                    });
                    if (props.multiple) {
                      setFiles([...files, file]);
                    } else {
                      setFiles([file]);
                    }
                    setUpdate(new Date().getTime());
                  }
                });
              }}
            >
              Take a Photo
            </Button>
          )}
          {(props.supportType === "file" || props.supportType === "video") && (
            <Button
              id="videoRecord"
              onClick={() => {
                if (!webcamRecoding) {
                  setWebcamRecording(true);
                  funixRecorder.videoRecord((file) => {
                    if (props.multiple) {
                      setFiles([...files, file]);
                    } else {
                      setFiles([file]);
                    }
                    setUpdate(new Date().getTime());
                    setWebcamRecording(false);
                  }, false);
                }
              }}
            >
              {webcamRecoding ? "Stop" : "Record"}
            </Button>
          )}
        </DialogActions>
      </Dialog>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        maxWidth="lg"
        fullWidth={previewType === "application/pdf"}
        PaperProps={{
          style: {
            height: previewType === "application/pdf" ? "80vh" : "auto",
          },
        }}
      >
        <DialogTitle>Media Preview</DialogTitle>
        <DialogContent>
          {preview !== null ? (
            <OutputMedias
              medias={preview}
              type={previewType}
              backend={""}
              outline={true}
            />
          ) : (
            <Typography variant="body2">No preview available</Typography>
          )}
        </DialogContent>
        <DialogActions
          sx={{
            width: "100%",
            paddingRight: 2.5,
          }}
        >
          <Button onClick={() => setOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={confirmOpen} onClose={() => setConfirmOpen(false)}>
        <DialogTitle>Delete All?</DialogTitle>
        <DialogContent>
          <Typography variant="body2">
            Are you sure you want to delete all {fileString}?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmOpen(false)}>Cancel</Button>
          <Button
            onClick={() => {
              removeAllFiles();
              setConfirmOpen(false);
            }}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
      <Stack
        direction="column"
        alignItems="center"
        justifyContent="center"
        sx={{ width: "100%" }}
        spacing={2}
      >
        <Paper
          sx={{
            width: "100%",
            cursor: "pointer",
          }}
          variant="outlined"
          {...getRootProps({ className: "dropzone" })}
        >
          <Stack
            direction="column"
            alignItems="center"
            justifyContent="center"
            spacing={2}
          >
            <input {...getInputProps()} />
            <Typography
              variant="body2"
              sx={{
                paddingX: 2,
              }}
            >
              Drag and drop some {fileString} here, or click to select{" "}
              {fileString}
            </Typography>
            <FileUpload fontSize="large" />
            <Typography variant="caption">
              {files.length} {fileString} selected
            </Typography>
            <Stack direction="row" spacing={2}>
              <Button
                color="primary"
                startIcon={<CameraAlt />}
                size="small"
                disabled={!supportMediaDevices}
                onClick={(event) => {
                  setCameraOpen(true);
                  event.stopPropagation();
                }}
              >
                Webcam
              </Button>
              <Button
                id="audioRecord"
                color="primary"
                startIcon={<KeyboardVoice />}
                size="small"
                disabled={
                  !supportMediaDevices &&
                  (props.supportType === "audio" ||
                    props.supportType === "file")
                }
                onClick={(event) => {
                  if (!audioRecoding) {
                    setAudioRecording(true);
                    funixRecorder.audioRecord((file) => {
                      if (props.multiple) {
                        setFiles([...files, file]);
                      } else {
                        setFiles([file]);
                      }
                      setUpdate(new Date().getTime());
                      setAudioRecording(false);
                    });
                  }
                  event.stopPropagation();
                }}
              >
                {audioRecoding ? "Stop" : "Microphone"}
              </Button>
            </Stack>
            <br />
          </Stack>
        </Paper>
        {files.filter((file) => file.type.startsWith("image")).length !== 0 && (
          <ImageList variant="masonry" cols={3} gap={8} sx={{ width: "100%" }}>
            {files
              .filter((file) => file.type.startsWith("image"))
              .map((item) => (
                <ImageListItem key={item.name}>
                  <img
                    src={URL.createObjectURL(item)}
                    alt={item.name}
                    title={item.name}
                    loading="lazy"
                    onClick={() => {
                      setPreview(item);
                      setPreviewType(item.type);
                      setOpen(true);
                    }}
                  />
                </ImageListItem>
              ))}
          </ImageList>
        )}
        <TableContainer component={Paper}>
          <Table
            sx={{
              width: "100%",
            }}
            size="small"
          >
            <TableHead>
              <TableRow>
                <TableCell>File Name</TableCell>
                <TableCell>File Size</TableCell>
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {files.length > 0 ? (
                files.map((file, index) => {
                  return (
                    <TableRow key={index}>
                      <TableCell
                        align="left"
                        sx={{
                          minWidth: "50%",
                        }}
                      >
                        {file.name}
                      </TableCell>
                      <TableCell align="left">
                        {fileSizeToReadable(file.size)}
                      </TableCell>
                      <TableCell align="left">
                        <Button
                          variant="text"
                          size="small"
                          startIcon={<Delete fontSize="small" />}
                          onClick={() => {
                            removeFile(index);
                          }}
                          color="error"
                        >
                          Delete
                        </Button>
                        {(file.type.startsWith("image") ||
                          file.type.startsWith("video") ||
                          file.type.startsWith("audio") ||
                          file.type === "application/pdf") && (
                          <Button
                            variant="text"
                            size="small"
                            startIcon={<Preview fontSize="small" />}
                            onClick={() => {
                              setPreviewType(file.type);
                              setPreview(file);
                              setOpen(true);
                            }}
                          >
                            Preview
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })
              ) : (
                <TableCell colSpan={3} align="center">
                  No files
                </TableCell>
              )}
            </TableBody>
            <TableFooter>
              <TableCell>
                <Button
                  color="error"
                  startIcon={<Delete />}
                  onClick={() => {
                    setConfirmOpen(true);
                  }}
                  size="small"
                  disabled={files.length === 0}
                >
                  Delete All
                </Button>
              </TableCell>
              <TableCell colSpan={2} align="right">
                <Typography variant="caption" component="span">
                  You can select up to 5 files, limited to 15MB for each file
                </Typography>
              </TableCell>
            </TableFooter>
          </Table>
        </TableContainer>
      </Stack>
    </>
  );
};

export default FileUploadWidget;
