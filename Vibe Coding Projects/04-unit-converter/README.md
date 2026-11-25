# Unit Converter

A simple converter for **length**, **weight** and **temperature**, made with plain HTML, CSS and JavaScript. It has no frameworks and no build step.

**▶ Try it:** https://dcalabuig7.github.io/Vibe%20Coding%20Projects/04-unit-converter/

## What it does

- Converts between units in 3 categories:
  - **Length:** metres, kilometres, centimetres, millimetres, miles, yards, feet, inches
  - **Weight:** kilograms, grams, milligrams, pounds, ounces
  - **Temperature:** Celsius, Fahrenheit, Kelvin
- The result updates live as you type.
- A **⇄** button swaps the "From" and "To" units.
- Works on phones as well as computers.

## How to run it

1. Download or clone this repository.
2. Open the `04-unit-converter` folder.
3. Double-click `index.html`. It opens in your browser, and that's it.

## How it works (the simple version)

Think of the page as a **restaurant**:

| File | Restaurant part | What it does |
|------|-----------------|--------------|
| `index.html` | The **furniture** | It puts the menus, the number box, the ⇄ button and the answer box on the page. |
| `style.css` | The **decoration** | Colours, rounded corners and spacing. On a phone it stacks the boxes. |
| `script.js` | The **cook** | It does the work: reads what you typed, does the maths and writes the answer. |

**What the cook (`script.js`) does, step by step:**

1. **It keeps a list of sizes.** Every unit has one number: its size in metres (for length) or kilograms (for weight). For example, 1 km is 1000 metres, and 1 foot is 0.3048 metres.
2. **It waits for you.** "Event listeners" are like a bell: when you type, pick a unit or click ⇄, the bell rings and the `convert()` function runs.
3. **It converts in two steps:** first into the base unit (metres or kilograms), then from the base unit into the unit you want.
   - Example: 2 km to cm → 2 × 1000 = 2000 metres → 2000 ÷ 0.01 = **200,000 cm**
   - In code that's one line:

     ```
     result = value * fromFactor / toFactor
     ```
4. **Temperature is the exception.** 0 °C is not 0 °F, so a single multiplier can't work. Instead it always goes **to Celsius first, then to the target unit**. Same idea: always pass through one middle unit.
5. **It writes the answer** in the result box. If the box is empty, it shows a hint instead.

That's the whole program: **data → wait for a change → calculate → show the result.**

## Test it

| Category | Input | Expected result |
|----------|-------|-----------------|
| Length | 1 mi → km | 1.609344 |
| Length | 10 ft → m | 3.048 |
| Length | 12 in → cm | 30.48 |
| Weight | 1 kg → lb | 2.2046226 |
| Weight | 16 oz → lb | 1 |
| Temperature | 100 °C → °F | 212 |
| Temperature | 98.6 °F → °C | 37 |
| Temperature | -40 °C → °F | -40 (the two scales meet here) |
| Empty box | (delete the number) | "Type a number to convert." |

## What I learned

- How to **read input** from a page and **show output** with `getElementById` and `textContent`.
- How **event listeners** make a page react to typing, clicking and choosing from a menu.
- How to **store data in objects** (the unit factors) instead of writing one `if` for every pair of units.
- Why temperature needs **its own function**, and how to go through one shared unit (Celsius).
- How to handle **edge cases**, like an empty input box.
- Why computers sometimes give answers like `0.30000000000000004`, and how to round them for display.
- How to make a layout **responsive** with a CSS media query.

## Check yourself

1. In `script.js`, `1 km` has the number `1000` and `1 cm` has `0.01`. Using `value * fromFactor / toFactor`, what's the result for **5 km → cm**, and why do we **multiply** first and then **divide**?
2. Why can't temperature just use a number in the `factors` list like length does? *(Hint: what is 0 °C in °F?)*
3. The number box has an `"input"` event listener. What would change for the user if we removed that line and kept only a "Convert" button?
