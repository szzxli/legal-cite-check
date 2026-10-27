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

// A year is attributed only from this citation's own parenthetical.
// A "(YYYY)" that belongs to the next citation, even within the old
// ~60-character lookahead, must not be borrowed — and the case name must
// not keep a signal or sentence-start word.
const leaked = extractCitations(
  "Smith v. Jones, 123 F.3d 456. Also Brown v. Board of Education, 347 U.S. 483 (1954).");
assert.strictEqual(leaked.length, 2, JSON.stringify(leaked));
assert.strictEqual(leaked[0].text, "123 F.3d 456");
assert.strictEqual(leaked[0].caseName, "Smith v. Jones");
assert.strictEqual(leaked[0].year, null, "no year of its own; got " + leaked[0].year);
assert.strictEqual(leaked[1].caseName, "Brown v. Board of Education");
assert.strictEqual(leaked[1].year, "1954");
const again = extractCitations(
  "Smith v. Jones, 123 F.3d 456. Again Roe v. Wade, 410 U.S. 113 (1973).");
assert.strictEqual(again[0].year, null);
assert.strictEqual(again[1].caseName, "Roe v. Wade");
assert.strictEqual(again[1].year, "1973");
const followed = extractCitations("See 347 U.S. 483, 576 U.S. 644 (2015).");
assert.strictEqual(followed[0].year, null, "year after the next cite is not this cite's");
assert.strictEqual(followed[0].pinCite, null);
assert.strictEqual(followed[1].year, "2015");

// Signal and transition words directly before the case name.
for (const [text, name] of [
  ["Also Brown v. Board of Education, 347 U.S. 483 (1954).", "Brown v. Board of Education"],
  ["Again Roe v. Wade, 410 U.S. 113 (1973).", "Roe v. Wade"],
  ["But Smith v. Jones, 123 F.3d 456 (2020).", "Smith v. Jones"],
  ["Accord Miranda v. Arizona, 384 U.S. 436 (1966).", "Miranda v. Arizona"],
  ["See also Brown v. Board of Education, 347 U.S. 483 (1954).", "Brown v. Board of Education"],
  ["Cf. Roe v. Wade, 410 U.S. 113 (1973).", "Roe v. Wade"],
  ["But cf. Smith v. Jones, 123 F.3d 456 (2020).", "Smith v. Jones"],
  ["Under Brown v. Board of Education, 347 U.S. 483 (1954).", "Brown v. Board of Education"],
  ["And United States v. Nixon, 418 U.S. 683 (1974).", "United States v. Nixon"],
]) {
  const found = extractCitations(text);
  assert.strictEqual(found[0].caseName, name, text + " -> " + found[0].caseName);
}

// Guards: ordinary cites, pin cites, court/year parentheticals, and
// multi-word party names must keep working. A party that is only a
// signal word is not erased.
const normal = extractCitations("Obergefell v. Hodges, 576 U.S. 644 (2015).");
assert.strictEqual(normal[0].caseName, "Obergefell v. Hodges");
assert.strictEqual(normal[0].year, "2015");
assert.strictEqual(normal[0].pinCite, null);
const pin = extractCitations("Obergefell v. Hodges, 576 U.S. 644, 650 (2015).");
assert.strictEqual(pin[0].pinCite, "650");
assert.strictEqual(pin[0].year, "2015");
const pinRange = extractCitations("Brown v. Board of Education, 347 U.S. 483, 490-492 (1954).");
assert.strictEqual(pinRange[0].pinCite, "490\u2013492");
assert.strictEqual(pinRange[0].year, "1954");
const court = extractCitations("Smith v. Jones, 123 F.3d 456 (9th Cir. 2020).");
assert.strictEqual(court[0].caseName, "Smith v. Jones");
assert.strictEqual(court[0].year, "2020");
const courtPin = extractCitations("Hunt v. Smith, 670 S.W.2d 248, 250 (Ky. App. 1984).");
assert.strictEqual(courtPin[0].pinCite, "250");
assert.strictEqual(courtPin[0].year, "1984");
const united = extractCitations("United States v. Nixon, 418 U.S. 683 (1974).");
assert.strictEqual(united[0].caseName, "United States v. Nixon");
assert.strictEqual(united[0].year, "1974");
const board = extractCitations("Board of Regents v. Roth, 408 U.S. 564 (1972).");
assert.strictEqual(board[0].caseName, "Board of Regents v. Roth");
assert.strictEqual(board[0].year, "1972");
const indiana = extractCitations("Indiana v. Edwards, 554 U.S. 164 (2008).");
assert.strictEqual(indiana[0].caseName, "Indiana v. Edwards");
const butz = extractCitations("Butz v. Economou, 438 U.S. 478 (1978).");
assert.strictEqual(butz[0].caseName, "Butz v. Economou");
const seeParty = extractCitations("See v. City of Seattle, 100 P.2d 200 (1940).");
assert.strictEqual(seeParty[0].caseName, "See v. City of Seattle");
assert.strictEqual(seeParty[0].year, "1940");

assert.ok(!/fetch\(|XMLHttpRequest/.test(src), "extract.js must not call the network");
console.log("web extract tests passed");
