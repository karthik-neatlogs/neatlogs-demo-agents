import "dotenv/config";
import { init, wrapMastra, flush, shutdown } from "neatlogs";

async function main() {
  await init({
    apiKey: process.env.NEATLOGS_API_KEY,
    workflowName: "mastra-demo",
  });

  const { Agent } = await import("@mastra/core/agent");
  const { openai } = await import("@ai-sdk/openai");

  const agent = wrapMastra(
    new Agent({
      name: "assistant",
      instructions: "Be concise.",
      model: openai("gpt-4o"),
    }),
  );

  const res = await agent.generate("In one sentence, what is Mastra?");
  console.log(res.text);

  await flush();
  await shutdown();
}

main().catch(console.error);
