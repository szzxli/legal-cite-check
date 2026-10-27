/* Browser UI (v2). Citation extraction stays local: the checker makes NO
   network calls. The translation viewer is OFF by default: it only calls
   a user-supplied LibreTranslate-compatible endpoint, and with no endpoint
   it shows an explanation instead of inventing a translation. */
var currentLang = "en";
function T() { return I18N[currentLang] || I18N.en; }
function esc(s) {
  return String(s || "").replace(/[&<>\"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
  });
}

function setLang(lang) {
  if (!I18N[lang]) return;
  currentLang = lang;
  document.documentElement.lang = lang;
  document.title = T().pageTitle;
  document.querySelectorAll("[data-i18n]").forEach(function (el) {
    el.textContent = T()[el.getAttribute("data-i18n")];
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
    el.placeholder = T()[el.getAttribute("data-i18n-placeholder")];
  });
  var sel = document.getElementById("lang");
  if (sel) sel.value = lang;
  if (window.__lastResults) render(window.__lastResults);
  if (window.__transRows) renderTrans(window.__transRows);
}

function render(results) {
  var tbody = document.getElementById("results");
  tbody.innerHTML = "";
  results.forEach(function (r, i) {
    var tr = document.createElement("tr");
    tr.innerHTML = "<td>" + (i + 1) + "</td><td>" + esc(r.text) + "</td>"
      + "<td>" + esc(r.caseName) + "</td><td>NOT_CHECKED</td>"
      + "<td><a href=\"" + esc(r.manualUrl) + "\" target=\"_blank\" rel=\"noopener\">"
      + esc(T().openCourtListener) + "</a>"
      + " | <a href=\"" + esc(r.scholarUrl) + "\" target=\"_blank\" rel=\"noopener\">"
      + esc(T().searchScholar) + "</a></td>";
    tbody.appendChild(tr);
  });
  document.getElementById("count").textContent =
    T().countFound.replace("{n}", results.length);
  window.__lastResults = results;
}

function showQueryPanel(original, english, status) {
  var orig = document.getElementById("origQuery");
  var en = document.getElementById("enQuery");
  var st = document.getElementById("queryStatus");
  if (orig) orig.textContent = original;
  if (en) en.value = english || "";
  if (st) st.textContent = status || "";
  window.__lastQuery = { original: original, english: english || "" };
}

/* Search flow (v2 query auto-translation): on a non-English UI, clicking
   search automatically translates the query to English and searches the
   English query -- the user never has to translate by hand. The original
   and the English query are both shown, and the English query is editable
   for a manual re-search. Citation-format content (volumes, pages,
   reporter abbreviations) and numbers are masked before translation and
   restored verbatim. With no endpoint, or on translation failure, NO
   English query is generated and NO English search is claimed: extraction
   below runs on the original query only, and the status says so. */
async function check() {
  var text = document.getElementById("input").value || "";
  if (currentLang === "en") {
    showQueryPanel(text, text, T().queryEnglishNote);
    render(extractCitations(text));
    return;
  }
  var endpoint = "";
  var mt = document.getElementById("mtEndpoint");
  if (mt) endpoint = (mt.value || "").trim();
  if (!endpoint) {
    showQueryPanel(text, "", T().queryNoEndpoint);
    render(extractCitations(text));
    return;
  }
  var rows = await translateParagraphs([text],
    { endpoint: endpoint, source: currentLang, target: "en" });
  if (!rows[0] || rows[0].error || rows[0].translation == null) {
    showQueryPanel(text, "", T().queryTranslateFailed);
    render(extractCitations(text));
    return;
  }
  showQueryPanel(text, rows[0].translation, T().queryTranslatedNote);
  render(extractCitations(rows[0].translation));
}

function searchEnQuery() {
  var q = (document.getElementById("enQuery").value || "");
  if (!q.trim()) return;
  render(extractCitations(q));
  var st = document.getElementById("queryStatus");
  if (st) st.textContent = T().queryEditedSearch;
}

function openFile(input) {
  var file = input.files && input.files[0];
  if (!file) return;
  var reader = new FileReader();
  reader.onload = function () {
    document.getElementById("input").value = reader.result || "";
    check();
  };
  reader.readAsText(file);
}

function exportMarkdown() {
  var results = window.__lastResults || [];
  var lines = ["> **" + I18N.en.disclaimer + "**"];
  if (currentLang !== "en") lines.push("> " + T().disclaimerNote);
  lines.push("");
  results.forEach(function (r) {
    lines.push("- [ ] NOT_CHECKED \u2014 " + r.text
      + (r.caseName ? " (" + r.caseName + ")" : "")
      + " \u2014 " + r.manualUrl);
  });
  navigator.clipboard.writeText(lines.join("\n")).then(function () {
    document.getElementById("count").textContent = T().copied;
  });
}

function exportJson() {
  var blob = new Blob([JSON.stringify(window.__lastResults || [], null, 2)],
    { type: "application/json" });
  var a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "legal-cite-check.json";
  a.click();
}

function renderTrans(rows) {
  var tbody = document.getElementById("transResults");
  tbody.innerHTML = "";
  rows.forEach(function (row) {
    var tr = document.createElement("tr");
    var transCell = row.error === "NO_ENDPOINT" ? esc(T().transNoEndpoint)
      : row.error ? esc(row.error) : esc(row.translation);
    tr.innerHTML = "<td>" + esc(row.original) + "</td><td>" + transCell + "</td>";
    tbody.appendChild(tr);
  });
  window.__transRows = rows;
}

async function doTranslate() {
  var text = document.getElementById("opinion").value || "";
  var endpoint = (document.getElementById("mtEndpoint").value || "").trim();
  var target = document.getElementById("mtTarget").value || "es";
  var rows = await translateParagraphs(splitParagraphs(text),
    { endpoint: endpoint, target: target });
  renderTrans(rows);
}
