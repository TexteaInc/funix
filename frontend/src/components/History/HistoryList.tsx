import useFunixHistory, { History } from "../../shared/useFunixHistory";
import { useAtom } from "jotai";
import { storeAtom } from "../../store";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  TextField,
} from "@mui/material";
import {
  Delete,
  Edit,
  FileDownload,
  MoreVert,
  Sick,
} from "@mui/icons-material";
import { getHistoryInfo, getHistoryStatusIcon } from "./HistoryUtils";
import React, { useEffect, useState } from "react";
import { exportHistory } from "../../shared";

const HistoryList = (props: { isOpen: boolean }) => {
  const { setHistoryNameAndPath, removeHistory } = useFunixHistory();
  const [{ selectedFunction, histories }, setStore] = useAtom(storeAtom);
  const [selectedHistoryTimestamp, setSelectedHistoryTimestamp] = useState(-1);
  const [selectedHistory, setSelectedHistory] = useState<null | History>(null);
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const [tempRename, setTempRename] = useState("");
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  useEffect(() => {
    setSelectedHistoryTimestamp(-1);
  }, [selectedFunction]);

  if (!props.isOpen) {
    return <></>;
  }

  if (selectedFunction === null || histories.length === 0) {
    return (
      <List component="nav">
        <ListItem>
          <ListItemIcon>
            <Sick />
          </ListItemIcon>
          <ListItemText
            primary={
              selectedFunction === null
                ? "Select a function to see history"
                : "No history"
            }
          />
        </ListItem>
      </List>
    );
  }

  const filteredHistories = histories.filter(
    (history) =>
      history.functionName === selectedFunction.name &&
      history.functionPath === selectedFunction.path,
  );

  const handleRenameDialogClose = () => {
    setRenameDialogOpen(false);
    setSelectedHistory(null);
    setTempRename("");
  };

  return (
    <>
      <Dialog open={renameDialogOpen} onClose={handleRenameDialogClose}>
        <DialogTitle>Rename History</DialogTitle>
        <DialogContent>
          <TextField
            value={tempRename}
            onChange={(event) => setTempRename(event.target.value)}
            fullWidth
            label="Name"
            variant="standard"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleRenameDialogClose}>Cancel</Button>
          <Button
            onClick={() => {
              if (selectedHistory !== null) {
                setHistoryNameAndPath(
                  selectedHistory.timestamp,
                  tempRename,
                  selectedHistory.functionPath,
                );
              }
              handleRenameDialogClose();
            }}
          >
            Rename
          </Button>
        </DialogActions>
      </Dialog>
      <Menu open={open} anchorEl={anchorEl} onClose={() => setAnchorEl(null)}>
        <MenuItem
          onClick={() => {
            if (selectedHistory !== null) {
              setTempRename(selectedHistory.name || "");
            }
            setRenameDialogOpen(true);
            setAnchorEl(null);
          }}
        >
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText>Rename</ListItemText>
        </MenuItem>
        <MenuItem
          onClick={() => {
            if (selectedHistory !== null) {
              removeHistory(selectedHistory.timestamp);
            }
            setSelectedHistory(null);
            setAnchorEl(null);
          }}
        >
          <ListItemIcon>
            <Delete fontSize="small" />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem
          onClick={() => {
            if (selectedHistory !== null) {
              exportHistory(selectedHistory);
            }
            setSelectedHistory(null);
            setAnchorEl(null);
          }}
        >
          <ListItemIcon>
            <FileDownload fontSize="small" />
          </ListItemIcon>
          <ListItemText>Export</ListItemText>
        </MenuItem>
      </Menu>
      <List component="div">
        {filteredHistories.length === 0 ? (
          <List component="nav">
            <ListItem>
              <ListItemIcon>
                <Sick />
              </ListItemIcon>
              <ListItemText primary="No history for this function" />
            </ListItem>
          </List>
        ) : (
          filteredHistories.map((history, index) => {
            const { status } = getHistoryInfo(history);
            return (
              <ListItem
                key={index}
                sx={{
                  flexDirection: "column",
                  justifyContent: "flex-start",
                  width: "100%",
                  padding: 0,
                  alignItems: "flex-start",
                }}
                secondaryAction={
                  <IconButton
                    onClick={(event) => {
                      setSelectedHistory(history);
                      setAnchorEl(event.currentTarget);
                    }}
                  >
                    <MoreVert />
                  </IconButton>
                }
              >
                <ListItemButton
                  onClick={() => {
                    setSelectedHistoryTimestamp(history.timestamp);
                    setStore((store) => ({
                      ...store,
                      backHistory: history,
                    }));
                  }}
                  selected={selectedHistoryTimestamp === history.timestamp}
                  sx={{
                    width: "100%",
                  }}
                >
                  <ListItemIcon>{getHistoryStatusIcon(status)}</ListItemIcon>
                  {history.name !== null ? (
                    <ListItemText
                      primary={history.name}
                      secondary={new Date(history.timestamp).toLocaleString()}
                    />
                  ) : (
                    <ListItemText
                      primary={new Date(history.timestamp).toLocaleString()}
                    />
                  )}
                </ListItemButton>
              </ListItem>
            );
          })
        )}
      </List>
    </>
  );
};

export default HistoryList;
