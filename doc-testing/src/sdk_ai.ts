import "dotenv/config";
import { init, shutdown } from "neatlogs";
import { wrapAISDK } from "neatlogs/ai";
import * as ai from "ai";
import { openai } from "@ai-sdk/openai";

async function main() {
  await init({
    apiKey: process.env.NEATLOGS_API_KEY,
    endpoint: process.env.NEATLOGS_ENDPOINT,
    workflowName: "ai-sdk-demo",
  });

  const { generateText } = wrapAISDK(ai);

  const { text } = await generateText({
    model: openai("gpt-4o-mini"),
    prompt: "In one sentence, what is the Vercel AI SDK?",
  });
  console.log(text);

  await shutdown();
}

main().catch(console.error);
