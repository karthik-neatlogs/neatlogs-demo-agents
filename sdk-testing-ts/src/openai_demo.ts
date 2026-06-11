import { config } from "dotenv";
import { resolve } from "path";
import { init, wrapOpenAI, flush, shutdown } from "neatlogs";
import OpenAI from "openai";

config({ path: resolve(import.meta.dir, "../../sdk-testing/.env") });

async function main() {
  await init({
    apiKey: process.env.NEATLOGS_API_KEY,
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
