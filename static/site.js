// Progressive enhancement: filter + sort for benchmark tables. Page is complete without it.
(function () {
  "use strict";
  document.querySelectorAll("form.filters").forEach(function (form) {
    var table = document.getElementById("t-" + form.dataset.target);
    if (!table) return;
    form.hidden = false;
    var rows = Array.prototype.slice.call(table.tBodies[0].rows);
    var search = form.querySelector("[data-search]");
    var count = form.querySelector("[data-count]");
    var active = {};

    function apply() {
      var q = search.value.trim().toLowerCase();
      var shown = 0;
      rows.forEach(function (tr) {
        var ok = (!q || tr.dataset.search.indexOf(q) !== -1) &&
          (!active.status || tr.dataset.status === active.status) &&
          (!active.risk || tr.dataset.risk === active.risk);
        tr.hidden = !ok;
        if (ok) shown++;
      });
      count.value = shown + " / " + rows.length;
    }
    search.addEventListener("input", apply);
    form.addEventListener("submit", function (e) { e.preventDefault(); });
    form.querySelectorAll("button[data-filter]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var k = btn.dataset.filter, v = btn.dataset.value;
        var on = active[k] === v;
        form.querySelectorAll('button[data-filter="' + k + '"]').forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
        if (on) { delete active[k]; } else { active[k] = v; btn.setAttribute("aria-pressed", "true"); }
        apply();
      });
    });
    apply();

    var ORDER = { status: ["active", "saturating", "saturated", "retired"], risk: ["low", "medium", "high", ""] };
    table.querySelectorAll("th[data-sort]").forEach(function (th) {
      th.tabIndex = 0;
      th.setAttribute("role", "button");
      function key(tr) {
        var k = th.dataset.sort, v = tr.dataset[k];
        if (k === "score") return parseFloat(v);
        if (ORDER[k]) return ORDER[k].indexOf(v);
        return v;
      }
      function sort() {
        var dir = th.getAttribute("aria-sort") === "descending" ? "ascending" : "descending";
        table.querySelectorAll("th[aria-sort]").forEach(function (o) { o.removeAttribute("aria-sort"); });
        th.setAttribute("aria-sort", dir);
        var sign = dir === "descending" ? -1 : 1;
        rows.sort(function (a, b) { var x = key(a), y = key(b); return x < y ? -sign : x > y ? sign : 0; });
        rows.forEach(function (tr) { table.tBodies[0].appendChild(tr); });
      }
      th.addEventListener("click", sort);
      th.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); sort(); } });
    });
  });
})();
