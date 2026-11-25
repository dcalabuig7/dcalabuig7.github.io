// ===== 1. THE DATA =====
// For length and weight, every unit has one number: how big it is
// compared to a "base unit" (metres for length, kilograms for weight).
// Example: 1 km = 1000 metres, so km is 1000.
const factors = {
  length: {
    m: 1,
    km: 1000,
    cm: 0.01,
    mm: 0.001,
    mi: 1609.344,
    yd: 0.9144,
    ft: 0.3048,
    in: 0.0254,
  },
  weight: {
    kg: 1,
    g: 0.001,
    mg: 0.000001,
    lb: 0.45359237,
    oz: 0.028349523125,
  },
};

// The names people see in the dropdown menus
const unitNames = {
  length: {
    m: "Metres (m)",
    km: "Kilometres (km)",
    cm: "Centimetres (cm)",
    mm: "Millimetres (mm)",
    mi: "Miles (mi)",
    yd: "Yards (yd)",
    ft: "Feet (ft)",
    in: "Inches (in)",
  },
  weight: {
    kg: "Kilograms (kg)",
    g: "Grams (g)",
    mg: "Milligrams (mg)",
    lb: "Pounds (lb)",
    oz: "Ounces (oz)",
  },
  temperature: {
    C: "Celsius (°C)",
    F: "Fahrenheit (°F)",
    K: "Kelvin (K)",
  },
};

// ===== 2. FIND THE HTML ELEMENTS =====
// We grab each element once by its id, so we can read and change it later.
const categoryMenu = document.getElementById("category");
const amountBox = document.getElementById("amount");
const fromMenu = document.getElementById("from-unit");
const toMenu = document.getElementById("to-unit");
const swapButton = document.getElementById("swap");
const resultText = document.getElementById("result");

// ===== 3. FILL THE UNIT MENUS =====
// Puts the right units in the "From" and "To" menus for the chosen category.
function fillUnitMenus() {
  const category = categoryMenu.value;     // e.g. "length"
  const names = unitNames[category];       // e.g. { m: "Metres (m)", ... }

  // Empty both menus first
  fromMenu.innerHTML = "";
  toMenu.innerHTML = "";

  // Add one <option> per unit to each menu
  for (const key in names) {
    fromMenu.add(new Option(names[key], key));
    toMenu.add(new Option(names[key], key));
  }

  // Start with the 1st unit in "From" and the 2nd unit in "To"
  fromMenu.selectedIndex = 0;
  toMenu.selectedIndex = 1;
}

// ===== 4. TEMPERATURE (special case) =====
// Temperatures can't use a single multiplier, because the scales
// start at different zero points. So we always go through Celsius:
// first turn the value into °C, then turn °C into the target unit.
function convertTemperature(value, from, to) {
  // Step 1: change the value to Celsius
  let celsius;
  if (from === "C") {
    celsius = value;
  } else if (from === "F") {
    celsius = (value - 32) * 5 / 9;
  } else {
    celsius = value - 273.15;              // from Kelvin
  }

  // Step 2: change Celsius to the target unit
  if (to === "C") {
    return celsius;
  } else if (to === "F") {
    return celsius * 9 / 5 + 32;
  } else {
    return celsius + 273.15;               // to Kelvin
  }
}

// ===== 5. THE MAIN CONVERSION =====
// Runs every time something changes. Reads the inputs, calculates, shows the answer.
function convert() {
  const category = categoryMenu.value;
  const from = fromMenu.value;
  const to = toMenu.value;

  // If the box is empty, show a hint instead of a result
  if (amountBox.value === "") {
    showMessage("Type a number to convert.");
    return;
  }

  // The input box always gives text, so turn it into a real number
  const value = Number(amountBox.value);

  let result;
  if (category === "temperature") {
    result = convertTemperature(value, from, to);
  } else {
    // Go to the base unit (multiply), then out to the target unit (divide).
    // Example: 2 km to m  ->  2 * 1000 / 1 = 2000
    result = value * factors[category][from] / factors[category][to];
  }

  // Show the answer, e.g. "1 km = 1000 m"
  resultText.className = "result";
  resultText.textContent = `${value} ${from} = ${formatNumber(result)} ${to}`;
}

// Shows a grey message in the result box (used for the empty box case)
function showMessage(message) {
  resultText.className = "result error";
  resultText.textContent = message;
}

// Computers store some decimals slightly wrong (0.1 + 0.2 = 0.30000000000000004).
// Keeping 8 significant digits hides that, and Number() drops extra zeros.
function formatNumber(number) {
  return Number(number.toPrecision(8));
}

// ===== 6. SWAP BUTTON =====
// Exchanges the "From" and "To" units, then converts again.
function swapUnits() {
  const oldFrom = fromMenu.value;
  fromMenu.value = toMenu.value;
  toMenu.value = oldFrom;
  convert();
}

// ===== 7. LISTEN FOR CHANGES =====
// "Event listeners" tell the browser: when THIS happens, run THAT function.
categoryMenu.addEventListener("change", function () {
  fillUnitMenus();   // new category = new list of units
  convert();
});
amountBox.addEventListener("input", convert);   // every key you type
fromMenu.addEventListener("change", convert);
toMenu.addEventListener("change", convert);
swapButton.addEventListener("click", swapUnits);

// ===== 8. START =====
// Set up the page once when it first loads.
fillUnitMenus();
convert();
