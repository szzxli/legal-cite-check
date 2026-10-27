// Node test for web/extract.js. No network. Run: node web/tests/test_extract.js
const assert = require("assert");
const fs = require("fs");
const path = require("path");
// Load extract.js source and eval the REPORTERS block + function in this context.
const src = fs.readFileSync(path.join(__dirname, "..", "extract.js"), "utf8");
const fnSrc = src.replace(/if \(typeof module[\s\S]*$/, "");
eval(fnSrc); // defines REPORTERS, extractCitations
assert.ok(Array.isArray(REPORTERS) && REPORTERS.length >= 10, "reporters table present");
const cases = extractCitations(
  "Obergefell v. Hodges, 576 U.S. 644 (2015). See also 616 S.W.3d 389 and 718 F. App'x 84.");
assert.strictEqual(cases.length, 3, JSON.stringify(cases));
assert.strictEqual(cases[0].text, "576 U.S. 644");
assert.strictEqual(cases[0].caseName, "Obergefell v. Hodges");
assert.strictEqual(cases[0].year, "2015");
assert.strictEqual(cases[0].manualUrl, "https://www.courtlistener.com/c/us/576/644/");
assert.strictEqual(cases[1].manualUrl, "https://www.courtlistener.com/c/sw3d/616/389/");
assert.strictEqual(cases[2].manualUrl, "https://www.courtlistener.com/c/f-appx/718/84/");
const signal = extractCitations("See Brown v. Board of Education, 347 U.S. 483 (1954).");
assert.strictEqual(signal[0].caseName, "Brown v. Board of Education");
assert.ok(!/fetch\(|XMLHttpRequest/.test(src), "extract.js must not call the network");
console.log("web extract tests passed");
