const board = document.querySelector("#board");
const pathLayer = document.querySelector("#pathLayer");
const form = document.querySelector("#controlForm");
const startButton = document.querySelector("#startButton");
const stopButton = document.querySelector("#stopButton");
const statusText = document.querySelector("#statusText");
const trajectoryList = document.querySelector("#trajectoryList");
const routeSummary = document.querySelector("#routeSummary");

const metrics = {
  generation: document.querySelector("#metricGeneration"),
  valid: document.querySelector("#metricValid"),
  invalid: document.querySelector("#metricInvalid"),
  unique: document.querySelector("#metricUnique"),
  fitness: document.querySelector("#metricFitness"),
  time: document.querySelector("#metricTime"),
};

let eventSource = null;
let latestState = null;

function createBoard() {
  const files = ["a", "b", "c", "d", "e", "f", "g", "h"];
  for (let row = 0; row < 8; row += 1) {
    for (let col = 0; col < 8; col += 1) {
      const index = row * 8 + col;
      const cell = document.createElement("div");
      cell.className = `cell ${(row + col) % 2 === 0 ? "light" : "dark"}`;
      cell.dataset.index = String(index);
      cell.innerHTML = `<span class="coord">${files[col]}${8 - row}</span>`;
      board.appendChild(cell);
    }
  }
}

function updateRangeLabels() {
  form.querySelectorAll("input[type='range']").forEach((input) => {
    const outputId = input.dataset.output;
    const output = document.querySelector(`#${outputId}`);
    if (output) {
      output.textContent = `${Math.round(Number(input.value) * 100)}%`;
    }
  });
}

function resetCell(cell) {
  const coord = cell.querySelector(".coord")?.outerHTML ?? "";
  cell.classList.remove("start", "end");
  cell.innerHTML = coord;
}

function centerOfCell(index) {
  const cell = board.querySelector(`[data-index='${index}']`);
  if (!cell) {
    return { x: 0, y: 0 };
  }

  const boardRect = board.getBoundingClientRect();
  const cellRect = cell.getBoundingClientRect();

  return {
    x: cellRect.left - boardRect.left + cellRect.width / 2,
    y: cellRect.top - boardRect.top + cellRect.height / 2,
  };
}

function drawPath(route, invalidEdges) {
  pathLayer.replaceChildren();
  if (route.length < 2) {
    return;
  }

  const bounds = board.getBoundingClientRect();
  pathLayer.setAttribute("viewBox", `0 0 ${bounds.width} ${bounds.height}`);

  const invalidSet = new Set(invalidEdges);
  for (let step = 0; step < route.length - 1; step += 1) {
    const origin = centerOfCell(route[step].index);
    const destination = centerOfCell(route[step + 1].index);
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", origin.x);
    line.setAttribute("y1", origin.y);
    line.setAttribute("x2", destination.x);
    line.setAttribute("y2", destination.y);
    line.classList.add("path-segment");
    if (invalidSet.has(step)) {
      line.classList.add("invalid");
    }
    pathLayer.appendChild(line);
  }
}

function renderBoard(state) {
  board.querySelectorAll(".cell").forEach(resetCell);

  state.route.forEach((square, position) => {
    const cell = board.querySelector(`[data-index='${square.index}']`);
    if (!cell) {
      return;
    }

    if (position === 0) {
      cell.classList.add("start");
    }
    if (position === state.route.length - 1) {
      cell.classList.add("end");
    }

    const marker = document.createElement("span");
    marker.className = "step-marker";
    marker.textContent = String(position + 1);
    cell.appendChild(marker);
  });

  drawPath(state.route, state.invalid_edges);
}

function renderTrajectory(state) {
  trajectoryList.replaceChildren();
  const invalidTargets = new Set(state.invalid_edges.map((edge) => edge + 1));

  state.route.forEach((square, position) => {
    const item = document.createElement("li");
    item.textContent = square.label;
    if (invalidTargets.has(position)) {
      item.classList.add("invalid");
      item.title = "Movimento anterior inválido";
    }
    trajectoryList.appendChild(item);
  });

  if (state.complete) {
    routeSummary.textContent = "64 casas, 63 movimentos válidos";
  } else {
    routeSummary.textContent = `${state.unique_squares} casas únicas, ${state.valid_moves}/63 movimentos válidos`;
  }
}

function renderMetrics(state) {
  metrics.generation.textContent = state.generation;
  metrics.valid.textContent = `${state.valid_moves}/63`;
  metrics.invalid.textContent = state.invalid_moves;
  metrics.unique.textContent = `${state.unique_squares}/64`;
  metrics.fitness.textContent = state.fitness;
  metrics.time.textContent = `${state.elapsed_seconds}s`;
}

function renderState(state) {
  latestState = state;
  renderBoard(state);
  renderTrajectory(state);
  renderMetrics(state);
}

function setRunning(isRunning) {
  startButton.disabled = isRunning;
  stopButton.disabled = !isRunning;
}

function stopRun(message = "Interrompido") {
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  setRunning(false);
  statusText.textContent = message;
}

function paramsFromForm() {
  const data = new FormData(form);
  const params = new URLSearchParams();
  for (const [key, value] of data.entries()) {
    if (key !== "warmStart") {
      params.set(key, value);
    }
  }
  params.set("warmStart", form.elements.warmStart.checked ? "1" : "0");
  params.set("reportEvery", "5");
  return params;
}

function startRun(event) {
  event.preventDefault();
  stopRun("Reiniciando");

  const params = paramsFromForm();
  eventSource = new EventSource(`/api/run?${params.toString()}`);
  setRunning(true);
  statusText.textContent = "Executando";

  eventSource.addEventListener("progress", (message) => {
    const state = JSON.parse(message.data);
    renderState(state);
    statusText.textContent = `Geração ${state.generation}`;
  });

  eventSource.addEventListener("done", (message) => {
    const state = JSON.parse(message.data);
    renderState(state);
    const finished = state.reason === "solution" ? "Solução encontrada" : "Limite atingido";
    stopRun(finished);
  });

  eventSource.onerror = () => {
    if (eventSource) {
      stopRun("Conexão encerrada");
    }
  };
}

form.addEventListener("input", updateRangeLabels);
form.addEventListener("submit", startRun);
stopButton.addEventListener("click", () => stopRun());
window.addEventListener("resize", () => {
  if (latestState) {
    drawPath(latestState.route, latestState.invalid_edges);
  }
});

createBoard();
updateRangeLabels();
