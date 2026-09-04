// Progressive enhancement: filter + sort for benchmark tables. Page is complete without it.
(function () {
  "use strict";
  document.querySelectorAll("form.filters").forEach(function (form) {
    var table = document.getElementById("t-" + form.dataset.target);
    if (!table) return;
    form.hidden = false;
    var rows = Array.prototype.slice.call(table.tBodies[0].rows).filter(function (r) { return !r.classList.contains("divider"); });
    var divider = table.querySelector("tr.divider");
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
      if (divider) divider.hidden = !rows.some(function (r) { return !r.hidden && r.classList.contains("compact"); });
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
        var live = rows.filter(function (r) { return !r.classList.contains("compact"); });
        var gone = rows.filter(function (r) { return r.classList.contains("compact"); });
        live.forEach(function (tr) { table.tBodies[0].appendChild(tr); });
        if (divider) table.tBodies[0].appendChild(divider);
        gone.forEach(function (tr) { table.tBodies[0].appendChild(tr); });
      }
      th.addEventListener("click", sort);
      th.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); sort(); } });
    });
  });
})();

// Lifespan chart: swap live/full SVG, hover highlight (row + its arrows), tooltip.
(function () {
  "use strict";
  var wrap = document.querySelector(".chart-wrap");
  if (!wrap) return;
  var tip = wrap.querySelector(".tooltip"), controls = wrap.querySelector(".chart-controls");
  var live = wrap.querySelectorAll(".chart-live, .chart-live-m"), full = wrap.querySelectorAll(".chart-full, .chart-full-m");
  controls.hidden = false;
  function setHidden(el, v) { if (v) el.setAttribute("hidden", "hidden"); else el.removeAttribute("hidden"); }
  var btn = controls.querySelector("button[data-toggle=retired]");
  btn.addEventListener("click", function () {
    var showFull = btn.getAttribute("aria-pressed") !== "true";
    btn.setAttribute("aria-pressed", String(showFull));
    live.forEach(function (el) { setHidden(el, showFull); }); full.forEach(function (el) { setHidden(el, !showFull); });
  });
  wrap.querySelectorAll(".row").forEach(function (r) {
    var svg = r.ownerSVGElement;
    var mine = Array.prototype.filter.call(svg.querySelectorAll(".chain-arrow"), function (a) {
      return a.dataset.from === r.dataset.id || a.dataset.to === r.dataset.id;
    });
    r.addEventListener("mouseenter", function () {
      wrap.classList.add("hovering"); r.classList.add("hot");
      mine.forEach(function (a) { a.classList.add("hot"); });
      tip.textContent = r.dataset.tip; tip.hidden = false;
    });
    r.addEventListener("mousemove", function (e) {
      var b = wrap.getBoundingClientRect();
      var x = e.clientX - b.left + 12, y = e.clientY - b.top + 12;
      if (x + tip.offsetWidth > b.width) x -= tip.offsetWidth + 24;
      tip.style.left = x + "px"; tip.style.top = y + "px";
    });
    r.addEventListener("mouseleave", function () {
      wrap.classList.remove("hovering"); r.classList.remove("hot");
      mine.forEach(function (a) { a.classList.remove("hot"); }); tip.hidden = true;
    });
  });
})();
