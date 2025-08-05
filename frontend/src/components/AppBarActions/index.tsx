import React, { useState } from "react";
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Button,
  FormGroup,
  FormControlLabel,
  Switch,
  InputAdornment,
} from "@mui/material";
import {
  MoreVert,
  Settings,
  History,
  EventNote,
  Share,
  Token,
  ContentCopy,
  Code,
} from "@mui/icons-material";
import { useAtom } from "jotai";
import {
  appSecretAtom,
  functionSecretAtom,
  selectedFunctionAtom,
  showFunctionDetailAtom,
  saveHistoryAtom,
} from "../../store";
import { useNavigate } from "react-router-dom";
import { useSnackbar } from "notistack";

export interface AppBarActionsProps {
  isTabBarMode?: boolean;
  trigger?: React.ReactElement;
  backend?: URL;
  onShareUrlChange?: (url: string) => void;
  shareUrl?: string;
  onHistoryOpen?: () => void;
  onHistorySideBarToggle?: () => void;
}

const AppBarActions: React.FC<AppBarActionsProps> = ({
  isTabBarMode = false,
  trigger,
  backend,
  onShareUrlChange,
  shareUrl = window.location.href,
  onHistoryOpen,
  onHistorySideBarToggle,
}) => {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const [selectedFunction] = useAtom(selectedFunctionAtom);
  const [appSecret, setAppSecret] = useAtom(appSecretAtom);
  const [functionSecret, setFunctionSecret] = useAtom(functionSecretAtom);
  const [showFunctionDetail, setShowFunctionDetail] = useAtom(
    showFunctionDetailAtom,
  );
  const [saveHistory, setSaveHistory] = useAtom(saveHistoryAtom);

  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [tokenOpen, setTokenOpen] = useState(false);
  const [shareOpen, setShareOpen] = useState(false);

  const [tempBackend, setTempBackend] = useState(backend?.origin || "");
  const [tempAppSecret, setTempAppSecret] = useState(appSecret);
  const [tempSecret, setTempSecret] = useState("");
  const [tempShareUrl, setTempShareUrl] = useState(shareUrl);

  const selectedFunctionSecret: string | null = selectedFunction?.secret
    ? selectedFunction?.path in functionSecret
      ? functionSecret[selectedFunction?.path]
      : appSecret
    : null;

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const handleSettingsOpen = () => {
    setTempBackend(backend?.origin || "");
    setTempAppSecret(appSecret);
    setSettingsOpen(true);
    handleMenuClose();
  };

  const handleTokenOpen = () => {
    setTempSecret(selectedFunctionSecret || "");
    setTokenOpen(true);
    handleMenuClose();
  };

  const handleShareOpen = () => {
    setTempShareUrl(shareUrl);
    setShareOpen(true);
    handleMenuClose();
  };

  const checkURL = (url: string | undefined): boolean => {
    if (!url) return false;
    try {
      new URL(url);
      return true;
    } catch (e) {
      return false;
    }
  };

  const handleSettingsConfirm = () => {
    navigate("/");
    setAppSecret(tempAppSecret);
    setSettingsOpen(false);
  };

  const handleTokenConfirm = () => {
    if (selectedFunction) {
      setFunctionSecret((store) => ({
        ...store,
        [selectedFunction.path]: tempSecret,
      }));
    }
    setTokenOpen(false);
  };

  const handleShareConfirm = () => {
    onShareUrlChange?.(tempShareUrl);
    setShareOpen(false);
  };

  const copyToClipboard = (text: string, message: string) => {
    navigator.clipboard.writeText(text).then(() => {
      enqueueSnackbar(message, { variant: "success" });
    });
  };

  const defaultTrigger = (
    <IconButton
      size="large"
      color="inherit"
      onClick={handleMenuOpen}
      sx={{
        ...(isTabBarMode && {
          color: "text.primary",
          backgroundColor: "transparent",
        }),
      }}
    >
      <MoreVert />
    </IconButton>
  );

  return (
    <>
      {trigger
        ? React.cloneElement(trigger, { onClick: handleMenuOpen })
        : defaultTrigger}

      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "right",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
      >
        {selectedFunction && selectedFunction.secret && (
          <MenuItem onClick={handleTokenOpen}>
            <ListItemIcon>
              <Token />
            </ListItemIcon>
            <ListItemText primary="Secret Token" />
          </MenuItem>
        )}

        <MenuItem
          onClick={() => {
            onHistoryOpen?.();
            handleMenuClose();
          }}
        >
          <ListItemIcon>
            <History />
          </ListItemIcon>
          <ListItemText primary="History" />
        </MenuItem>

        <MenuItem
          onClick={() => {
            onHistorySideBarToggle?.();
            handleMenuClose();
          }}
        >
          <ListItemIcon>
            <EventNote />
          </ListItemIcon>
          <ListItemText primary="History Sidebar" />
        </MenuItem>

        <MenuItem onClick={handleShareOpen}>
          <ListItemIcon>
            <Share />
          </ListItemIcon>
          <ListItemText primary="Share" />
        </MenuItem>

        <Divider />

        <MenuItem onClick={handleSettingsOpen}>
          <ListItemIcon>
            <Settings />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </MenuItem>
      </Menu>

      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)}>
        <DialogTitle>Settings</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="Backend URL"
            fullWidth
            variant="standard"
            onChange={(e) => setTempBackend(e.target.value)}
            value={tempBackend}
            error={!checkURL(tempBackend)}
          />
          <TextField
            margin="dense"
            label="All pages secret (for this app)"
            fullWidth
            variant="standard"
            onChange={(e) => setTempAppSecret(e.target.value)}
            value={tempAppSecret}
          />
          <FormGroup>
            <FormControlLabel
              control={
                <Switch
                  checked={showFunctionDetail}
                  onChange={(event) => {
                    const value = event.target.checked;
                    localStorage.setItem(
                      "showFunctionDetail",
                      value.toString(),
                    );
                    setShowFunctionDetail(value);
                  }}
                />
              }
              label="Show function detail"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={saveHistory}
                  onChange={(event) => {
                    const value = event.target.checked;
                    localStorage.setItem("saveHistory", value.toString());
                    setSaveHistory(value);
                  }}
                />
              }
              label="Save history"
            />
          </FormGroup>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setTempBackend(backend?.origin || "");
              setTempAppSecret(appSecret);
              setSettingsOpen(false);
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSettingsConfirm}
            disabled={!checkURL(tempBackend)}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={tokenOpen}
        onClose={() => setTokenOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Secret Token</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Secret Token"
            onChange={(e) => setTempSecret(e.target.value)}
            value={tempSecret}
            fullWidth
            variant="standard"
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setTempSecret(selectedFunctionSecret || "");
              setTokenOpen(false);
            }}
          >
            Cancel
          </Button>
          <Button onClick={handleTokenConfirm}>Confirm</Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={shareOpen}
        onClose={() => setShareOpen(false)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>Share</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="URL"
            fullWidth
            variant="outlined"
            value={tempShareUrl}
            onChange={(e) => setTempShareUrl(e.target.value)}
            error={!checkURL(tempShareUrl)}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    edge="end"
                    onClick={() => copyToClipboard(tempShareUrl, "Copied URL")}
                  >
                    <ContentCopy />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <Button
            color="primary"
            startIcon={<Code />}
            onClick={() => {
              copyToClipboard(
                `<iframe src="${tempShareUrl}" width="100%" height="100%" style="border: none"></iframe>`,
                "Copied iframe",
              );
            }}
          >
            Copy Iframe
          </Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShareOpen(false)}>Close</Button>
          <Button onClick={handleShareConfirm}>Confirm</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default AppBarActions;
