/* NoctiCycle – interactive layer (inlined into the generated page). */
(function () {
  "use strict";

  var dataEl = document.getElementById("nocticycle-data");
  if (!dataEl) { return; }
  var data = JSON.parse(dataEl.textContent);
  var tz = data.tz;

  /* ---------- date helpers (everything is evaluated in the calendar's timezone) ---------- */

  function isoInTz(date) {
    try {
      return date.toLocaleDateString("en-CA", { timeZone: tz });
    } catch (e) {
      return date.toLocaleDateString("en-CA");
    }
  }

  function dayNumber(iso) {
    var p = iso.split("-");
    return Date.UTC(+p[0], +p[1] - 1, +p[2]) / 86400000;
  }

  function relativeDays(fromIso, toIso) {
    var n = dayNumber(toIso) - dayNumber(fromIso);
    if (n === 0) { return "today"; }
    if (n === 1) { return "tomorrow"; }
    if (n === -1) { return "yesterday"; }
    return n > 0 ? "in " + n + " days" : Math.abs(n) + " days ago";
  }

  function formatMoment(date) {
    try {
      return new Intl.DateTimeFormat(undefined, {
        weekday: "short", day: "numeric", month: "short",
        hour: "2-digit", minute: "2-digit", timeZone: tz
      }).format(date);
    } catch (e) {
      return date.toLocaleString();
    }
  }

  function nextEvent(kind, now) {
    for (var i = 0; i < data.events.length; i++) {
      var ev = data.events[i];
      if (ev.kind === kind && new Date(ev.iso) > now) { return ev; }
    }
    return null;
  }

  /* ---------- today highlight + next-events banner ---------- */

  function setupToday() {
    var now = new Date();
    var today = isoInTz(now);
    var cell = document.querySelector('.day-cell[data-date="' + today + '"]');
    if (cell) {
      cell.classList.add("today");
      cell.id = "today";
      var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      cell.scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" });
    }

    var banner = document.getElementById("next-events");
    if (!banner) { return; }

    var items = [
      { kind: "new", label: "Next new moon", cls: "ne-new" },
      { kind: "full", label: "Next full moon", cls: "ne-full" }
    ];
    var html = "";
    items.forEach(function (it) {
      var ev = nextEvent(it.kind, now);
      if (!ev) { return; }
      var when = new Date(ev.iso);
      html += '<div class="ne-item ' + it.cls + '">' +
        '<span class="ne-label">' + it.label + "</span>" +
        '<span class="ne-when">' + formatMoment(when) + "</span>" +
        '<span class="ne-rel">' + relativeDays(today, isoInTz(when)) + "</span></div>";
    });
    if (html) {
      banner.innerHTML = html;
      banner.hidden = false;
    }
  }

  /* ---------- day detail card ---------- */

  var cells = Array.prototype.slice.call(document.querySelectorAll(".day-cell[data-date]"));
  var card, backdrop, current = -1, lastFocus = null;

  function esc(text) {
    var d = document.createElement("div");
    d.textContent = text;
    return d.innerHTML;
  }

  function longDate(iso) {
    var p = iso.split("-");
    var d = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2], 12));
    return new Intl.DateTimeFormat(undefined, {
      weekday: "long", day: "numeric", month: "long", year: "numeric", timeZone: "UTC"
    }).format(d);
  }

  function nextOnOrAfter(kind, iso) {
    for (var i = 0; i < data.events.length; i++) {
      var ev = data.events[i];
      if (ev.kind !== kind) { continue; }
      var evIso = isoInTz(new Date(ev.iso));
      if (evIso >= iso) { return { ev: ev, iso: evIso }; }
    }
    return null;
  }

  function row(label, value) {
    return '<div class="dc-row"><span class="dc-k">' + label + '</span><span class="dc-v">' + value + "</span></div>";
  }

  function nextRow(label, kind, iso) {
    var n = nextOnOrAfter(kind, iso);
    if (!n) { return ""; }
    return row(label, esc(formatMoment(new Date(n.ev.iso))) +
      ' <span class="dc-rel">' + relativeDays(iso, n.iso) + "</span>");
  }

  function traditionBlock(info) {
    var tr = data.tradition;
    if (!tr || !info.t || !tr.items[info.t]) { return ""; }
    var it = tr.items[info.t];
    var kind = tr.kinds[it.k] || { svg: "" };
    return '<div class="dc-trad" data-tk="' + esc(it.k) + '">' +
      '<div class="dc-trad-name">' + esc(tr.name) + "</div>" +
      '<div class="dc-trad-label">' + kind.svg + "<span>" + esc(it.l) + "</span>" +
        (it.b ? '<span class="tb">' + esc(it.b) + "</span>" : "") + "</div>" +
      (it.p ? '<div class="dc-trad-sub">' + esc(it.p) + "</div>" : "") +
      "<p>" + esc(it.m) + "</p></div>";
  }

  function wheelBlock(info) {
    var wh = data.wheel;
    if (!wh || !info.w || !wh.items[info.w]) { return ""; }
    var it = wh.items[info.w];
    var meta = [];
    if (it.time) { meta.push("Exact moment: " + esc(it.time) + " local time"); }
    if (it.approx) { meta.push("Fixed, approximate date: it varies between communities"); }
    if (it.flipped) { meta.push("Dated for the southern hemisphere"); }
    return '<div class="dc-wheel" data-wk="' + esc(it.season) + '">' +
      '<div class="dc-w-head"><div class="dc-w-icon">' + it.svg + "</div><div>" +
        '<div class="dc-w-wheel">' + esc(wh.name) + " &middot; " + esc(it.kind) + "</div>" +
        '<div class="dc-w-name">' + esc(it.n) + "</div>" +
        '<div class="dc-w-sub">' + esc(it.sub) + "</div></div></div>" +
      '<div class="dc-w-theme">Theme: ' + esc(it.theme) + "</div>" +
      '<div class="dc-w-label">What is celebrated</div><p>' + esc(it.celebrates) + "</p>" +
      '<div class="dc-w-label">About this day</div><p>' + esc(it.about) + "</p>" +
      (meta.length ? '<div class="dc-w-meta">' + meta.join(" &middot; ") + "</div>" : "") +
      "</div>";
  }

  function buildCard() {
    backdrop = document.createElement("div");
    backdrop.className = "dc-backdrop";
    backdrop.hidden = true;
    card = document.createElement("div");
    card.className = "day-card";
    card.setAttribute("role", "dialog");
    card.setAttribute("aria-modal", "true");
    card.setAttribute("aria-label", "Day details");
    backdrop.appendChild(card);
    document.body.appendChild(backdrop);

    backdrop.addEventListener("click", function (e) {
      if (e.target === backdrop) { closeCard(); }
    });
    card.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-dc]");
      if (!btn) { return; }
      var action = btn.getAttribute("data-dc");
      if (action === "close") { closeCard(); }
      if (action === "prev") { showDay(current - 1); }
      if (action === "next") { showDay(current + 1); }
    });
  }

  function showDay(index) {
    if (index < 0 || index >= cells.length) { return; }
    current = index;
    var cell = cells[index];
    var iso = cell.getAttribute("data-date");
    var info = data.days[iso] || {};
    var svg = cell.querySelector(".moon-svg");

    var rows = row("Illumination", info.i + "%");
    if (info.a !== null && info.a !== undefined) {
      rows += row("Moon age", info.a + " days");
    }
    if (info.e) { rows += row("Exact time", esc(info.e)); }
    if (data.riseSet) {
      rows += row("Moonrise", info.r ? esc(info.r) : "&mdash;");
      rows += row("Moonset", info.s ? esc(info.s) : "&mdash;");
    }
    rows += nextRow("Next new moon", "new", iso);
    rows += nextRow("Next full moon", "full", iso);

    card.innerHTML =
      '<div class="dc-head">' +
        '<button type="button" class="dc-btn" data-dc="prev" aria-label="Previous day"' + (index === 0 ? " disabled" : "") + ">&#8249;</button>" +
        '<div class="dc-date">' + esc(longDate(iso)) + "</div>" +
        '<button type="button" class="dc-btn" data-dc="next" aria-label="Next day"' + (index === cells.length - 1 ? " disabled" : "") + ">&#8250;</button>" +
        '<button type="button" class="dc-btn dc-close" data-dc="close" aria-label="Close">&times;</button>' +
      "</div>" +
      '<div class="dc-moon">' + (svg ? svg.outerHTML : "") + "</div>" +
      '<div class="dc-phase">' + esc(info.n || "") + "</div>" +
      '<div class="dc-rows">' + rows + "</div>" + wheelBlock(info) + traditionBlock(info);

    var big = card.querySelector(".moon-svg");
    if (big) { big.classList.add("dc-moon-svg"); }
    backdrop.hidden = false;
    var focusTarget = card.querySelector(".dc-close");
    if (focusTarget) { focusTarget.focus(); }
  }

  function openCard(index) {
    if (!card) { buildCard(); }
    lastFocus = document.activeElement;
    showDay(index);
  }

  function closeCard() {
    if (!backdrop) { return; }
    backdrop.hidden = true;
    current = -1;
    if (lastFocus && lastFocus.focus) { lastFocus.focus(); }
  }

  cells.forEach(function (cell, i) {
    cell.setAttribute("tabindex", "0");
    cell.setAttribute("role", "button");
    cell.addEventListener("click", function () { openCard(i); });
    cell.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openCard(i);
      }
    });
  });

  document.addEventListener("keydown", function (e) {
    if (current < 0) { return; }
    if (e.key === "Escape") { closeCard(); }
    else if (e.key === "ArrowLeft") { showDay(current - 1); }
    else if (e.key === "ArrowRight") { showDay(current + 1); }
  });

  document.querySelectorAll(".wchip[data-wd]").forEach(function (chip) {
    chip.style.cursor = "pointer";
    chip.addEventListener("click", function () {
      var iso = chip.getAttribute("data-wd");
      for (var i = 0; i < cells.length; i++) {
        if (cells[i].getAttribute("data-date") === iso) { openCard(i); return; }
      }
    });
  });

  setupToday();
})();
