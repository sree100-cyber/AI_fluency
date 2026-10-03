# Day 3 Lab Report: Build a ReAct Agent from Scratch, Break It on Purpose, Then Fix It

**Unit:** Unit 1: Foundations of AI Agents (Sub-topics 1.5 and 1.6)  
**Date:** October 3, 2026  
**Status:** Complete  

---

## 1. Executive Summary

In this lab, a complete ReAct (Reason + Act) agent loop was designed and implemented from scratch in plain Python without using external agent frameworks (such as LangChain or CrewAI). The agent was equipped with two tools:
1. **`calculator(expression)`**: A safe AST-based arithmetic parser that evaluates math expressions without using unsafe `eval()`.
2. **`read_webpage(url)`**: A document/webpage reader that fetches HTTP/HTTPS URLs via `requests` or reads local `.html`/`.txt` files, stripping script/style blocks and HTML markup to return clean text.

Three critical failure modes inherent to agentic tool use were deliberately triggered and documented:
- **Failure 1 (Repeating loop):** Endless tool invocations when querying non-existent files.
- **Failure 2 (Hallucinated tool call):** Process crash due to unsafe registry lookup when the LLM hallucinated an unregistered tool (`send_email`).
- **Failure 3 (Context overflow & cost):** API rate limit errors (HTTP 413) and token inflation when reading massive document payloads (`big.html`).

Three defensive guards were implemented in `my_agent_fixed.py` to remedy these failures:
1. **Repeat Detection Guard (`seen_calls`):** Tracks `(tool_name, argument)` signatures to halt execution if identical calls repeat 3 times.
2. **Observation Truncation Guard (`MAX_TOOL_CHARS`):** Caps any single tool output at 1,500 characters.
3. **Character Budget Guard (`CHAR_BUDGET`):** Bounds total characters sent to the LLM across all steps to 30,000.

---

## 2. Code Files Created

1. **[notice.html](file:///c:/Users/SREE/OneDrive/Desktop/day1_lab/day3-practice/notice.html)**: Test document containing academic fee details, merit scholarship rules, hostel charges, and embedded `<script>` tags.
2. **[my_tools.py](file:///c:/Users/SREE/OneDrive/Desktop/day1_lab/day3-practice/my_tools.py)**: Contains AST calculator, HTML reader, tool registry (`TOOL_FUNCTIONS`), and JSON OpenAI function schemas (`TOOLS`).
3. **[my_agent.py](file:///c:/Users/SREE/OneDrive/Desktop/day1_lab/day3-practice/my_agent.py)**: The baseline ReAct agent loop built from scratch (Reason, Stop, Record, Act & Observe, Safety Exit).
4. **[make_big_page.py](file:///c:/Users/SREE/OneDrive/Desktop/day1_lab/day3-practice/make_big_page.py)**: Script generating `big.html` (~357,000 characters) for context overflow testing.
5. **[big.html](file:///c:/Users/SREE/OneDrive/Desktop/day1_lab/day3-practice/big.html)**: Attendance register file with 3,000 student table rows used to trigger overflow.
6. **[my_agent_fixed.py](file:///c:/Users/SREE/OneDrive/Desktop/day1_lab/day3-practice/my_agent_fixed.py)**: Guarded ReAct agent loop incorporating repeat detection, observation truncation, and character budget enforcement.

---

## 3. Terminal Execution Screenshots

### 3.1 Setup Check & Tools Output (`check_setup.py` & `my_tools.py`)
![Setup Check and my_tools.py Output](file:///c:/Users/SREE/OneDrive/Desktop/day1_lab/day3-practice/screenshots/day3_setup_and_tools.png)

### 3.2 Baseline Agent & Big Page Generation (`my_agent.py` & `make_big_page.py`)
![my_agent.py and make_big_page.py Output](file:///c:/Users/SREE/OneDrive/Desktop/day1_lab/day3-practice/screenshots/day3_agent_and_big_page.png)

### 3.3 Guarded Agent Execution (`my_agent_fixed.py`)
![my_agent_fixed.py Output](file:///c:/Users/SREE/OneDrive/Desktop/day1_lab/day3-practice/screenshots/day3_agent_fixed.png)

---

## 4. Observations & Laboratory Logs

### 4.1 Step Counts from Part C (Baseline Agent)

| Question | Steps Used | Tools Called | Final Result / Answer |
| :--- | :---: | :---: | :--- |
| **Merit scholarship total**<br>`"Read notice.html and tell me the total fee for CS101 and AI202 after the merit scholarship."` | 2 | `read_webpage`, `calculator` | **Rs. 27,000**<br>`(12000 + 18000) * 0.9 = 27000.0` |
| **Hostel student total**<br>`"Read notice.html. What does a hostel student taking all three courses pay in total, including laboratory charges?"` | 2 | `read_webpage`, `calculator` | **Rs. 49,500**<br>`12000 + 18000 + 15000 + 4500 = 49500` |
| **15% of AI202**<br>`"Read notice.html and tell me what is 15% of the AI202 fee?"` | 2 | `read_webpage`, `calculator` | **Rs. 2,700**<br>`18000 * 0.15 = 2700.0` |
| **Welcome message**<br>`"Write a one-line welcome message for new students."` | 0 | *None* | Direct LLM output: *"Welcome to your new chapter!"* |
| **Read URL (Optional)**<br>`"Read https://example.com and summarise it."` | 1 | `read_webpage` | Concise summary of example domain. |

---

### 4.2 Failure Log from Part D (Unguarded Agent)

| Failure Mode | What Was Observed (No Guards) | Cost & Impact (Steps / Time / Error) |
| :--- | :--- | :--- |
| **1. Repeating Loop** | Agent called `read_webpage({'url': 'fees.html'})` repeatedly. Each step returned `"Read error: 'fees.html' is not a URL and no such file exists."` | Burned all 6 steps (`max_steps`), ~12s latency, wasted 6 API calls without yielding an answer. |
| **2a. Hallucinated Tool (`.get`)** | System prompt instructed agent to call `send_email` if fee > 25000. Agent requested `send_email`. Registry lookup `TOOL_FUNCTIONS.get("send_email")` returned `None`. | Handled gracefully: returned `"Unknown tool: send_email"`. Agent continued execution and explained limitation politely. |
| **2b. Hallucinated Tool (`[]`)** | Unsafe registry lookup `TOOL_FUNCTIONS["send_email"]` executed. Python raised an unhandled `KeyError: 'send_email'`. | **FATAL CRASH:** Immediate process termination, entire conversation state lost. |
| **3. Context Overflow** | Disabling truncation (`max_chars = 200000`) on `big.html` resulted in 200,041 characters (~57,633 tokens) being injected into prompt context. | **API 413 ERROR:** `APIStatusError: Error code: 413 - Request too large on input tokens per minute (ITPM): Limit 7000, Requested 57633`. |

---

### 4.3 After the Fixes (Part E Guarded Agent)

| Failure Mode | Behavior with Guards | Guard That Acted |
| :--- | :--- | :--- |
| **1. Repeating Loop** | Stopped on the 3rd attempt: `"Stopped: the tool read_webpage was called 3 times with the same arguments and no progress was made. Last result: Read error: 'fees.html' is not a URL..."` | **Guard 1: Repeat Detection (`seen_calls`)** |
| **2. Unknown Tool** | Safe `.get()` lookup prevents `KeyError` crash and returns `"Unknown tool: send_email. Available: ['calculator', 'read_webpage']"`. | **Safe Registry Lookup (`TOOL_FUNCTIONS.get`)** |
| **3. Context Overflow** | Observation truncated at 1,500 characters (`" ... [observation truncated]"`). The agent read the initial table snippet and completed execution without context errors. | **Guard 2: Observation Truncation (`MAX_TOOL_CHARS = 1500`)** & **Guard 3: Character Budget (`CHAR_BUDGET = 30000`)** |

---

### 4.4 Chosen Limits & Justifications

| Setting | Value Chosen | Justification |
| :--- | :---: | :--- |
| `max_steps` | **6** | Approximately twice the longest successful run (2 steps), providing sufficient headroom for multi-step reasoning while capping infinite loops. |
| `MAX_TOOL_CHARS` | **1500** | Large enough to fit complete notice text/tables, but small enough that 10 cumulative tool outputs (~15,000 chars / ~3,750 tokens) easily fit within model context limits. |
| `CHAR_BUDGET` | **30000** | Bounds overall prompt context (~7,500 tokens max), providing headroom for complex queries while protecting against API token rate limits and cost inflation. |
| `Repeat threshold` | **3** | Allows 1 initial attempt + 1 retry for transient glitches, but halts the agent on the 3rd identical attempt to prevent spinning in dead-end loops. |

---

## 5. Discussion Questions

### Q1: In Failure 1 the model was not wrong about anything: it asked for a file it was told to read. Whose fault was the loop, and where should the fix live?
**Answer:**  
The loop was the fault of the **agent execution architecture (control loop)**, not the LLM. Because LLMs are stateless function-mappers, presenting the exact same conversation state and tool failure message will cause the LLM to output the same tool call again. The fix must live in the **agent runtime loop** via stateful execution tracking (`seen_calls` repeat detection), rather than expecting the LLM to break out of infinite loops on its own.

### Q2: The unsafe registry lookup crashed the program. Why is a crash worse than an "Unknown tool" message for an agent, when in ordinary code a crash is often preferred?
**Answer:**  
In conventional software engineering, fail-fast crashing prevents state corruption. However, in LLM agent systems, tool hallucination is a expected probabilistic generation anomaly rather than a syntax or memory fault. Returning an `"Unknown tool: <name>"` error string preserves the agent runtime, giving the model feedback so it can self-correct, try alternative available tools, or inform the user. A hard crash kills the process, destroying active state and breaking the user session.

### Q3: Your reader tool truncates at 2000 characters. What information could be lost by that, and how would you design the tool so the agent can still reach the rest?
**Answer:**  
Fixed truncation can cut off critical information located deep inside long documents (e.g., lower rows of large tables, detailed terms, or appendices). To provide access without context overflow, the reader tool should implement **paginated/windowed retrieval** (e.g., `offset`, `line_start`/`line_end` parameters) or a **semantic search/grep interface** allowing the agent to query specific sections on demand.

### Q4: The budget guard counts characters, not tokens or rupees. What would you need to count them properly, and why is the rough version still useful?
**Answer:**  
To count properly, one would require model-specific tokenizer libraries (e.g., `tiktoken` for OpenAI, `SentencePiece`/`transformers` for Qwen) and current API pricing tables. The character-counting guard remains extremely valuable because characters correlate linearly with token count (~4 characters per token in English), introducing zero external dependencies, negligible CPU overhead, and immediate protection against payload overflow.

### Q5: Would any of today's three guards have helped on Day 1's fee agent? Which failure modes are specific to tools that read the outside world?
**Answer:**  
Yes, **repeat detection** and **character budgets** would have prevented infinite loop spinning and runaway token costs on Day 1. However, **observation truncation** is specifically essential for tools interacting with the external environment (web scrapers, file readers, SQL queries), where payload sizes are untrusted and unpredictable, unlike internal math/string helpers whose outputs are small and bounded.

---

## 6. Viva Questions

1. **What are the six steps of the loop in `my_agent.py`, and which lines implement each?**
   - **Step 1 (REASON):** Lines 23–26 (`response = client.chat.completions.create(...)`). Queries the LLM with accumulated history.
   - **Step 2 (STOP):** Lines 29–30 (`if not message.tool_calls: return message.content.strip()`). Exits if no tools are requested.
   - **Step 3 (RECORD):** Lines 33–44 (`messages.append({"role": "assistant", ...})`). Saves assistant tool call requests into message history.
   - **Step 4 & 5 (ACT and OBSERVE):** Lines 47–68 (`for call in message.tool_calls: ... result = function(**arguments) ... messages.append({"role": "tool", ...})`). Dispatches tool functions and appends observations to history.
   - **Step 6 (SAFETY EXIT):** Line 71 (`return "Stopped: maximum steps reached without a final answer."`). Prevents infinite step execution.

2. **Why does the registry use `.get(name)` instead of `[name]`?**
   - `.get(name)` returns `None` safely when a tool name is missing, enabling soft error handling. `[name]` raises a hard `KeyError` that terminates the Python execution process.

3. **Why must a tool return an error string instead of raising an exception?**
   - Returning an error string injects the failure message into the ReAct conversation history as an observation. This allows the LLM to inspect the failure reason and re-plan, whereas raising an unhandled exception crashes the runtime.

4. **What does the tag-stripping regular expression remove, and why are script and style handled separately?**
   - `TAG = re.compile(r"<(script|style)[^>]*>.*?</\1>|<[^>]+>", re.S | re.I)` strips all HTML tags. `<script>` and `<style>` content are removed along with their inner body code because executable JavaScript and CSS styles are non-visible noise that pollutes the prompt context.

5. **Why does `read_webpage` truncate its output?**
   - To enforce an upper bound on document payload size, preventing context window exhaustion and excessive token costs.

6. **How does repeat detection tell a loop apart from legitimate repeated work?**
   - It hashes a combined signature of the **tool name** and **sorted JSON arguments** `(name, json.dumps(arguments, sort_keys=True))`. Repeating the *exact same tool with identical inputs* indicates a zero-progress loop, whereas calling the same tool with different arguments (e.g., reading different files) is recognized as legitimate progress.

7. **What is the difference between `max_steps` and `CHAR_BUDGET` as stopping conditions?**
   - `max_steps` bounds the number of interaction turns; `CHAR_BUDGET` bounds the cumulative text volume (tokens/cost). `max_steps` guards control flow; `CHAR_BUDGET` guards resource consumption.

8. **Name the three failure modes you triggered today and the guard that fixes each.**
   - 1. **Repeating loop:** Fixed by **Repeat Detection (`seen_calls`)**.
   - 2. **Hallucinated tool call:** Fixed by **Safe Registry Lookup (`TOOL_FUNCTIONS.get`)**.
   - 3. **Context overflow / cost:** Fixed by **Observation Truncation (`MAX_TOOL_CHARS`)** and **Character Budget (`CHAR_BUDGET`)**.

---

## 7. Result

Thus, a ReAct agent was built from scratch in plain Python with a calculator and a web-page reader tool; three failure modes were deliberately triggered and recorded; and repeat detection, output truncation and a budget guard were added to correct them. The observations show that incorporating deterministic defensive guards directly into the agent execution loop prevents fatal program crashes, eliminates infinite tool retry loops, bounds API token costs, and ensures robust operation without requiring modifications to the underlying LLM model.
