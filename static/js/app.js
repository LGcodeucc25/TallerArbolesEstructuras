// Live clock, current shift, sidebar toggle and dismissible messages.
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
  if (toggle && sidebar) {
    toggle.addEventListener("click", function () {
      sidebar.classList.toggle("open");
    });
  }

  document.querySelectorAll(".flash-close").forEach(function (button) {
    button.addEventListener("click", function () {
      button.parentElement.remove();
    });
  });
})();
