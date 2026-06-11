import "dotenv/config";
import { init, strandsHooks, shutdown } from "neatlogs";
import { Agent } from "@strands-agents/sdk";
import { OpenAIModel } from "@strands-agents/sdk/models/openai";

async function main() {
  await init({
    apiKey: process.env.NEATLOGS_API_KEY,
    workflowName: "strands-demo",
  });

  const model = new OpenAIModel({ api: "chat", modelId: "gpt-4o" });
  const agent = strandsHooks(new Agent({ model, printer: false }));

  const result = await agent.invoke("In one sentence, what is Strands?");
  const text = result.lastMessage?.content
    ?.map((part) => ("text" in part ? part.text : ""))
    .join("");
  console.log(text);

  await shutdown();
}

main().catch(console.error);
