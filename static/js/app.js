// Live clock, current shift, collapsible sidebar and auto-dismissing toasts.
(function () {
  var clock = document.getElementById("clock");
  var shift = document.getElementById("shift");

  function pad(value) {
    return value < 10 ? "0" + value : String(value);
  }

  function shiftName(hour) {
    if (hour >= 7 && hour < 13) return "Turno mañana · 07:00–13:00";
    if (hour >= 13 && hour < 19) return "Turno tarde · 13:00–19:00";
    return "Turno noche · 19:00–07:00";
  }

  function tick() {
    var now = new Date();
    if (clock) clock.textContent = pad(now.getHours()) + ":" + pad(now.getMinutes()) + ":" + pad(now.getSeconds());
    if (shift) shift.textContent = shiftName(now.getHours());
  }

  tick();
  setInterval(tick, 1000);

  var toggle = document.getElementById("menu-toggle");
  var sidebar = document.getElementById("sidebar");
  var backdrop = document.getElementById("backdrop");

  function setMenu(open) {
    sidebar.classList.toggle("open", open);
    backdrop.classList.toggle("show", open);
  }

  if (toggle && sidebar && backdrop) {
    toggle.addEventListener("click", function () {
      setMenu(!sidebar.classList.contains("open"));
    });
    backdrop.addEventListener("click", function () {
      setMenu(false);
    });
  }

  function dismiss(toast) {
    toast.classList.add("hide");
    setTimeout(function () { toast.remove(); }, 200);
  }

  document.querySelectorAll(".toast").forEach(function (toast) {
    var close = toast.querySelector(".toast-close");
    if (close) close.addEventListener("click", function () { dismiss(toast); });
    setTimeout(function () { dismiss(toast); }, 6000);
  });
})();
