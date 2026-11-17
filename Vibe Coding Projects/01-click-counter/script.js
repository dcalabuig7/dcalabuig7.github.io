// 1. Grab the elements we need from the page
const countEl = document.getElementById("count");
const increaseBtn = document.getElementById("increase");
const decreaseBtn = document.getElementById("decrease");
const resetBtn = document.getElementById("reset");

// 2. Load the saved count (or start at 0)
let count = 0;
try {
  count = Number(localStorage.getItem("count")) || 0;
} catch (e) {
  // Storage can be blocked (e.g. private browsing) — just start at 0
}

// 3. Show the number on screen, color it, and save it
function updateDisplay() {
  countEl.textContent = count;
  countEl.classList.toggle("positive", count > 0);
  countEl.classList.toggle("negative", count < 0);

  // Small "bump" animation
  countEl.classList.add("bump");
  setTimeout(() => countEl.classList.remove("bump"), 100);

  try {
    localStorage.setItem("count", count);
  } catch (e) {}
}

// 4. React to button clicks
increaseBtn.addEventListener("click", () => {
  count++;
  updateDisplay();
});

decreaseBtn.addEventListener("click", () => {
  count--;
  updateDisplay();
});

resetBtn.addEventListener("click", () => {
  count = 0;
  updateDisplay();
});

// 5. Bonus: keyboard shortcuts
document.addEventListener("keydown", (event) => {
  if (event.key === "ArrowUp") increaseBtn.click();
  if (event.key === "ArrowDown") decreaseBtn.click();
});

updateDisplay();
