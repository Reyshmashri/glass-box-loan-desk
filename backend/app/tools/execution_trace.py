
import time
from copy import deepcopy


def run_with_trace(agent_name, tool_name, tool_function, **inputs):
    """Run a tool and record its actual input, output, and duration."""

    start_time = time.perf_counter()

    trace = {
        "agent": agent_name,
        "tool": tool_name,
        "input": deepcopy(inputs),
    }

    try:
        output = tool_function(**inputs)

        trace["status"] = "success"
        trace["output"] = deepcopy(output)

        return output, trace

    except Exception as exc:
        trace["status"] = "error"
        trace["error"] = str(exc)
        raise

    finally:
        trace["duration_ms"] = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )
