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

// Saturation chart: status toggles, focus/full domain switch, hover highlight, tooltip.
(function () {
  "use strict";
  var wrap = document.querySelector(".chart-wrap");
  if (!wrap) return;
  var tip = wrap.querySelector(".tooltip"), controls = wrap.querySelector(".chart-controls");
  var svgs = { focus: wrap.querySelector(".chart-focus"), full: wrap.querySelector(".chart-full") };
  var on = {};
  controls.hidden = false;
  function setHidden(el, v) { if (v) el.setAttribute("hidden", "hidden"); else el.removeAttribute("hidden"); }
  controls.querySelectorAll("button[data-toggle=status]").forEach(function (b) {
    on[b.dataset.value] = b.getAttribute("aria-pressed") === "true";
    b.addEventListener("click", function () {
      on[b.dataset.value] = !on[b.dataset.value];
      b.setAttribute("aria-pressed", String(on[b.dataset.value]));
      apply();
    });
  });
  function apply() {
    // Full domain only when a retired/saturated group is shown; otherwise the focused (recent) domain.
    var wide = on.saturated || on.retired;
    setHidden(svgs.focus, wide); setHidden(svgs.full, !wide);
    Object.keys(svgs).forEach(function (k) {
      var shown = {};
      svgs[k].querySelectorAll(".series").forEach(function (s) {
        var v = !!on[s.dataset.status]; setHidden(s, !v); if (v) shown[s.dataset.id] = true;
      });
      svgs[k].querySelectorAll(".chain-arrow").forEach(function (a) { setHidden(a, !(shown[a.dataset.from] && shown[a.dataset.to])); });
    });
  }
  apply();
  // Narrow screens: land on the recent end of the plot with the label gutter peeking in on the right.
  if (wrap.scrollWidth > wrap.clientWidth) {
    var vis = svgs.focus.hasAttribute("hidden") ? svgs.full : svgs.focus;
    var plotRight = vis.getBoundingClientRect().width * 0.81;  // x1 / CHART_W
    wrap.scrollLeft = Math.max(0, plotRight - wrap.clientWidth * 0.55);
  }
  wrap.querySelectorAll(".series").forEach(function (s) {
    s.addEventListener("mouseenter", function () {
      wrap.classList.add("hovering"); s.classList.add("hot");
      tip.textContent = s.dataset.tip; tip.hidden = false;
    });
    s.addEventListener("mousemove", function (e) {
      var r = wrap.getBoundingClientRect();
      var x = e.clientX - r.left + 12, y = e.clientY - r.top + 12;
      if (x + tip.offsetWidth > r.width) x -= tip.offsetWidth + 24;
      tip.style.left = x + "px"; tip.style.top = y + "px";
    });
    s.addEventListener("mouseleave", function () {
      wrap.classList.remove("hovering"); s.classList.remove("hot"); tip.hidden = true;
    });
  });
})();
