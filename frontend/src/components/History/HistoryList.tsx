import useFunixHistory, { History } from "../../shared/useFunixHistory";
import { useAtom } from "jotai";
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
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { exportHistory } from "../../shared";
import {
  backHistoryAtom,
  historiesAtom,
  selectedFunctionAtom,
} from "../../store";

const HistoryList = React.memo((props: { isOpen: boolean }) => {
  const { setHistoryNameAndPath, removeHistory } = useFunixHistory();
  const [selectedFunction] = useAtom(selectedFunctionAtom);
  const [histories] = useAtom(historiesAtom);
  const [, setBackHistory] = useAtom(backHistoryAtom);
  const [selectedHistoryTimestamp, setSelectedHistoryTimestamp] = useState(-1);
  const [selectedHistory, setSelectedHistory] = useState<null | History>(null);
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const [tempRename, setTempRename] = useState("");
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  useEffect(() => {
    setSelectedHistoryTimestamp(-1);
  }, [selectedFunction]);

  const filteredHistories = useMemo(() => {
    if (selectedFunction === null) return [];
    return histories.filter(
      (history) =>
        history.functionName === selectedFunction.name &&
        history.functionPath === selectedFunction.path,
    );
  }, [histories, selectedFunction]);

  const handleRenameDialogClose = useCallback(() => {
    setRenameDialogOpen(false);
    setSelectedHistory(null);
    setTempRename("");
  }, []);

  const handleMenuClose = useCallback(() => {
    setAnchorEl(null);
  }, []);

  const handleRename = useCallback(() => {
    if (selectedHistory !== null) {
      setTempRename(selectedHistory.name || "");
    }
    setRenameDialogOpen(true);
    setAnchorEl(null);
  }, [selectedHistory]);

  const handleDelete = useCallback(() => {
    if (selectedHistory !== null) {
      removeHistory(selectedHistory.timestamp);
    }
    setSelectedHistory(null);
    setAnchorEl(null);
  }, [selectedHistory, removeHistory]);

  const handleExport = useCallback(() => {
    if (selectedHistory !== null) {
      exportHistory(selectedHistory);
    }
    setSelectedHistory(null);
    setAnchorEl(null);
  }, [selectedHistory]);

  const handleRenameConfirm = useCallback(() => {
    if (selectedHistory !== null) {
      setHistoryNameAndPath(
        selectedHistory.timestamp,
        tempRename,
        selectedHistory.functionPath,
      );
    }
    handleRenameDialogClose();
  }, [
    selectedHistory,
    tempRename,
    setHistoryNameAndPath,
    handleRenameDialogClose,
  ]);

  const handleTempRenameChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setTempRename(event.target.value);
    },
    [],
  );

  const handleHistoryClick = useCallback(
    (history: History) => {
      setSelectedHistoryTimestamp(history.timestamp);
      setBackHistory(history);
    },
    [setBackHistory],
  );

  const handleMoreClick = useCallback(
    (event: React.MouseEvent<HTMLElement>, history: History) => {
      setSelectedHistory(history);
      setAnchorEl(event.currentTarget);
    },
    [],
  );

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

  return (
    <>
      <Dialog open={renameDialogOpen} onClose={handleRenameDialogClose}>
        <DialogTitle>Rename History</DialogTitle>
        <DialogContent>
          <TextField
            value={tempRename}
            onChange={handleTempRenameChange}
            fullWidth
            label="Name"
            variant="standard"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleRenameDialogClose}>Cancel</Button>
          <Button onClick={handleRenameConfirm}>Rename</Button>
        </DialogActions>
      </Dialog>
      <Menu open={open} anchorEl={anchorEl} onClose={handleMenuClose}>
        <MenuItem onClick={handleRename}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText>Rename</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleDelete}>
          <ListItemIcon>
            <Delete fontSize="small" />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleExport}>
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
                key={`${history.timestamp}-${index}`}
                sx={{
                  flexDirection: "column",
                  justifyContent: "flex-start",
                  width: "100%",
                  padding: 0,
                  alignItems: "flex-start",
                }}
                secondaryAction={
                  <IconButton
                    onClick={(event) => handleMoreClick(event, history)}
                  >
                    <MoreVert />
                  </IconButton>
                }
              >
                <ListItemButton
                  onClick={() => handleHistoryClick(history)}
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
});

HistoryList.displayName = "HistoryList";

export default HistoryList;
