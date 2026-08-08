#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { spawn } from "child_process";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { fileURLToPath } from "url";

/**
 * Determines the absolute path to the Trading repo root dynamically.
 * Priority:
 * 1. TRADING_REPO_ROOT environment variable (if set)
 * 2. process.cwd() if research_scanner exists in current working directory
 * 3. Two directories up from this script file (antigravity-bridge/src or antigravity-bridge/build -> repo root)
 */
function getRepoRoot(): string {
  if (process.env.TRADING_REPO_ROOT) {
    return path.resolve(process.env.TRADING_REPO_ROOT);
  }
  const cwdScanner = path.join(process.cwd(), "research_scanner");
  if (fs.existsSync(cwdScanner)) {
    return process.cwd();
  }
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
  return path.resolve(__dirname, "..", "..");
}

/**
 * Executes a CLI command with stdin redirected from /dev/null ('ignore'),
 * captures stdout/stderr, and enforces timeout with SIGTERM.
 */
function runCommand(
  file: string,
  args: string[],
  timeoutMs: number
): Promise<{ stdout: string; stderr: string; code: number | null }> {
  return new Promise((resolve, reject) => {
    const child = spawn(file, args, {
      stdio: ["ignore", "pipe", "pipe"],
      shell: false,
    });

    let stdout = "";
    let stderr = "";
    let timedOut = false;

    const timer = setTimeout(() => {
      timedOut = true;
      child.kill("SIGTERM");
    }, timeoutMs);

    child.stdout?.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    child.stderr?.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    child.on("error", (err: any) => {
      clearTimeout(timer);
      err.stdout = stdout;
      err.stderr = stderr;
      reject(err);
    });

    child.on("close", (code) => {
      clearTimeout(timer);
      if (timedOut) {
        const err: any = new Error(`Execution timed out after ${timeoutMs / 1000} seconds.`);
        err.code = "ETIMEDOUT";
        err.killed = true;
        err.stdout = stdout;
        err.stderr = stderr;
        return reject(err);
      }
      resolve({ stdout, stderr, code });
    });
  });
}

/**
 * Checks stderr, stdout, or error strings for quota or rate-limit specific indicators.
 * Reuses the exact logic/keywords from run_daemon.py's is_quota_error().
 */
function isQuotaError(stderr: string = "", stdout: string = "", extra: string = ""): boolean {
  const combined = `${stderr} ${stdout} ${extra}`.toLowerCase();
  const quotaKeywords = [
    "quota",
    "rate limit",
    "ratelimit",
    "rate_limit",
    "resource_exhausted",
    "resourceexhausted",
    "429",
    "too many requests",
  ];
  return quotaKeywords.some((kw) => combined.includes(kw));
}

const RUN_AGENT_TOOL: Tool = {
  name: "antigravity_run_agent",
  description:
    "Executes an autonomous agent via the local agy CLI binary in headless mode. " +
    "IMPORTANT: The prompt parameter MUST be completely self-contained with no assumed prior conversation context, " +
    "because each underlying CLI call runs statelessly in a fresh execution environment. " +
    "Executed as 'agy -p \"<prompt text>\" --add-dir \"<repo root>\" --output-format json'. " +
    "Does NOT use --dangerously-skip-permissions (relies on host permissions in ~/.gemini/antigravity-cli/settings.json). " +
    "Returns execution output, or distinct error states for quota exhaustion, process timeouts, missing binary, or CLI failures.",
  inputSchema: {
    type: "object",
    properties: {
      prompt: {
        type: "string",
        description:
          "Required. The complete, fully self-contained task prompt text for the agent to execute.",
      },
      timeout_seconds: {
        type: "number",
        description:
          "Optional. Timeout limit in seconds for the agent call (default: 300 seconds). Execution will be aborted if exceeded.",
      },
    },
    required: ["prompt"],
  },
  annotations: {
    readOnlyHint: false,
    destructiveHint: true,
    idempotentHint: false,
    openWorldHint: true,
  },
};

const CHECK_STATUS_TOOL: Tool = {
  name: "antigravity_check_status",
  description:
    "Lightweight check to verify that the local agy CLI binary is installed and executable without consuming API quota. " +
    "NOTE: The agy CLI does not provide a zero-quota authentication check subcommand; this tool verifies binary existence " +
    "and settings file availability, but cannot verify API token validity or session expiration without consuming quota.",
  inputSchema: {
    type: "object",
    properties: {},
  },
  annotations: {
    readOnlyHint: true,
    destructiveHint: false,
    idempotentHint: true,
    openWorldHint: true,
  },
};

const server = new Server(
  {
    name: "antigravity-bridge",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [RUN_AGENT_TOOL, CHECK_STATUS_TOOL],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "antigravity_check_status") {
    return handleCheckStatus();
  }

  if (name === "antigravity_run_agent") {
    const prompt = args?.prompt as string;
    const timeoutSeconds =
      typeof args?.timeout_seconds === "number" && args.timeout_seconds > 0
        ? args.timeout_seconds
        : 300;

    if (!prompt || typeof prompt !== "string") {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                status: "invalid_input_error",
                error: "Missing required string parameter 'prompt'.",
              },
              null,
              2
            ),
          },
        ],
        isError: true,
      };
    }

    return handleRunAgent(prompt, timeoutSeconds);
  }

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify({ status: "unknown_tool", error: `Unknown tool: ${name}` }, null, 2),
      },
    ],
    isError: true,
  };
});

async function handleCheckStatus() {
  const homeDir = os.homedir();
  const settingsPath = path.join(homeDir, ".gemini", "antigravity-cli", "settings.json");
  let settingsFileFound = false;

  try {
    if (fs.existsSync(settingsPath)) {
      settingsFileFound = true;
    }
  } catch {
    settingsFileFound = false;
  }

  try {
    const { stdout, stderr } = await runCommand("agy", ["--version"], 10000);

    const versionStr = stdout.trim() || stderr.trim();
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              status: "ok",
              cli_version: versionStr,
              settings_file_found: settingsFileFound,
              settings_path: settingsPath,
              auth_status_note:
                "agy CLI does not provide a zero-quota auth-status endpoint. Binary presence and settings file confirmed.",
            },
            null,
            2
          ),
        },
      ],
    };
  } catch (err: any) {
    if (err.code === "ENOENT") {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                status: "binary_not_found_error",
                error: "agy executable not found in PATH.",
                settings_file_found: settingsFileFound,
              },
              null,
              2
            ),
          },
        ],
        isError: true,
      };
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              status: "execution_error",
              error: `Failed to execute 'agy --version': ${err.message}`,
              settings_file_found: settingsFileFound,
            },
            null,
            2
          ),
        },
      ],
      isError: true,
    };
  }
}

async function handleRunAgent(prompt: string, timeoutSeconds: number) {
  const timeoutMs = timeoutSeconds * 1000;
  const repoRoot = getRepoRoot();
  const cmdArgs = ["-p", prompt, "--add-dir", repoRoot, "--output-format", "json"];

  try {
    // Execute agy CLI with stdin redirected from null (ignore)
    // and enforced timeout via setTimeout & SIGTERM kill.
    const { stdout, stderr, code } = await runCommand("agy", cmdArgs, timeoutMs);

    const stdoutText = stdout.trim();
    const stderrText = stderr.trim();

    if (isQuotaError(stderrText, stdoutText)) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                status: "quota_error",
                error: "QUOTA EXHAUSTED - Antigravity API rate limit or quota exceeded.",
                stdout: stdoutText,
                stderr: stderrText,
              },
              null,
              2
            ),
          },
        ],
        isError: true,
      };
    }

    if (code !== 0) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                status: "execution_error",
                error: `agy CLI call failed with exit code ${code}`,
                stdout: stdoutText,
                stderr: stderrText,
              },
              null,
              2
            ),
          },
        ],
        isError: true,
      };
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              status: "success",
              stdout: stdoutText,
              stderr: stderrText,
            },
            null,
            2
          ),
        },
      ],
    };
  } catch (err: any) {
    const stdoutText = err.stdout ? err.stdout.toString().trim() : "";
    const stderrText = err.stderr ? err.stderr.toString().trim() : "";

    // 1. Quota error detection
    if (isQuotaError(stderrText, stdoutText, err.message || "")) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                status: "quota_error",
                error: "QUOTA EXHAUSTED - Antigravity API rate limit or quota exceeded.",
                stdout: stdoutText,
                stderr: stderrText,
              },
              null,
              2
            ),
          },
        ],
        isError: true,
      };
    }

    // 2. Timeout error detection
    if (err.code === "ETIMEDOUT" || err.signal === "SIGTERM" || err.killed) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                status: "timeout_error",
                error: `Execution timed out after ${timeoutSeconds} seconds.`,
                stdout: stdoutText,
                stderr: stderrText,
              },
              null,
              2
            ),
          },
        ],
        isError: true,
      };
    }

    // 3. Binary not found error detection
    if (err.code === "ENOENT") {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                status: "binary_not_found_error",
                error: "agy executable not found in PATH.",
                stdout: stdoutText,
                stderr: stderrText,
              },
              null,
              2
            ),
          },
        ],
        isError: true,
      };
    }

    // 4. Generic execution error
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              status: "execution_error",
              error: `agy CLI call failed (exit code ${err.code ?? "unknown"}): ${err.message}`,
              stdout: stdoutText,
              stderr: stderrText,
            },
            null,
            2
          ),
        },
      ],
      isError: true,
    };
  }
}

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Fatal error in antigravity-bridge MCP server:", error);
  process.exit(1);
});
