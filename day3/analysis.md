# From Prompt to Action: Understanding LLMs, Tools, and Agents (GPA-Calculator Scenario)

## Scenario

I chose a small student scenario. A student asks a few general questions about GPA, such as what it means and why colleges weight it by credits. The student also gives a list of semester courses with grades and credit values and asks for the exact GPA. The general questions can be answered from knowledge. The GPA question needs an exact credit-weighted average, which is an operation, not a fact. I used a 10-point scale (O=10, A+=9, A=8, B+=7, B=6, C=5, U=0), which I stated in the question so the model had everything it needed. The one tool, `calculate_gpa`, computes that average. I ran five questions in two ways: Q1, Q3 and Q5 are general (no tool needed), and Q2 and Q4 need exact arithmetic (tool needed).

## 3.1 Explanation of Concepts

**What is a Large Language Model?** An LLM is a program trained on a very large amount of text to predict what text should come next. Everything it says is generated from patterns learned during training, so it answers immediately, in one pass, from what it already "knows". In my scenario it handles Q1 ("what does GPA stand for and measure?"), Q3 (why weight by credits) and Q5 (habits for a high GPA) confidently and correctly, because these are widely documented, stable ideas that appear throughout its training data. It starts to guess or go wrong when the answer depends on information it cannot have (my actual grades, today's data, a private file) or on an operation that must be exact. Q2 and Q4 are the second kind. Computing 162/20 or 159/19 is not recall. The model has to carry out several multiplications and a division in text. A model can often manage this, but nothing guarantees it. A single slip in a product or a rounding step gives a wrong number that is stated just as confidently as a right one, and the reader cannot tell the difference.

**What is an agent, and how does its response differ?** In the LLM context, an agent is an LLM that is connected to tools and can decide, while answering, to use them. A plain chat model returns text and stops. An agent can see that a question needs something it cannot produce reliably, ask for an action, receive the real result, and then answer. For my Q2, the plain chat response is a GPA typed out from the model's own internal calculation. The agent's response is a GPA that came back from running `calculate_gpa` on the six courses, with the model wrapping that exact result in a sentence. For Q1 the two behave the same, because a good agent does not call a tool when it has no need to. Even with one tool and no loop, this "recognise the need, act, then answer" behaviour is what makes the system agent-like.

**What is a tool, and what is a tool call?** A tool is an ordinary function in my code (here `calculate_gpa(courses)`) that the model is allowed to request. A tool call is the model's request to run it: a structured message naming the tool and giving the argument values, for example the list of courses with grades and credits. The model never runs the function itself. It only produces the request, and my script runs the code and sends the result back. The model knows the tool exists only through its schema, which has three parts. The **name** (`calculate_gpa`) identifies it. The **description** says what it does and when to use it ("calculates a semester GPA as a credit-weighted average... use it whenever the user gives courses with grades and credits"). The **parameters** say what to pass and in what shape (an array of courses, each with grade and credits). The model needs this description before deciding anything because it cannot see the function's code. The schema is all it knows about the tool. Without a clear description it cannot tell that a GPA question matches this tool, and without the parameter definitions it cannot build a valid call. A vague description would lead to the tool being skipped or called wrongly.

**How one tool call flows from start to finish.** Take Q2. First, the user's question, with the courses, grades and credits, is sent to the model together with the tool schema. Second, the model reads the question and the schema and decides that an exact credit-weighted average is needed. Instead of writing a number, it replies with a tool call: `calculate_gpa` with the six courses as arguments, and it stops there. Third, my script sees the tool call and runs `calculate_gpa` on those arguments. The function multiplies each grade point by its credits, sums them (162), sums the credits (20) and divides, giving 8.10. Fourth, the result is sent back to the model as a tool result in the conversation. Fifth, the model reads the result and writes the final answer, telling the student their GPA is 8.10. For Q1 the flow stops after the second step with a direct answer, because the model judges that no tool is needed.

**Why a tool should return plain text even when it fails.** A tool result goes back into the conversation for the model to read. Plain text is something the model can read and reason about, while a raised exception is not. If the tool crashes with an exception, my script stops before the model ever sees the problem, and the student gets a stack trace instead of an answer. If the tool instead returns a sentence such as `ERROR: unknown grade 'D' for X. Valid grades: O, A+, A, B+, B, C, U.`, the model can read it and explain the problem to the student or ask for a corrected grade. My `calculate_gpa` therefore never raises: bad grades, zero credits, empty lists and unexpected exceptions all come back as an `ERROR: ...` string. Returning failures as text also keeps the program running, and it fits the way the model works, since text is its only input.

## 3.2 Comparison Table

| Basis for comparison | Plain LLM prompt (no tool) | LLM with one tool (`calculate_gpa`) |
|---|---|---|
| Source of the answer | The model's trained knowledge and its own text-based calculation | General questions from trained knowledge; the GPA number from the function's exact computation |
| Can it fetch or compute information outside its own memory? | No. It can only generate text, so it cannot reliably run an operation or read new data | Yes, within the one tool: it can request a real calculation and use the real result |
| Reliability on factual or numeric questions | Good on stable general knowledge. For multi-step arithmetic it may be right, but nothing guarantees it, and wrong answers look equally confident | High for the numeric question, since the arithmetic is done by code that gives the same correct result every time; the model's job is limited to passing the courses correctly and reporting the result |
| Transparency (can you see how the answer was reached?) | Low. You see only the final text, and any working is the model's own account | High. You can see the tool call, its exact arguments and the raw result, and check them against the question |
| Speed / cost of getting an answer | Fastest and cheapest: one model call | Slower and costlier for tool questions: two model calls plus a function run. Questions that need no tool cost the same as before (one call) |

## 3.3 Minimal Implementation

The repository holds the smallest working example. `tool.py` contains the one tool, `calculate_gpa`, and its schema. `no_tool.py` asks the five questions directly with no tool access and saves each answer to `outputs/no_tool_output.txt`. `with_tool.py` asks the same five questions with the tool available, runs one tool-call round (it handles a tool request if the model makes one, with no ReAct loop), and saves the tool call, the tool result and the final answer for each question to `outputs/with_tool_output.txt`. `common.py` holds the questions so that both scripts receive identical input, and `run_all.bat` runs the whole workflow. Screenshots of both runs are in the `screenshots` folder.

## 3.4 Observation

The correct values, computed by the tool, are **8.10** for Q2 (162 grade points over 20 credits) and **8.37** for Q4 (159 grade points over 19 credits, which is 8.368...). I compared every answer against these.

**Q1: what does GPA stand for and measure? (no tool needed).**
Plain run: *[FILL IN from your no-tool run: correct / guessed / refused / confidently wrong]*. With tool: *[FILL IN: did it avoid calling the tool? it should]*. This is a stable general-knowledge question, and the expected behaviour in both runs is a correct direct answer with no tool call.

**Q2: semester GPA for six courses (tool needed).**
Plain run: *[FILL IN: the number the model gave, whether it matches 8.10, and whether it showed working]*. With tool: *[FILL IN: the tool call arguments shown in your log, the tool result, and whether the final answer says 8.10]*. The key check is that the tool-enabled answer matches the tool's printed result exactly.

**Q3: why weight GPA by credits? (no tool needed).**
Plain run: *[FILL IN]*. With tool: *[FILL IN: tool call or none]*. This is a conceptual explanation. Calling the tool here would be a mistake, because there is no list of courses to calculate.

**Q4: semester GPA for seven courses, with a result that is not a round number (tool needed).**
Plain run: *[FILL IN: the number given, whether it matches 8.37, whether it rounded correctly]*. With tool: *[FILL IN: arguments, result, final answer]*. This question is harder to do mentally because 159/19 does not divide evenly and the credits include a 1-credit course, so it is the better test of whether the plain model's arithmetic holds up.

**Q5: two habits for a high GPA (no tool needed).**
Plain run: *[FILL IN]*. With tool: *[FILL IN]*. Again, a direct answer is correct and no tool is needed.

*(Write each line in your own words from your actual logs in `outputs/` and your screenshots. If the plain model got Q2 and Q4 right, say so. It is a legitimate finding, and the point then is that the answer cannot be verified from the text, not that it was wrong.)*

## 3.5 Suitability and Conclusion

In my scenario, the plain LLM prompt was good enough for Q1, Q3 and Q5. These are questions of explanation and general knowledge, where the answer lives in the model's training and there is nothing to verify beyond common sense. A tool would add cost and delay without improving anything. A single tool became necessary for Q2 and Q4, the exact GPA calculations. Even if the plain model sometimes gets these right, the student is relying on a number produced by text prediction, with nothing to check it against. For a figure that may be used for scholarship forms, internship applications or eligibility cutoffs, it should come from code that does the arithmetic and shows the steps. The tool's output also shows its working, so a human can check it in seconds.

In general, a plain LLM prompt is sufficient when the answer is stable, general knowledge or language work: explaining a concept, summarising or rewriting text supplied in the prompt, brainstorming, drafting, or translating. A problem needs a tool when the correct answer depends on something the model cannot reliably produce from memory. That includes exact or multi-step calculations, current or changing information (prices, weather, news), private or user-specific data held in files or databases, and any real-world action such as sending a message or writing a file. The practical test is to ask whether a wrong answer would be both likely and hard to notice. If so, the answer should come from a tool, and the model's role is to recognise the need, make the call and explain the result.
