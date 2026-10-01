# Agentic AI: Day 2 Lab Report
**Tracing ReAct on Paper, and Comparing Answers With and Without Chain-of-Thought**

---

## 1. Executive Summary
This lab explores the internal mechanics of agentic reasoning, specifically comparing paper-traced ReAct cycles against real machine agent execution, as well as evaluating the performance of direct prompting vs. Chain-of-Thought (CoT) prompting and Self-Consistency sampling on complex multi-step reasoning problems.

---

## 2. Setup & Environment Verification

![Setup Check Output](screenshots/01_check_setup.png)

```text
Python version : 3.11.9
Provider       : groq
Model          : qwen/qwen3.8-27b
Calling the model ...
Model replied : SETUP OK
```

---

## 3. Part A & B: ReAct Trace Analysis

### Problem Statement
> *Which is cheaper: CS101 and AI202 with a 10% scholarship, or all three courses with a 25% scholarship? And by how much?*
> 
> Fee Structure:
> - **CS101**: Rs. 12,000
> - **AI202**: Rs. 18,000
> - **DS303**: Rs. 15,000

### Execution Output (Real Agent Trace)

![Real ReAct Trace Output](screenshots/02_react_trace.png)

```text
--- the agent's actions and observations ---
   step 1: get_course_fee({'course_code': 'CS101'}) -> 12000
   step 1: get_course_fee({'course_code': 'AI202'}) -> 18000
   step 1: get_course_fee({'course_code': 'DS303'}) -> 15000
   step 2: calculator({'expression': '(12000+18000)*0.9'}) -> 27000.0
   step 2: calculator({'expression': '(12000+18000+15000)*0.75'}) -> 33750.0
   step 3: calculator({'expression': '33750-27000'}) -> 6750

FINAL ANSWER: CS101 + AI202 with a 10% scholarship is cheaper by Rs. 6,750.
```

---

### 3.1 Paper ReAct Trace Worksheet (Section 7.1)

| Step | Type | Content | Why this step |
| :--- | :--- | :--- | :--- |
| 1 | **Thought** | I need to get the fee for course CS101. | Need cost of CS101 for Option 1. |
| 2 | **Action** | `get_course_fee('CS101')` | Query tool for CS101 fee. |
| 3 | **Observation** | `12000` | Retrieved fee. |
| 4 | **Thought** | I need to get the fee for course AI202. | Need cost of AI202 for Option 1. |
| 5 | **Action** | `get_course_fee('AI202')` | Query tool for AI202 fee. |
| 6 | **Observation** | `18000` | Retrieved fee. |
| 7 | **Thought** | I will calculate the cost of CS101 and AI202 with a 10% scholarship. | Compute Option 1 total. |
| 8 | **Action** | `calculator('(12000 + 18000) * 0.9')` | Calculate discounted total. |
| 9 | **Observation** | `27000.0` | Option 1 result. |
| 10 | **Thought** | I need to get the fee for course DS303. | Need DS303 fee for Option 2. |
| 11 | **Action** | `get_course_fee('DS303')` | Query tool for DS303 fee. |
| 12 | **Observation** | `15000` | Retrieved fee. |
| 13 | **Thought** | I will calculate the cost of all three courses with a 25% scholarship. | Compute Option 2 total. |
| 14 | **Action** | `calculator('(12000 + 18000 + 15000) * 0.75')` | Calculate discounted total. |
| 15 | **Observation** | `33750.0` | Option 2 result. |
| 16 | **Thought** | I will calculate how much cheaper Option 1 is than Option 2. | Find the difference. |
| 17 | **Action** | `calculator('33750 - 27000')` | Compute price difference. |
| 18 | **Observation** | `6750.0` | Difference result. |
| 19 | **Final Answer** | Taking CS101 and AI202 with the 10% scholarship costs Rs. 27,000, which is Rs. 6,750 cheaper than all three courses at Rs. 33,750. | State final conclusion. |

---

### 3.2 Paper Trace vs Agent Trace Comparison (Section 11.1)

| Item | Your Paper Trace | The Agent (Machine Trace) |
| :--- | :--- | :--- |
| **Number of fee lookups** | 3 (`CS101`, `AI202`, `DS303`) | 3 (`CS101`, `AI202`, `DS303`) |
| **Number of calculator calls** | 3 | 3 |
| **Total steps** | 6 tool-call steps (19 rows) | 3 steps (parallel batching) |
| **Any tools called in parallel? (Y/N)** | N (Sequential on paper) | **Y** (Step 1 called 3 lookups; Step 2 called 2 calc operations) |
| **Final answer** | Rs. 6,750 cheaper | Rs. 6,750 cheaper |
| **Correct? (Y/N)** | Y | Y |

---

## 4. Part C: Chain-of-Thought (CoT) Comparison (Section 11.2)

### Execution Screenshots

#### Question 1 (Multi-step arithmetic: Instalments)
![CoT Comparison Question 1](screenshots/03_cot_compare_q1.png)

#### Question 3 (Ordering / Logic: Height ordering)
![CoT Comparison Question 3](screenshots/04_cot_compare_q3.png)

### Empirical Comparison Results Table

| Question | Without CoT Correct? (Y/N) | With CoT Correct? (Y/N) | Which reply was longer? |
| :--- | :--- | :--- | :--- |
| **Q1 instalments** | **N** (Outputs `10,125` - fails arithmetic) | **Y** (Outputs `9562.5` step-by-step) | **With CoT** (~150 words vs 2 words) |
| **Q2 lab sittings** | **Y** (Outputs `90`) | **Y** (Outputs `90` with full breakdown) | **With CoT** (~100 words vs 1 word) |
| **Q3 tallest and shortest** | **Y** (Outputs `Tallest: Ravi; Shortest: Priya`) | **Y** (Outputs `Ravi tallest, Priya shortest` with derivation) | **With CoT** (~200 words vs 6 words) |

---

## 5. Part D: Self-Consistency Evaluation (Section 11.3)

### Execution Screenshot

![Self-Consistency Output](screenshots/05_self_consistency.png)

### Results Table

| Item | Value |
| :--- | :--- |
| **Answers seen across the 5 runs** | `Rs. 9,562.50` (5 out of 5 runs) |
| **Majority answer** | `Rs. 9,562.50` |
| **Was the majority answer correct?** | **Yes** |
| **Result when temperature = 0** | Identical output across all 5 runs (deterministic decoding) |

---

## 6. Discussion Questions (Section 12)

1. **Your paper trace and the agent's trace probably differ. Does a different order of steps make either one wrong?**
   - **Answer:** No. As long as data dependencies are respected (e.g., retrieving a fee before using it in a calculation), the precise order of independent tool calls does not affect correctness. In fact, real agents can execute independent tool calls in parallel (e.g., retrieving all three course fees in a single API round-trip), which optimizes latency without altering correctness.

2. **In Part C, the model improved when asked to think step by step. If the ability was already there, why did it not do this by itself?**
   - **Answer:** Autoregressive LLMs predict tokens sequentially. In direct prompting, the model must output the final answer in the very next token without intermediate scratchpad computations. When forced to output intermediate tokens (CoT), the LLM allocates compute per reasoning step, allowing attention mechanisms to compute intermediate numerical results dynamically across token positions.

3. **Chain-of-Thought could not answer the fee question correctly. Which component from Day 2 theory is missing, and which pattern supplies it?**
   - **Answer:** **Grounding / External Environment (Tools)** is missing. CoT relies purely on parametric memory. For private or dynamic data (like custom course fees), CoT will hallucinate facts. The **ReAct (Reason + Act)** pattern supplies tools to query real-world databases and perform deterministic execution.

4. **Self-consistency needs a non-zero temperature, but Day 1 used temperature 0 for tool calling. Explain why the two settings differ.**
   - **Answer:** Tool calling requires maximum determinism and strict JSON schema adherence, making `temperature = 0` optimal to avoid syntax errors or invalid function arguments. Self-consistency, however, relies on sampling diverse reasoning paths across the solution space; non-zero temperature ($T=0.8$) introduces stochasticity so different reasoning trajectories can be generated and voted on.

5. **The agent solved the Section 6 question in around six tool calls. How would Plan-and-Execute handle the same question, and how many LLM calls would it need?**
   - **Answer:** Plan-and-Execute would use **2 LLM calls**: 
     - **Call 1 (Planner):** Generates a full static execution plan upfront ("1. Get fees for CS101, AI202, DS303. 2. Calculate Option 1. 3. Calculate Option 2. 4. Subtract").
     - **Call 2 (Re-planner / Summarizer):** Synthesizes results after an execution engine runs all tool steps.
     ReAct required multiple LLM iterations (one per step/batch), while Plan-and-Execute decouples planning from execution, reducing LLM round-trips.

---

## 7. Viva Questions (Section 14)

1. **What are the three row types in a ReAct trace, and what does each contain?**
   - **Thought:** The model's internal reasoning about what information is needed next and why.
   - **Action:** The explicit tool call command and arguments sent to an external environment.
   - **Observation:** The actual data/result returned by the tool execution.

2. **Why can a thought not change anything in the outside world?**
   - **Thought** is internal text generated inside the LLM's context window. Only an **Action** invokes external APIs, code execution, or database calls that cause side-effects in the outside environment.

3. **What is the difference between Chain-of-Thought and ReAct?**
   - **Chain-of-Thought (CoT)** expands internal reasoning step-by-step using parametric knowledge only, with no tool access.
   - **ReAct** interleaves reasoning (Thought) with external environment interaction (Action) and feedback (Observation), enabling real-time tool usage and fact grounding.

4. **Why did CoT fail on the course-fee question?**
   - Course fees are domain-specific private data not present in the public training corpus of the LLM. Without external tool lookups, CoT hallucinates fictitious fee numbers.

5. **Why does self-consistency need temperature above 0?**
   - At `temperature = 0`, greedy decoding generates the exact same token sequence on every run. Non-zero temperature enables sampling multiple distinct reasoning paths needed for majority voting.

6. **Why is voting done on the final answer rather than on the whole reply?**
   - Reasoning paths vary in phrasing, formatting, and step wording even when arriving at the same exact logical conclusion. Voting on the extracted final answer normalizes the variance and isolates the core claim.

7. **What does it mean when two tool calls are printed under the same step number?**
   - It indicates **parallel tool execution**. The LLM generated multiple tool call requests in a single response turn, which the agent runtime executed simultaneously.

8. **Name one advantage and one disadvantage of Chain-of-Thought prompting.**
   - **Advantage:** Significantly improves multi-step reasoning accuracy without training or external software tools.
   - **Disadvantage:** Increases token consumption, cost, and response latency; cannot retrieve private/external data.

---

## 8. Result Statement (Section 15)

> *Thus, a ReAct run was traced on paper and compared with the trace produced by a working agent, and the effect of Chain-of-Thought prompting and self-consistency was measured on a set of reasoning questions. The observations show that Chain-of-Thought prompting substantially improves mathematical reasoning accuracy over direct prompting by providing intermediate context workspace, while ReAct provides essential grounding in external dynamic data through deterministic tool integration.*
