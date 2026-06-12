import "dotenv/config";
import { init, flush, shutdown, openaiAgentsProcessor } from "neatlogs";
import { Agent, run, addTraceProcessor } from "@openai/agents";

async function main() {
  await init({
    apiKey: process.env.NEATLOGS_API_KEY,
    endpoint: process.env.NEATLOGS_ENDPOINT,
    workflowName: "openai-agents-demo",
  });

  addTraceProcessor(openaiAgentsProcessor());

  const agent = new Agent({ name: "assistant", instructions: "Be concise." });
  const result = await run(
    agent,
    "In one sentence, what is the OpenAI Agents SDK?",
  );
  console.log(result.finalOutput);

  await flush();
  await shutdown();
}

main().catch(console.error);
