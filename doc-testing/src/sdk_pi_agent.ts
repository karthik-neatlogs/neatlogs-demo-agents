import "dotenv/config";
import { init, shutdown } from "neatlogs";
import { piAgentHooks } from "neatlogs/pi-agent";
import { Agent } from "@mariozechner/pi-agent-core";
import { getModel } from "@mariozechner/pi-ai";

async function main() {
  await init({
    apiKey: process.env.NEATLOGS_API_KEY,
    endpoint: process.env.NEATLOGS_ENDPOINT,
    workflowName: "pi-agent-demo",
  });

  const agent = piAgentHooks(
    new Agent({
      initialState: {
        systemPrompt: "Be concise.",
        model: getModel("openai", "gpt-4o"),
        tools: [],
        messages: [],
      },
    }),
  );

  agent.subscribe((event) => {
    if (
      event.type === "message_update" &&
      event.assistantMessageEvent.type === "text_delta"
    ) {
      process.stdout.write(event.assistantMessageEvent.delta);
    }
  });

  await agent.prompt("In one sentence, what is Pi Agent?");
  console.log();

  await shutdown();
}

main().catch(console.error);
