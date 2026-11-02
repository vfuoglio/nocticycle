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

  setupToday();
})();
