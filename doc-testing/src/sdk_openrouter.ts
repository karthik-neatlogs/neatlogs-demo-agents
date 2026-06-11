import "dotenv/config";
import { init, flush, shutdown } from "neatlogs";
import { wrapOpenRouterAgent } from "neatlogs/openrouter-agent";
import { OpenRouter } from "@openrouter/agent";

async function main() {
  await init({
    apiKey: process.env.NEATLOGS_API_KEY,
    workflowName: "openrouter-demo",
  });

  const openrouter = wrapOpenRouterAgent(
    new OpenRouter({ apiKey: process.env.OPENROUTER_API_KEY! }),
  );

  const result = openrouter.callModel({
    model: "openai/gpt-4o-mini",
    input: "In one sentence, what is OpenRouter?",
    temperature: 0.3,
    topP: 0.9,
    maxOutputTokens: 256,
  });
  console.log(await result.getText());

  await flush();
  await shutdown();
}

main().catch(console.error);
