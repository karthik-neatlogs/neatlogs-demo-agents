import "dotenv/config";
import { init, wrapOpenAI, flush, shutdown } from "neatlogs";
import OpenAI from "openai";

async function main() {
  await init({
    apiKey: process.env.NEATLOGS_API_KEY,
    endpoint: process.env.NEATLOGS_ENDPOINT,
    workflowName: "openai-demo",
  });

  const client = wrapOpenAI(new OpenAI());

  const res = await client.chat.completions.create({
    model: "gpt-4o",
    messages: [{ role: "user", content: "In one sentence, what is OpenAI?" }],
  });
  console.log(res.choices[0].message.content);

  await flush();
  await shutdown();
}

main().catch(console.error);
