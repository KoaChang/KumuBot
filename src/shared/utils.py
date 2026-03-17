import os
import re
from typing import Union, List, Any, Dict, Tuple
from openai import OpenAI
from datetime import datetime
import pytz

# ---------------------------
# OpenAI Client Setup
# ---------------------------
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------
# HTML sanitizing helper
# ---------------------------
HTML_TAG_RE = re.compile(r"<[^>]+>")

def _strip_html_if_needed(txt: str) -> str:
    """Strip HTML tags if they exist in the text, otherwise return as-is"""
    if "<" in txt and ">" in txt:
        return HTML_TAG_RE.sub("", txt)
    return txt

# ---------------------------
# API Usage Logger
# ---------------------------
def log_api_usage(endpoint_name, prompt, completion, total):
    """Log API usage with HST timestamp and token counts"""
    # Get the absolute path to the calling script's directory
    import inspect
    caller_frame = inspect.stack()[1]
    caller_dir = os.path.dirname(os.path.realpath(caller_frame.filename))
    
    # Create a directory for the logs if it doesn't exist
    logs_dir = os.path.join(caller_dir, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Open the log file for the endpoint
    log_file = os.path.join(logs_dir, f"{endpoint_name}.txt")
    with open(log_file, "a") as f:
        # Get current time in UTC
        now_utc = datetime.now(pytz.timezone("UTC"))
        # Convert to HST
        now_hst = now_utc.astimezone(pytz.timezone("Pacific/Honolulu"))
        # Format the datetime
        formatted_time = now_hst.strftime("%m/%d/%Y %I:%M %p")
        # Write the current time and the number of tokens used to the log file
        if endpoint_name == "art":
            f.write(
                f"{formatted_time}. Prompt: {prompt}. Completion: {completion}. Total: {total}. Image Cost: 0.04\n"
            )
        else:
            f.write(
                f"{formatted_time}. Prompt: {prompt}. Completion: {completion}. Total: {total}.\n"
            )

# ---------------------------
# Responses API helpers
# ---------------------------
def _as_parts_for_role(content: Union[str, List[Any], Dict[str, Any]], role: str) -> List[Dict[str, Any]]:
    """
    Convert chat-style content to Responses API content parts, respecting role:
      - user: {"type": "input_text"} / {"type": "input_image"}
      - assistant: {"type": "output_text"}  (assistant images are ignored)
    Also sanitizes any HTML-like strings.
    """
    parts: List[Dict[str, Any]] = []

    def push_user_text(txt: str):
        if txt is None:
            return
        parts.append({"type": "input_text", "text": _strip_html_if_needed(str(txt))})

    def push_user_image(url: str):
        if url is None:
            return
        parts.append({"type": "input_image", "image_url": url})

    def push_assistant_text(txt: str):
        if txt is None:
            return
        # Assistant history must be output_* types
        parts.append({"type": "output_text", "text": _strip_html_if_needed(str(txt))})

    if role == "assistant":
        # We only push output_text for assistant history
        if isinstance(content, str):
            push_assistant_text(content)
            return parts
        if isinstance(content, dict):
            # Try common shapes; coerce to text
            if "text" in content and isinstance(content["text"], str):
                push_assistant_text(content["text"])
                return parts
            if "content" in content and isinstance(content["content"], str):
                push_assistant_text(content["content"])
                return parts
            # Fallback: stringify
            push_assistant_text(str(content))
            return parts
        if isinstance(content, list):
            # If an array slipped in, concatenate textual parts
            buf: List[str] = []
            for item in content:
                if isinstance(item, str):
                    buf.append(item)
                elif isinstance(item, dict):
                    t = item.get("type")
                    if t in ("text", "input_text", "output_text") and isinstance(item.get("text"), str):
                        buf.append(item["text"])
                    elif "text" in item and isinstance(item["text"], str):
                        buf.append(item["text"])
            push_assistant_text("\n".join(buf) if buf else "")
            return parts
        # Default
        push_assistant_text(str(content))
        return parts

    # role != assistant -> treat as user input
    if isinstance(content, str):
        push_user_text(content)
        return parts

    if isinstance(content, dict):
        t = content.get("type")
        if t in ("input_text", "text"):
            push_user_text(content.get("text") or content.get("content"))
            return parts
        if t in ("input_image", "image", "image_url"):
            image_url = None
            if isinstance(content.get("image_url"), dict):
                image_url = content["image_url"].get("url")
            elif isinstance(content.get("image_url"), str):
                image_url = content["image_url"]
            else:
                image_url = content.get("url")
            push_user_image(image_url)
            return parts

        if "content" in content and isinstance(content["content"], str):
            push_user_text(content["content"])
            return parts
        if "url" in content and isinstance(content["url"], str):
            push_user_image(content["url"])
            return parts

    if isinstance(content, list):
        for item in content:
            parts.extend(_as_parts_for_role(item, role))
        return parts

    push_user_text(str(content))
    return parts

def _messages_to_responses_input(messages: List[Dict[str, Any]]) -> Tuple[Union[str, None], List[Dict[str, Any]]]:
    """
    Pull out a single system prompt into `instructions` and convert the rest
    to Responses API input format with role-aware parts.
    """
    instructions = None
    converted: List[Dict[str, Any]] = []

    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")

        if role == "system" and instructions is None:
            if isinstance(content, str):
                instructions = content
            elif isinstance(content, dict) and isinstance(content.get("content"), str):
                instructions = content["content"]
            else:
                instructions = str(content)
            continue

        converted.append({
            "role": role,
            "content": _as_parts_for_role(content, role)
        })

    return (instructions or None, converted)

def _extract_text_and_usage(resp) -> Tuple[str, int, int, int]:
    """
    Extract the unified text output and usage safely.
    """
    text = getattr(resp, "output_text", None)
    u = getattr(resp, "usage", None)

    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    if u is not None:
        input_tokens = getattr(u, "input_tokens", None) or getattr(u, "prompt_tokens", 0) or 0
        output_tokens = getattr(u, "output_tokens", None) or getattr(u, "completion_tokens", 0) or 0
        total_tokens = getattr(u, "total_tokens", None) or (input_tokens + output_tokens)

    return (text or "", input_tokens, output_tokens, total_tokens)

# ---------------------------
# Model wrappers (gpt-5-mini)
# ---------------------------
def get_completionOpen(prompt: str, model: str = "gpt-5-mini"):
    """Simple text prompt -> text response."""
    resp = openai_client.responses.create(
        model=model,
        reasoning={"effort": "low"},  # Limit reasoning effort
        input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
    )
    return resp

def get_completion_from_messagesOpen(messages: List[Dict[str, Any]], model: str = "gpt-5-mini"):
    """Full chat history -> text response."""
    instructions, input_msgs = _messages_to_responses_input(messages)

    resp = openai_client.responses.create(
        model=model,
        reasoning={"effort": "low"},  # Limit reasoning effort
        instructions=instructions,
        input=input_msgs,
    )
    return resp

# ---------------------------
# History trimming helper
# ---------------------------
def _last_five_pairs(message_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enforce sending only the last 5 user–assistant pairs.
    Returns up to 10 messages (5 pairs) in chronological order.
    """
    out = []
    i = len(message_history) - 1
    # Ensure we end on assistant before pairing
    if i >= 0 and message_history[i].get("role") == "user":
        i -= 1
    pairs = []
    while i >= 1 and len(pairs) < 5:
        a = message_history[i]
        u = message_history[i - 1]
        if a.get("role") == "assistant" and u.get("role") == "user":
            pairs.append((u, a))
            i -= 2
        else:
            i -= 1
    for u, a in reversed(pairs):
        out.extend([u, a])
    return out
