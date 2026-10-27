# Prompt Engineering

Topic: NLP & GenAI

## What a prompt is
A prompt is the input text you give a language model. The same model can give a vague answer or an excellent one
depending on how the request is written. Prompt engineering is the practice of writing clear, specific instructions and
testing them systematically.

## Principles of a good prompt
- **Be specific about the task:** "Summarise this review in two sentences for a product manager" beats "Summarise this".
- **Give context:** who the audience is, what the answer will be used for, and any facts the model needs.
- **Show the format:** ask for bullet points, a table or JSON with named fields.
- **Set boundaries:** say what to do when the information is missing, for example "If the answer is not in the text,
  say you don't know".

## System and user messages
Chat models accept messages with roles. The **system message** sets lasting behaviour, such as "You are a patient tutor
for beginners. Answer in simple English." The **user message** carries the actual request. Keeping rules in the system
message makes behaviour more consistent across a conversation.

## Zero-shot and few-shot prompting
A **zero-shot** prompt simply describes the task. A **few-shot** prompt also includes a handful of worked examples of
input and desired output. Examples are one of the most reliable ways to show the model the style, labels or format you
want, especially for classification and data extraction.

## Asking for step-by-step reasoning
For multi-step problems, asking the model to work through the problem before giving a final answer often improves
accuracy. In applications, ask for the reasoning and the final answer in separate fields so your code can read the answer
reliably.

## Structured output
When code will read the answer, request JSON with exact field names and then validate it. Always handle the case where
the output is not valid JSON, for example by retrying or showing an error.

## Testing prompts
Treat prompts like code. Keep a small set of test inputs, run every prompt version on all of them and compare the results.
Change one thing at a time so you know what helped.

## Prompt injection
If your prompt includes text from users or documents, that text may contain instructions such as "ignore previous
instructions". Clearly separate untrusted content, tell the model to treat it as data, and never give the model more
permissions than the task needs.
