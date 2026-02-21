"""
Regression tests for websocket print_to_web reliability.
"""

import json
import sys
import time
from unittest import TestCase, main

from funix.app import app
from funix.app.websocket import StdoutToWebsocket
from funix.decorator.call import funix_call


STEP3_TIME_LINE = "[Step 3] Generating answer with LLM... Time: 88.84s"
LARGE_MARKDOWN_TOKEN = "FUNIX_LARGE_MARKDOWN_TOKEN"
LARGE_MARKDOWN = f"## {LARGE_MARKDOWN_TOKEN}\n\n" + ("A" * 250_000)


class LossyOnImmediateCloseWebSocket:
    """
    Test double that emulates a transport/proxy dropping trailing large frames
    when the socket is closed immediately after send.
    """

    def __init__(self, args: str = "{}", drop_threshold_ms: float = 20.0):
        self._args = args
        self.drop_threshold_ms = drop_threshold_ms
        self.messages: list[str] = []
        self._last_send_monotonic = 0.0

    def receive(self):
        return self._args

    def send(self, data):
        self.messages.append(data)
        self._last_send_monotonic = time.monotonic()

    def close(self):
        elapsed_ms = (time.monotonic() - self._last_send_monotonic) * 1000
        if elapsed_ms >= self.drop_threshold_ms:
            return
        # Emulate that trailing large payload frames are lost on abrupt close.
        while self.messages:
            tail = self.messages[-1]
            if LARGE_MARKDOWN_TOKEN in tail or len(tail) > 50_000:
                self.messages.pop()
                continue
            break


def long_step_three_function() -> str:
    print("[Step 1] Rewriting query (attempt 1)...")
    print("[Step 2] Fetching matching records from Goodmem... Retrieved 90 records Time: 2.16s")
    print(STEP3_TIME_LINE)
    return LARGE_MARKDOWN


def legacy_output_to_web(function, ws) -> None:
    """
    Legacy behavior model: immediate close after final print frame.
    """
    org_stdout = sys.stdout
    try:
        sys.stdout = StdoutToWebsocket(ws)
        function_result = function()
        if function_result:
            print(function_result)
        sys.stdout = org_stdout
    finally:
        sys.stdout = org_stdout
        ws.close()


class TestPrintToWebWebsocketReliability(TestCase):
    def _collected_stream_text(self, messages: list[str]) -> str:
        chunks: list[str] = []
        for raw in messages:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                chunks.extend(str(item) for item in parsed)
        return "\n".join(chunks)

    def test_legacy_immediate_close_can_drop_large_final_markdown(self):
        ws = LossyOnImmediateCloseWebSocket()
        legacy_output_to_web(long_step_three_function, ws)
        text = self._collected_stream_text(ws.messages)

        self.assertIn(STEP3_TIME_LINE, text)
        self.assertNotIn(LARGE_MARKDOWN_TOKEN, text)

    def test_funix_call_preserves_large_final_markdown_with_drain(self):
        ws = LossyOnImmediateCloseWebSocket()
        with app.test_request_context("/call/test-id", method="POST"):
            result = funix_call(
                app_name="test_app",
                limiters=[],
                need_websocket=True,
                use_pandas=False,
                pandas_module=None,
                function_id="test-id",
                function=long_step_three_function,
                return_type_parsed="Markdown",
                cast_to_list_flag=False,
                json_schema_props={},
                print_to_web=True,
                secret_key=False,
                matplotlib_format="png",
                ws=ws,
                next_to=None,
            )

        self.assertIsNone(result)
        text = self._collected_stream_text(ws.messages)
        self.assertIn(STEP3_TIME_LINE, text)
        self.assertIn(LARGE_MARKDOWN_TOKEN, text)
        self.assertTrue(
            any(
                isinstance(json.loads(raw), dict)
                and json.loads(raw).get("__funix_event") == "done"
                for raw in ws.messages
            )
        )


if __name__ == "__main__":
    main(verbosity=2)
