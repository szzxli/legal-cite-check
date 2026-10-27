/* Browser UI. Local only: this file makes NO network calls.
   Text stays in memory; nothing is stored (no localStorage of brief text)
   and nothing is sent anywhere. The only third-party script on the page
   is the GoatCounter page-view counter in index.html. */
function render(results) {
  const tbody = document.getElementById("results");
  tbody.innerHTML = "";
  results.forEach((r, i) => {
    const tr = document.createElement("tr");
    const esc = (s) => String(s || "").replace(/[&<>"]/g,
      (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    tr.innerHTML = "<td>" + (i + 1) + "</td><td>" + esc(r.text) + "</td>"
      + "<td>" + esc(r.caseName) + "</td><td>NOT_CHECKED</td>"
      + "<td><a href=\"" + esc(r.manualUrl) + "\" target=\"_blank\" rel=\"noopener\">Open on CourtListener</a>"
      + " | <a href=\"" + esc(r.scholarUrl) + "\" target=\"_blank\" rel=\"noopener\">Search Google Scholar</a></td>";
    tbody.appendChild(tr);
  });
  document.getElementById("count").textContent =
    results.length + " citation(s) found. Browser mode: NOT_CHECKED for all \u2014 run the CLI for the full CourtListener check.";
  window.__lastResults = results;
}

function check() {
  const text = document.getElementById("input").value || "";
  render(extractCitations(text));
}

function openFile(input) {
  const file = input.files && input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    document.getElementById("input").value = reader.result || "";
    check();
  };
  reader.readAsText(file);
}

function exportMarkdown() {
  const results = window.__lastResults || [];
  const lines = ["> **Not legal advice. This tool only checks whether a cited case exists in CourtListener and whether the case name matches. It does not check whether the case supports your argument, whether quotes or pin cites are accurate, or whether the case is still good law. A case marked NOT FOUND may still exist (CourtListener's coverage is incomplete); a case marked VERIFIED may still be wrong for your purpose. Read every case you cite.**", ""];
  results.forEach((r) => {
    lines.push("- [ ] NOT_CHECKED \u2014 " + r.text
      + (r.caseName ? " (" + r.caseName + ")" : "")
      + " \u2014 " + r.manualUrl);
  });
  navigator.clipboard.writeText(lines.join("\n")).then(() => {
    document.getElementById("count").textContent = "Markdown checklist copied.";
  });
}

function exportJson() {
  const blob = new Blob([JSON.stringify(window.__lastResults || [], null, 2)],
    { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "legal-cite-check.json";
  a.click();
}
