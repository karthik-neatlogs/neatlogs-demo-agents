// import "dotenv/config";
// import { init, span, trace, PromptTemplate, UserPromptTemplate, flush, shutdown } from "neatlogs";

// await init({
//   apiKey: process.env.NEATLOGS_API_KEY ?? "",
//   endpoint: process.env.NEATLOGS_ENDPOINT,
//   workflowName: "doc-testing",
//   instrumentations: ["openai"],
// });

// // LLM SDK imported AFTER init so the instrumentor patches it at load time
// const { default: OpenAI } = await import("openai");

// import { Hono } from "hono";

// const app = new Hono();
// const client = new OpenAI();

// const SYS_TPL = new PromptTemplate("You are a helpful assistant.");
// const USER_TPL = new UserPromptTemplate("{{query}}");

// const handleQuery = span({ kind: "WORKFLOW", name: "handle_query" }, async (query: string) => {
//   return trace(
//     { name: "llm_call", kind: "LLM", promptTemplate: SYS_TPL, userPromptTemplate: USER_TPL },
//     async () => {
//       const sys = SYS_TPL.compile() as string;
//       const user = USER_TPL.compile({ query }) as string;
//       const res = await client.chat.completions.create({
//         model: "gpt-4o",
//         messages: [
//           { role: "system", content: sys },
//           { role: "user", content: user },
//         ],
//       });
//       return res.choices[0].message.content;
//     }
//   );
// });

// app.get("/", (c) => {
//   return c.text("Hello Hono!");
// });

// app.post("/ask", async (c) => {
//   const { query } = await c.req.json<{ query: string }>();
//   const answer = await handleQuery(query);
//   return c.json({ answer });
// });

// const onShutdown = async () => {
//   await flush();
//   await shutdown();
//   process.exit(0);
// };

// process.on("SIGTERM", onShutdown);
// process.on("SIGINT", onShutdown);

// const port = Number(process.env.PORT) || 3006;

// const server = Bun.serve({
//   port,
//   fetch: app.fetch,
//   development: process.env.NODE_ENV !== "production",
// });

// console.log(`Listening on http://localhost:${server.port}`);




import "dotenv/config";
import { init, wrapOpenAI, flush, shutdown } from "neatlogs";
import OpenAI from "openai";

async function main() {
  await init({
    apiKey: process.env.NEATLOGS_API_KEY,
    // endpoint: process.env.NEATLOGS_ENDPOINT,
    workflowName: "my-first-app",
    // debug: true,
  });

  const client = wrapOpenAI(new OpenAI());

  const res = await client.chat.completions.create({
    model: 'gpt-4o',
    messages: [{ role: 'user', content: 'What is the capital of France?' }],
  });
  console.log(res.choices[0].message.content);

  await flush();
  await shutdown();
}

main().catch(console.error);