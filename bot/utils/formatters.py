def escape_md(text: str) -> str:
    """Escape special characters for MarkdownV2."""
    chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for c in chars:
        text = text.replace(c, f'\\{c}')
    return text


def truncate(text: str, max_len: int = 4000) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 50] + "\n\n... _(truncated)_"


def format_code_result(code: str, result: str) -> str:
    code_preview = code[:800] + "..." if len(code) > 800 else code
    result_preview = result[:1500] + "..." if len(result) > 1500 else result
    return f"""💻 **Code Generated & Executed**

```python
{code_preview}
```

📤 **Output:**
```
{result_preview}
```"""


def format_task_history(tasks: list) -> str:
    if not tasks:
        return "📋 No task history yet."
    lines = ["📋 **Recent Tasks:**\n"]
    for task_type, desc, status, created in tasks:
        emoji = "✅" if status == "completed" else "❌"
        lines.append(f"{emoji} [{task_type}] {desc[:50]}...")
        lines.append(f"   _{created[:16]}_\n")
    return "\n".join(lines)


def format_automations(automations: list) -> str:
    if not automations:
        return "⚙️ No automations configured."
    lines = ["⚙️ **Your Automations:**\n"]
    for auto_id, name, task, schedule, active in automations:
        status = "🟢" if active else "🔴"
        lines.append(f"{status} **{name}**")
        lines.append(f"   📅 {schedule}")
        lines.append(f"   📝 {task[:60]}...\n")
    return "\n".join(lines)
