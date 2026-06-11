import "dotenv/config";
import { init, openaiAgentsProcessor, shutdown } from "neatlogs";
import { addTraceProcessor, Agent, run } from "@openai/agents";

async function main() {
  await init({
    apiKey: process.env.NEATLOGS_API_KEY,
    workflowName: "openai-agents-demo",
  });

  addTraceProcessor(openaiAgentsProcessor());

  const agent = new Agent({
    name: "assistant",
    instructions: "Be concise.",
  });

  const result = await run(
    agent,
    "In one sentence, what is the OpenAI Agents SDK?",
  );
  console.log(result.finalOutput);

  await shutdown();
}

main().catch(console.error);
