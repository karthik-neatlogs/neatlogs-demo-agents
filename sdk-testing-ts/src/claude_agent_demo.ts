import { config } from "dotenv";
import { resolve } from "path";
import { init, flush, shutdown } from "neatlogs";
import { wrapClaudeAgentSDK } from "neatlogs/claude-agent-sdk";
import * as claudeAgentSDK from "@anthropic-ai/claude-agent-sdk";

config({ path: resolve(import.meta.dir, "../../sdk-testing/.env") });

async function main() {
  await init({
    apiKey: process.env.NEATLOGS_API_KEY,
    workflowName: "claude-agent-demo",
  });

  const { query } = wrapClaudeAgentSDK(claudeAgentSDK);

  for await (const message of query({
    prompt:
      "List the files in the current directory and summarize what this project does.",
    options: { model: "claude-sonnet-4-5" },
  })) {
    if (message.type === "result") console.log(message.result);
  }

  await flush();
  await shutdown();
}

main().catch(console.error);
