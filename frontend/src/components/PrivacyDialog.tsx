import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import MarkdownDiv from "./Common/MarkdownDiv";
import { useEffect, useRef, useState } from "react";
import { getCookie, setCookie } from "typescript-cookie";
import React from "react";
import _ from "lodash";

export type PrivacyDialogProps = {
  backend: URL | undefined;
};

const PrivacyDialog: React.FC<PrivacyDialogProps> = ({ backend }) => {
  const [privacy, setPrivacy] = useState(false);
  const [privacyText, setPrivacyText] = useState("");
  const [logLevel, setLogLevel] = useState(0);
  const [lastPrivacyHash, setLastPrivacyHash] = useState("");
  const privacyDone = useRef(false);

  useEffect(() => {
    if (privacyDone.current) return;
    if (backend === undefined) return;
    fetch(new URL("/privacy", backend), {
      method: "GET",
    })
      .then((body) => {
        return body.json();
      })
      .then((json: { text: string; log_level: number; hash: string }) => {
        if (json.log_level !== 0) {
          setPrivacyText(json.text);
          setLogLevel(json.log_level);
          setLastPrivacyHash(json.hash);

          if (localStorage.getItem("privacy-hash") !== json.hash) {
            setPrivacy(true);
          } else {
            setPrivacy(
              json.log_level === 0
                ? false
                : getCookie("first-join") === undefined,
            );
          }
        }
        privacyDone.current = true;
      })
      .catch(() => {
        console.warn("No privacy text!");
      });
  }, [backend]);
  return (
    <Dialog open={privacy} fullWidth maxWidth="lg">
      <DialogTitle>Welcome to Funix</DialogTitle>
      <DialogContent>
        <MarkdownDiv markdown={privacyText} isRenderInline={false} />
      </DialogContent>
      <DialogActions>
        <Button
          onClick={() => {
            logLevel === 1
              ? setCookie("DO_NOT_LOG_ME", "YES")
              : (window.location.href = "http://funix.io");
            localStorage.setItem("privacy-hash", lastPrivacyHash);
            setCookie("first-join", "false", { expires: 365 * 10 });
            setPrivacy(false);
          }}
        >
          Do not track me
        </Button>
        <Button
          onClick={() => {
            setCookie("first-join", "false", { expires: 365 * 10 });
            setPrivacy(false);
            localStorage.setItem("privacy-hash", lastPrivacyHash);
          }}
        >
          Agree
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default React.memo(PrivacyDialog, (prevProps, nextProps) => {
  return _.isEqual(prevProps.backend, nextProps.backend);
});
