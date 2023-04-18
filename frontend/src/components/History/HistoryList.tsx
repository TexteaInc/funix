import useFunixHistory from "../../shared/useFunixHistory";
import { useAtom } from "jotai";
import { storeAtom } from "../../store";
import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import { Sick } from "@mui/icons-material";
import { getHistoryInfo, getHistoryStatusIcon } from "./HistoryUtils";
import { useEffect, useState } from "react";

const HistoryList = () => {
  const { getHistories } = useFunixHistory();
  const [{ selectedFunction }, setStore] = useAtom(storeAtom);
  const [selectedIndex, setSelectedIndex] = useState(-1);

  useEffect(() => {
    setSelectedIndex(-1);
  }, [selectedFunction]);

  const histories = getHistories();

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
    (history) => history.functionName === selectedFunction.name
  );

  return (
    <List>
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
            <ListItemButton
              key={index}
              onClick={() => {
                setSelectedIndex(index);
                setStore((store) => ({
                  ...store,
                  backHistory: history,
                }));
              }}
              selected={selectedIndex === index}
            >
              <ListItemIcon>{getHistoryStatusIcon(status)}</ListItemIcon>
              <ListItemText
                primary={history.name || "Untitled"}
                secondary={new Date(history.timestamp).toLocaleString()}
              />
            </ListItemButton>
          );
        })
      )}
    </List>
  );
};

export default HistoryList;
