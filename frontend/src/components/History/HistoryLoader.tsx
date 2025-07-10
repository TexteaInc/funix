import { useAtom } from "jotai";
import useFunixHistory from "../../shared/useFunixHistory";
import { useEffect, useRef } from "react";
import { historiesAtom } from "../../store";

const HistoryLoader = (props: { children: React.ReactNode }) => {
  const [, setHistories] = useAtom(historiesAtom);
  const { getHistories } = useFunixHistory();
  const historyLoaded = useRef<boolean>(false);

  useEffect(() => {
    if (historyLoaded.current) {
      return;
    }
    historyLoaded.current = true;
    getHistories().then((histories) => {
      setHistories(histories);
    });
  }, [getHistories, setHistories]);

  useEffect(() => {
    const handleHistoryUpdate = () => {
      getHistories().then((histories) => {
        setHistories(histories);
      });
    };

    window.addEventListener("funix-history-update", handleHistoryUpdate);

    return () => {
      window.removeEventListener("funix-history-update", handleHistoryUpdate);
    };
  }, [getHistories, setHistories]);

  return <>{props.children}</>;
};

export default HistoryLoader;
