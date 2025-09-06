import React, { useCallback, useEffect, useState, useRef } from "react";
import { Box, IconButton, Typography, useTheme } from "@mui/material";
import {
  MoreHoriz,
  Functions,
  Folder,
  ChevronRight,
  KeyboardArrowDown,
} from "@mui/icons-material";
import AppBarActions from "../AppBarActions";
import { useAtom } from "jotai";
import { FunctionPreview, getList } from "../../shared";
import { useNavigate, useLocation } from "react-router-dom";
import {
  backConsensusAtom,
  backHistoryAtom,
  callableDefaultAtom,
  functionsAtom,
  functionSecretAtom,
  selectedFunctionAtom,
} from "../../store";

export type FunixTabBarProps = {
  backend: URL;
  onHistoryOpen?: () => void;
  onHistorySideBarToggle?: () => void;
  sideBarOpen?: boolean;
  onSideBarToggle?: () => void;
  functions?: string[] | null;
};

interface TreeNode {
  [key: string]: TreeNode | string[];
}

interface TabGroup {
  id: string;
  name: string;
  functions: FunctionPreview[];
  expanded: boolean;
  color?: string;
}

const addFileToTree = (tree: TreeNode, parts: string[]) => {
  let currentNode = tree;

  for (const part of parts) {
    if (!currentNode[part]) {
      currentNode[part] = {};
    }
    currentNode = currentNode[part] as TreeNode;
  }
};

const treeToList = (tree: TreeNode): any[] => {
  const list: any[] = [];

  for (const key in tree) {
    if (Array.isArray(tree[key])) {
      const asList = tree[key] as string[];
      list.push(...asList);
    } else {
      const nestedList = treeToList(tree[key] as TreeNode);
      if (nestedList.length > 0) {
        list.push({ [key]: nestedList });
      } else {
        list.push(key);
      }
    }
  }

  return list;
};

const treeToTabGroups = (
  treeList: any[],
  functions: FunctionPreview[],
): TabGroup[] => {
  const groups: TabGroup[] = [];

  const processNode = (node: any, path: string[] = []): void => {
    if (typeof node === "string") {
      return;
    }

    const [k, v] = Object.entries(node)[0];
    if (k === "") {
      return;
    }

    if (Array.isArray(v) && v.every((element) => typeof element === "string")) {
      const groupFunctions = v
        .map((id) => {
          const [_, functionPath] = id.split("#");
          return functions.find((f) => f.path === functionPath)!;
        })
        .filter(Boolean);

      if (groupFunctions.length > 0) {
        groups.push({
          id: [...path, k].join("."),
          name: k,
          functions: groupFunctions,
          expanded: false,
        });
      }
    } else if (Array.isArray(v)) {
      v.forEach((element) => processNode(element, [...path, k]));
    }
  };

  treeList.forEach((element) => processNode(element));
  return groups;
};

const FunixTabBar: React.FC<FunixTabBarProps> = ({
  backend,
  onHistoryOpen,
  onHistorySideBarToggle,
}) => {
  const [, setSelectedFunction] = useAtom(selectedFunctionAtom);
  const [, setFunctions] = useAtom(functionsAtom);
  const [backHistory, setBackHistory] = useAtom(backHistoryAtom);
  const [backConsensus, setBackConsensus] = useAtom(backConsensusAtom);
  const [callableDefault, setCallableDefault] = useAtom(callableDefaultAtom);
  const [functionSecret, setFunctionSecret] = useAtom(functionSecretAtom);

  const [state, setState] = useState<FunctionPreview[]>([]);
  const [selectedTab, setSelectedTab] = useState<string | null>(null);
  const [url, setURL] = useState("");
  const [tabGroups, setTabGroups] = useState<TabGroup[]>([]);

  const { pathname, search } = useLocation();
  const navigate = useNavigate();
  const theme = useTheme();

  const lastProcessedHistoryRef = useRef<number>(-1);

  const renderThemeIcon = () => {
    const themeAny = theme as any;
    const iconUrl = themeAny.funix_icon;

    if (!iconUrl) {
      return null;
    }

    const iconHeight = themeAny.funix_icon_height || "32px";
    const iconWidth = themeAny.funix_icon_width || "32px";

    return (
      <img
        src={iconUrl}
        alt="Funix Theme Icon"
        style={{
          height: iconHeight,
          width: iconWidth,
          marginRight: 16,
          objectFit: "contain",
          flexShrink: 0,
        }}
      />
    );
  };

  const handleFetchFunctionDetail = useCallback(
    (functionPreview: FunctionPreview) => {
      setSelectedFunction(functionPreview);
    },
    [setSelectedFunction],
  );

  const handleTabClick = (functionPath: string) => {
    setSelectedTab(functionPath);
    const selectedFunctionPreview = state.find((f) => f.path === functionPath);
    if (selectedFunctionPreview) {
      navigate(`/${functionPath}`);
      handleFetchFunctionDetail(selectedFunctionPreview);
    }
  };

  const toggleTabGroup = (groupId: string) => {
    setTabGroups((groups) =>
      groups.map((group) =>
        group.id === groupId ? { ...group, expanded: !group.expanded } : group,
      ),
    );
  };

  useEffect(() => {
    if (backend.origin === url) return;
    setSelectedFunction(null);
    async function queryData() {
      const { list, default_function } = await getList(
        new URL("/list", backend),
      );
      setState(list);
      setFunctions(list.map((f) => f.name));

      if (list.some((f) => typeof f.module === "string")) {
        const hasMultipleModules = !list.every(
          (f) => f.module === list[0].module,
        );

        if (hasMultipleModules) {
          const fileTree: TreeNode = {};
          list.forEach((preview) => {
            const path = preview.module ?? "";
            const pathList = path.split(".");
            pathList.push(
              `${preview.name}#${preview.path}#${preview.class}#${preview.order}`,
            );
            addFileToTree(fileTree, pathList);
          });

          const treeList = treeToList(fileTree);
          const groups = treeToTabGroups(treeList, list);
          setTabGroups(groups);
        }
      }

      if (list.length === 1) {
        handleFetchFunctionDetail(list[0]);
        setSelectedTab(list[0].path);
      } else {
        if (default_function !== null) {
          const preview = list.filter(
            (preview) => preview.id === default_function,
          );
          if (preview.length === 1) {
            handleFetchFunctionDetail(preview[0]);
            setSelectedTab(preview[0].path);
          }
        } else if (list.length >= 1) {
          const preview = list[0];
          handleFetchFunctionDetail(preview);
          setSelectedTab(preview.path);
        }
      }
    }
    queryData().then();
    setURL(backend.origin);
  }, [backend, url]);

  useEffect(() => {
    if (backHistory === null || backHistory === undefined) {
      lastProcessedHistoryRef.current = -1;
      return;
    }
    if (lastProcessedHistoryRef.current === backHistory.timestamp) return;
    lastProcessedHistoryRef.current = backHistory.timestamp;
    handleTabClick(backHistory.functionPath);
    if (!backConsensus[0]) {
      const newBackConsensus = [...backConsensus];
      newBackConsensus[0] = true;
      setBackConsensus(newBackConsensus);
    }
  }, [backHistory]);

  useEffect(() => {
    if (backConsensus.every((v) => v)) {
      setBackConsensus([false, false, false]);
      setBackHistory(null);
    }
  }, [backConsensus]);

  useEffect(() => {
    const pathParam = pathname.substring(1);
    if (pathParam !== selectedTab) {
      const functionPath = decodeURIComponent(pathParam).split("?")[0];
      const selectedFunctionPreview = state.find(
        (f) => f.path === functionPath,
      );
      if (selectedFunctionPreview) {
        const searchParams = new URLSearchParams(search);
        const args = searchParams.get("args");
        if (args !== null) {
          const newCallableDefault = { ...callableDefault };
          newCallableDefault[selectedFunctionPreview.path] = JSON.parse(
            atob(args.replace(/_/g, "/").replace(/-/g, "+")),
          );
          setCallableDefault(newCallableDefault);
          setSelectedFunction(selectedFunctionPreview);
        } else {
          setSelectedFunction(selectedFunctionPreview);
        }
        setSelectedTab(functionPath);
      }
    }
  }, [pathname, state]);

  useEffect(() => {
    if (search === "" || typeof selectedTab !== "string") return;
    const searchParams = new URLSearchParams(search);
    const secret = searchParams.get("secret");
    if (secret !== null) {
      const newFunctionSecret = {
        ...functionSecret,
        [selectedTab]: secret,
      };
      setFunctionSecret(newFunctionSecret);
      navigate(`/${selectedTab}`);
    }
  }, [search, selectedTab]);

  return (
    <Box
      id="funix-tab-bar"
      sx={{
        backgroundColor: "background.paper",
        boxShadow:
          "0px 2px 4px -1px rgba(25,118,210,0.2),0px 4px 5px 0px rgba(25,118,210,0.14),0px 1px 10px 0px rgba(25,118,210,0.12)",
        borderBottom: 1,
        borderColor: "divider",
        minHeight: 64,
      }}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          minHeight: 64,
          px: 2,
        }}
      >
        {renderThemeIcon()}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            flexGrow: 1,
            overflow: "auto",
            py: 1,
          }}
        >
          {tabGroups.flatMap((group) => {
            const isGroupSelected = group.functions.some(
              (func) => func.path === selectedTab,
            );

            const groupButton = (
              <Box
                key={group.id}
                onClick={() => toggleTabGroup(group.id)}
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 0.5,
                  px: 2,
                  py: 1,
                  borderRadius: 1,
                  cursor: "pointer",
                  backgroundColor: isGroupSelected
                    ? "primary.main"
                    : "grey.100",
                  color: isGroupSelected
                    ? "primary.contrastText"
                    : "text.primary",
                  border: 1,
                  borderColor: isGroupSelected ? "primary.main" : "grey.300",
                  "&:hover": {
                    backgroundColor: isGroupSelected
                      ? "primary.dark"
                      : "grey.200",
                  },
                }}
              >
                <Folder fontSize="small" />
                <Typography variant="body2" component="span">
                  {group.name}
                </Typography>
                {group.expanded ? (
                  <KeyboardArrowDown fontSize="small" />
                ) : (
                  <ChevronRight fontSize="small" />
                )}
              </Box>
            );

            const expandedFunctions = group.expanded
              ? group.functions.map((func) => (
                  <Box
                    key={func.path}
                    onClick={() => handleTabClick(func.path)}
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 0.5,
                      px: 2,
                      py: 1,
                      borderRadius: 1,
                      cursor: "pointer",
                      backgroundColor:
                        selectedTab === func.path ? "primary.main" : "grey.100",
                      color:
                        selectedTab === func.path
                          ? "primary.contrastText"
                          : "text.primary",
                      border: 1,
                      borderColor:
                        selectedTab === func.path ? "primary.main" : "grey.300",
                      borderLeft: 3,
                      borderLeftColor: "primary.main",
                      "&:hover": {
                        backgroundColor:
                          selectedTab === func.path
                            ? "primary.dark"
                            : "grey.200",
                      },
                    }}
                  >
                    <Functions fontSize="small" />
                    <Typography variant="body2" component="span">
                      {func.name}
                    </Typography>
                  </Box>
                ))
              : [];

            return [groupButton, ...expandedFunctions];
          })}
          {state
            .filter(
              (func) =>
                !tabGroups.some((group) =>
                  group.functions.some(
                    (groupFunc) => groupFunc.path === func.path,
                  ),
                ),
            )
            .map((func) => (
              <Box
                key={func.path}
                onClick={() => handleTabClick(func.path)}
                sx={{
                  display: "flex",
                  alignItems: "center",
                  gap: 0.5,
                  px: 2,
                  py: 1,
                  borderRadius: 1,
                  cursor: "pointer",
                  backgroundColor:
                    selectedTab === func.path ? "primary.main" : "grey.100",
                  color:
                    selectedTab === func.path
                      ? "primary.contrastText"
                      : "text.primary",
                  border: 1,
                  borderColor:
                    selectedTab === func.path ? "primary.main" : "grey.300",
                  "&:hover": {
                    backgroundColor:
                      selectedTab === func.path ? "primary.dark" : "grey.200",
                  },
                }}
              >
                <Functions fontSize="small" />
                <Typography variant="body2" component="span">
                  {func.name}
                </Typography>
              </Box>
            ))}

          {state.length === 0 && (
            <Typography variant="body2" color="text.secondary">
              No functions available
            </Typography>
          )}
        </Box>
        <AppBarActions
          isTabBarMode={true}
          backend={backend}
          onHistoryOpen={onHistoryOpen}
          onHistorySideBarToggle={onHistorySideBarToggle}
          trigger={
            <IconButton sx={{ ml: 1 }}>
              <MoreHoriz />
            </IconButton>
          }
        />
      </Box>
    </Box>
  );
};

export default React.memo(FunixTabBar);
