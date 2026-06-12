import "dotenv/config";
import { init, span, trace, flush, shutdown, PromptTemplate, UserPromptTemplate } from "neatlogs";

await init({
  apiKey: process.env.NEATLOGS_API_KEY ?? "",
    endpoint: process.env.NEATLOGS_ENDPOINT,
  workflowName: "wizard-test",
  instrumentations: ["openai"],
});

// OpenAI imported AFTER init so the instrumentor patches it at load time.
const { default: OpenAI } = await import("openai");
const openai = new OpenAI();

import { Hono } from "hono";

const SYS_TPL = new PromptTemplate("You are a helpful assistant.");
const USER_TPL = new UserPromptTemplate("{{query}}");

const app = new Hono();

const handleChat = span({ kind: "WORKFLOW", name: "chat" }, async (query: string): Promise<string> => {
  return trace({ name: "llm_call", kind: "LLM", promptTemplate: SYS_TPL, userPromptTemplate: USER_TPL }, async () => {
    const sys = SYS_TPL.compile({}) as string;
    const user = USER_TPL.compile({ query }) as string;
    const res = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        { role: "system", content: sys },
        { role: "user", content: user },
      ],
    });
    return res.choices[0].message.content ?? "";
  });
});

app.get("/", (c) => {
  return c.text("Hello Hono!");
});

app.post("/chat", async (c) => {
  const { query } = await c.req.json<{ query: string }>();
  const answer = await handleChat(query);
  await flush();
  return c.json({ answer });
});

process.on("SIGTERM", async () => {
  await flush();
  await shutdown();
  process.exit(0);
});

process.on("SIGINT", async () => {
  await flush();
  await shutdown();
  process.exit(0);
});

export default { 
  port: 3006, 
  fetch: app.fetch, 
} 
