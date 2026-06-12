import { config } from "dotenv";
import { resolve } from "path";
import { init, langchainHandler, flush, shutdown } from "neatlogs";

config({ path: resolve(import.meta.dir, "../../sdk-testing/.env") });

async function main() {
  await init({
    apiKey: process.env.NEATLOGS_API_KEY,
    endpoint: process.env.NEATLOGS_ENDPOINT,
    workflowName: "langchain-demo",
  });

  const { ChatOpenAI } = await import("@langchain/openai");
  const llm = new ChatOpenAI({ model: "gpt-4o" });

  const handler = langchainHandler();
  const res = await llm.invoke("In one sentence, what is LangChain?", {
    callbacks: [handler],
  });
  console.log(res.content);

  await flush();
  await shutdown();
}

main().catch(console.error);
