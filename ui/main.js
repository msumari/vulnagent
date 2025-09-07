const promptInput = document.getElementById("prompt");
const swarmModeCheckbox = document.getElementById("swarmMode");
const analyzeBtn = document.getElementById("analyzeBtn");
const loading = document.getElementById("loading");
const results = document.getElementById("results");
const humanInput = document.getElementById("humanInput");
const humanPrompt = document.getElementById("humanPrompt");
const humanResponse = document.getElementById("humanResponse");
const submitResponse = document.getElementById("submitResponse");
const cancelHandoff = document.getElementById("cancelHandoff");

const AGENT_URL = "http://localhost:8080/invocations";

let currentConversationId = null;

analyzeBtn.addEventListener("click", analyzeVulnerabilities);
submitResponse.addEventListener("click", submitHumanResponse);
cancelHandoff.addEventListener("click", cancelHumanHandoff);

async function analyzeVulnerabilities() {
  const prompt = promptInput.value.trim();
  if (!prompt) {
    alert("Please enter a prompt");
    return;
  }

  showLoading();

  try {
    const response = await fetch(AGENT_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt: prompt,
        swarm_mode: swarmModeCheckbox.checked,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const rawData = await response.text();

    let jsonData;
    if (rawData.startsWith('"') && rawData.endsWith('"')) {
      // Response is JSON-wrapped string, extract and parse the Python dict
      const pythonString = JSON.parse(rawData);
      jsonData = extractContent(pythonString);
    } else {
      // Direct Python dict string
      jsonData = extractContent(rawData);
    }

    handleResponse(jsonData);
  } catch (error) {
    console.error("Error:", error);
    displayError(error.message);
  } finally {
    hideLoading();
  }
}

function extractContent(data) {
  const agents = {};

  // Extract gather_phase - handle both empty [] and with content
  const gatherMatch = data.match(
    /'gather_phase':\s*{[^}]*'content':\s*(\[[^\]]*\])/s
  );

  if (gatherMatch) {
    const contentStr = gatherMatch[1];
    if (contentStr === "[]") {
      agents.gather_phase = { content: [] };
    } else {
      const textMatch = contentStr.match(
        /'text':\s*(['"])((?:(?!\1)[^\\]|\\.)*)(\1)/s
      );
      if (textMatch) {
        const quote = textMatch[1];
        const text = textMatch[2];
        const unescapedText =
          quote === '"'
            ? text.replace(/\\n/g, "\n").replace(/\\"/g, '"')
            : text.replace(/\\n/g, "\n").replace(/\\'/g, "'");
        agents.gather_phase = {
          content: [{ text: unescapedText }],
        };
      }
    }
  }

  // Extract vuln_remediator - handle both empty [] and with content
  const remediatorMatch = data.match(
    /'vuln_remediator':[^{]*'content':\s*(\[[^\]]*\])/s
  );
  if (remediatorMatch) {
    const contentStr = remediatorMatch[1];
    if (contentStr === "[]") {
      agents.vuln_remediator = { result: { message: { content: [] } } };
    } else {
      const textMatch = contentStr.match(
        /'text':\s*(['"])((?:(?!\1)[^\\]|\\.)*)(\1)/s
      );
      if (textMatch) {
        agents.vuln_remediator = {
          result: {
            message: {
              content: [
                {
                  text: textMatch[1].replace(/\\n/g, "\n").replace(/\\"/g, '"'),
                },
              ],
            },
          },
        };
      }
    }
  }

  // Extract vuln_keeper - handle both empty [] and with content
  const keeperMatch = data.match(
    /'vuln_keeper':[^{]*'content':\s*(\[[^\]]*\])/s
  );
  if (keeperMatch) {
    const contentStr = keeperMatch[1];
    if (contentStr === "[]") {
      agents.vuln_keeper = { result: { message: { content: [] } } };
    } else {
      const textMatch = contentStr.match(
        /'text':\s*(['"])((?:(?!\1)[^\\]|\\.)*)(\1)/s
      );
      if (textMatch) {
        agents.vuln_keeper = {
          result: {
            message: {
              content: [
                {
                  text: textMatch[1].replace(/\\n/g, "\n").replace(/\\"/g, '"'),
                },
              ],
            },
          },
        };
      }
    }
  }

  const statusMatch = data.match(/'status':\s*'([^']+)'/);

  return {
    result: {
      ...agents,
      swarm_remediation: {
        results: agents,
        status: statusMatch ? statusMatch[1] : null,
      },
      status: statusMatch ? statusMatch[1] : null,
    },
  };
}

async function submitHumanResponse() {
  const decision = document.querySelector(
    'input[name="decision"]:checked'
  ).value;

  const prompt = `Human has chosen to ${decision} the remediation plan`;

  showLoading();
  hideHumanInput();

  try {
    const apiResponse = await fetch(AGENT_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt: prompt,
        human_response: decision,
        conversation_id: currentConversationId,
        swarm_mode: swarmModeCheckbox.checked,
      }),
    });

    if (!apiResponse.ok) {
      throw new Error(`HTTP error! status: ${apiResponse.status}`);
    }

    const rawData = await apiResponse.text();

    let data;
    if (rawData.startsWith('"') && rawData.endsWith('"')) {
      // Response is JSON-wrapped string, extract and parse the Python dict
      const pythonString = JSON.parse(rawData);
      data = extractContent(pythonString);
    } else {
      // Direct Python dict string
      data = extractContent(rawData);
    }
    handleResponse(data);
  } catch (error) {
    console.error("Error:", error);
    displayError(error.message);
  } finally {
    hideLoading();
  }
}

function cancelHumanHandoff() {
  hideHumanInput();
  displayError("Human handoff cancelled by user");
}

function handleResponse(data) {
  if (data.error) {
    displayError(data.error);
    return;
  }

  const result = data.result;

  // Check if human input is required
  if (result && result.status === "awaiting_human_input") {
    // Check if we have meaningful content from any agent
    const hasContent =
      result.gather_phase?.content?.[0]?.text ||
      result.swarm_remediation?.results?.vuln_remediator?.result?.message
        ?.content?.[0]?.text ||
      result.swarm_remediation?.results?.vuln_keeper?.result?.message
        ?.content?.[0]?.text ||
      result.swarm_remediation?.results?.vuln_critic?.result?.message
        ?.content?.[0]?.text;

    if (hasContent) {
      showHumanInput(
        result.human_prompt || "Please provide your input:",
        result.conversation_id
      );
      displayResults(data); // Show partial results
      return;
    } else {
      // No meaningful content, treat as completed
      console.log("=== NO CONTENT AVAILABLE, TREATING AS COMPLETED ===");
      result.status = "completed";
    }
  }

  console.log("=== CALLING DISPLAY RESULTS ===");
  // Normal result display
  displayResults(data);
}

function showHumanInput(prompt, conversationId) {
  currentConversationId = conversationId;
  humanPrompt.textContent = prompt;
  humanInput.classList.remove("hidden");
}

function hideHumanInput() {
  humanInput.classList.add("hidden");
  currentConversationId = null;
}

function showLoading() {
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";
  loading.classList.remove("hidden");
  results.classList.add("hidden");
  humanInput.classList.add("hidden");
}

function hideLoading() {
  analyzeBtn.disabled = false;
  analyzeBtn.textContent = "Analyze";
  loading.classList.add("hidden");
}

function displayResults(data) {
  results.innerHTML = "";

  if (data.error) {
    displayError(data.error);
    return;
  }

  const result = data.result;

  if (
    swarmModeCheckbox.checked &&
    result &&
    (result.swarm_remediation || result.gather_phase)
  ) {
    displaySwarmResults(result);
  } else {
    displaySingleAgentResults(result);
  }

  results.classList.remove("hidden");
}

function displaySingleAgentResults(result) {
  const section = createResultSection(
    "Vulnerability Analysis",
    extractText(result)
  );
  results.appendChild(section);
}

function displaySwarmResults(result) {
  console.log("=== FULL RESULT OBJECT ===");
  console.log(JSON.stringify(result, null, 2));
  console.log("=== GATHER PHASE ===");
  console.log("result.gather_phase:", result.gather_phase);
  console.log("=== SWARM REMEDIATION ===");
  console.log("result.swarm_remediation:", result.swarm_remediation);

  // Gather Phase
  if (result.gather_phase) {
    const title =
      result.status === "completed"
        ? "Remediation Results"
        : "Remediation Plan";
    const gatherSection = createResultSection(
      title,
      extractText(result.gather_phase)
    );
    results.appendChild(gatherSection);
  }

  // Swarm Results
  if (result.swarm_remediation) {
    const swarmData = result.swarm_remediation;

    // Show any agents that provided meaningful output
    if (swarmData.results) {
      Object.entries(swarmData.results).forEach(([agentName, agentResult]) => {
        const agentMessage = agentResult.result;
        if (
          agentMessage &&
          agentMessage.message &&
          agentMessage.message.content &&
          agentMessage.message.content.length > 0
        ) {
          const title = `${
            agentName.charAt(0).toUpperCase() + agentName.slice(1)
          } Analysis`;
          const content = extractText(agentMessage);
          const section = createResultSection(title, content);
          results.appendChild(section);
        }
      });
    }

    // Status indicator for human input
    if (result.status === "awaiting_human_input") {
      const statusSection = createResultSection(
        "Human Review Required",
        "The swarm has completed its analysis. Please review the findings and provide your feedback or approval to proceed."
      );
      results.appendChild(statusSection);
    }
  }
}

function createResultSection(title, content) {
  const section = document.createElement("div");
  section.className = "result-section";

  const heading = document.createElement("h3");
  heading.textContent = title;

  const contentDiv = document.createElement("div");
  contentDiv.className = "result-content";
  contentDiv.textContent = content;

  section.appendChild(heading);
  section.appendChild(contentDiv);

  return section;
}

function extractText(messageObj) {
  console.log("extractText called with:", messageObj);

  if (typeof messageObj === "string") {
    console.log("Returning string:", messageObj);
    return messageObj;
  }

  // Handle undefined/null
  if (!messageObj) {
    console.log("messageObj is null/undefined");
    return "No content available";
  }

  // Handle direct text content
  if (messageObj?.text) {
    console.log("Found direct text:", messageObj.text);
    return messageObj.text;
  }

  // Handle role/content structure with empty content array
  if (messageObj?.role === "assistant" && Array.isArray(messageObj?.content)) {
    if (messageObj.content.length === 0) {
      console.log("Found empty content array");
      return "No content provided by this agent";
    }
    if (messageObj.content[0]?.text) {
      console.log(
        "Found role assistant with content:",
        messageObj.content[0].text
      );
      return messageObj.content[0].text;
    }
  }

  // Handle nested message structures - try all possible paths
  if (messageObj?.result?.message?.content?.[0]?.text) {
    console.log(
      "Found result.message.content[0].text:",
      messageObj.result.message.content[0].text
    );
    return messageObj.result.message.content[0].text;
  }

  if (messageObj?.message?.content?.[0]?.text) {
    console.log(
      "Found message.content[0].text:",
      messageObj.message.content[0].text
    );
    return messageObj.message.content[0].text;
  }

  if (messageObj?.content?.[0]?.text) {
    console.log("Found content[0].text:", messageObj.content[0].text);
    return messageObj.content[0].text;
  }

  // Handle array of content
  if (Array.isArray(messageObj?.content)) {
    console.log("Found content array:", messageObj.content);
    if (messageObj.content.length === 0) {
      console.log("Content array is empty");
      return "No content available";
    }
    const result = messageObj.content
      .map((item) => item.text || item)
      .join("\n");
    console.log("Mapped content array to:", result);
    return result;
  }

  // Last resort - convert to readable string
  if (typeof messageObj === "object") {
    console.log("Converting object to JSON string");
    return JSON.stringify(messageObj, null, 2);
  }

  console.log("Returning string conversion:", String(messageObj));
  return String(messageObj);
}

function displayError(message) {
  results.innerHTML = `
        <div class="error">
            <strong>Error:</strong> ${message}
        </div>
    `;
  results.classList.remove("hidden");
}
