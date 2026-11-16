(function () {
  var button = document.querySelector("[data-listen]");
  var src = button && button.getAttribute("data-audio");
  if (!button || !src || !window.Audio) {
    if (button) button.hidden = true;
    return;
  }

  var audio = new Audio(src);
  audio.preload = "none";
  var playLabel = button.getAttribute("data-play") || "Listen";
  var stopLabel = button.getAttribute("data-stop") || "Stop";

  function showPlaying(playing) {
    button.textContent = playing ? stopLabel : playLabel;
    button.setAttribute("aria-pressed", playing ? "true" : "false");
  }

  button.addEventListener("click", function () {
    if (!audio.paused && !audio.ended) {
      audio.pause();
      showPlaying(false);
      return;
    }
    var pending = audio.play();
    showPlaying(true);
    if (pending && pending.catch) pending.catch(function () { showPlaying(false); });
  });

  audio.addEventListener("ended", function () { showPlaying(false); });
  audio.addEventListener("error", function () { showPlaying(false); });
  window.addEventListener("pagehide", function () { audio.pause(); });
})();
