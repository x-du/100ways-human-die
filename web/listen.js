(function () {
  var button = document.querySelector("[data-listen]");
  var src = button && button.getAttribute("data-audio");
  if (!button || !src || !window.Audio) {
    if (button) button.hidden = true;
    return;
  }

  var zh = (document.documentElement.lang || "").indexOf("zh") === 0;
  var audio = new Audio(src);
  audio.preload = "metadata";
  if ("preservesPitch" in audio) audio.preservesPitch = true;
  var playLabel = button.getAttribute("data-play") || "Listen";
  var stopLabel = button.getAttribute("data-stop") || "Stop";
  var rates = [0.75, 1, 1.25, 1.5, 2];
  var savedRate = readRate();
  var popoverOK = typeof HTMLElement.prototype.showPopover === "function";

  var toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "listen-more";
  toggle.textContent = rateLabel(savedRate);
  toggle.setAttribute("aria-label", zh ? "朗读设置" : "Narration settings");
  if (popoverOK) toggle.setAttribute("popovertarget", "narration-controls");

  var panel = document.createElement("div");
  panel.id = "narration-controls";
  panel.className = "narration-panel";
  if (popoverOK) panel.setAttribute("popover", "auto");

  var seek = document.createElement("label");
  seek.className = "seek";
  var seekName = document.createElement("span");
  seekName.className = "control-name";
  seekName.textContent = zh ? "进度" : "Position";
  var seekRow = document.createElement("span");
  seekRow.className = "seek-row";
  var elapsed = document.createElement("span");
  elapsed.className = "time";
  elapsed.textContent = "0:00";
  var range = document.createElement("input");
  range.type = "range";
  range.min = "0";
  range.max = "0";
  range.step = "0.1";
  range.value = "0";
  range.disabled = true;
  range.setAttribute("aria-label", zh ? "进度" : "Position");
  var total = document.createElement("span");
  total.className = "time";
  total.textContent = "0:00";
  seekRow.appendChild(elapsed);
  seekRow.appendChild(range);
  seekRow.appendChild(total);
  seek.appendChild(seekName);
  seek.appendChild(seekRow);

  var rateGroup = document.createElement("div");
  rateGroup.className = "rate";
  rateGroup.setAttribute("role", "group");
  rateGroup.setAttribute("aria-label", zh ? "语速" : "Speed");
  var rateName = document.createElement("span");
  rateName.className = "control-name";
  rateName.textContent = zh ? "语速" : "Speed";
  var rateRow = document.createElement("span");
  rateRow.className = "rate-row";
  var rateButtons = rates.map(function (rate) {
    var choice = document.createElement("button");
    choice.type = "button";
    choice.className = "rate-choice";
    choice.textContent = rateLabel(rate);
    choice.setAttribute("aria-pressed", rate === savedRate ? "true" : "false");
    choice.addEventListener("click", function () { applyRate(rate); });
    rateRow.appendChild(choice);
    return choice;
  });
  rateGroup.appendChild(rateName);
  rateGroup.appendChild(rateRow);
  var play = document.createElement("button");
  play.type = "button";
  play.className = "narration-play";
  play.setAttribute("aria-pressed", "false");
  setPlayIcon(false);

  panel.appendChild(seek);
  panel.appendChild(play);
  panel.appendChild(rateGroup);

  button.insertAdjacentElement("afterend", toggle);
  document.body.appendChild(panel);
  applyRate(savedRate);
  if (!popoverOK) toggle.hidden = true;

  function readRate() {
    try {
      var stored = Number(window.sessionStorage.getItem("narration-rate"));
      if (rates.indexOf(stored) !== -1) return stored;
    } catch (error) {}
    return 1;
  }

  function rateLabel(rate) {
    return String(rate) + "×";
  }

  function applyRate(rate) {
    audio.playbackRate = rate;
    toggle.textContent = rateLabel(rate);
    rateButtons.forEach(function (choice, index) {
      choice.setAttribute("aria-pressed", rates[index] === rate ? "true" : "false");
    });
    try {
      window.sessionStorage.setItem("narration-rate", String(rate));
    } catch (error) {}
  }

  function format(seconds) {
    if (!isFinite(seconds) || seconds < 0) seconds = 0;
    var whole = Math.floor(seconds);
    var minutes = Math.floor(whole / 60);
    var remainder = whole % 60;
    return minutes + ":" + (remainder < 10 ? "0" : "") + remainder;
  }

  function knownDuration() {
    return isFinite(audio.duration) && audio.duration > 0;
  }

  function icon(name) {
    return document.createElementNS("http://www.w3.org/2000/svg", name);
  }

  function setPlayIcon(playing) {
    while (play.firstChild) play.removeChild(play.firstChild);
    var svg = icon("svg");
    svg.setAttribute("viewBox", "0 0 16 16");
    svg.setAttribute("aria-hidden", "true");
    if (playing) {
      var left = icon("rect");
      left.setAttribute("x", "3");
      left.setAttribute("y", "2");
      left.setAttribute("width", "3.2");
      left.setAttribute("height", "12");
      var right = icon("rect");
      right.setAttribute("x", "9.8");
      right.setAttribute("y", "2");
      right.setAttribute("width", "3.2");
      right.setAttribute("height", "12");
      svg.appendChild(left);
      svg.appendChild(right);
      play.setAttribute("aria-label", zh ? "暂停" : "Pause");
    } else {
      var triangle = icon("path");
      triangle.setAttribute("d", "M4 2.2 L13.2 8 L4 13.8 Z");
      svg.appendChild(triangle);
      play.setAttribute("aria-label", zh ? "播放" : "Play");
    }
    play.appendChild(svg);
  }

  function showPlaying(playing) {
    button.textContent = playing ? stopLabel : playLabel;
    button.setAttribute("aria-pressed", playing ? "true" : "false");
    play.setAttribute("aria-pressed", playing ? "true" : "false");
    setPlayIcon(playing);
  }

  function togglePlayback() {
    if (!audio.paused && !audio.ended) {
      audio.pause();
      showPlaying(false);
      return;
    }
    var pending = audio.play();
    showPlaying(true);
    if (pending && pending.catch) pending.catch(function () { showPlaying(false); });
  }

  function showTime() {
    elapsed.textContent = format(audio.currentTime);
    if (!knownDuration()) return;
    total.textContent = format(audio.duration);
    if (document.activeElement === range) return;
    range.value = String(audio.currentTime);
  }

  function placePanel() {
    if (!popoverOK || !panel.matches(":popover-open")) return;
    var rect = toggle.getBoundingClientRect();
    var width = panel.offsetWidth;
    var left = rect.left;
    var maxLeft = window.innerWidth - width - 12;
    if (left > maxLeft) left = Math.max(12, maxLeft);
    panel.style.top = Math.round(rect.bottom + 8) + "px";
    panel.style.left = Math.round(left) + "px";
  }

  button.addEventListener("click", togglePlayback);
  play.addEventListener("click", togglePlayback);

  range.addEventListener("input", function () {
    if (!knownDuration()) return;
    audio.currentTime = Number(range.value);
    elapsed.textContent = format(audio.currentTime);
  });

  function armSeek() {
    if (!knownDuration()) return;
    range.disabled = false;
    range.max = String(audio.duration);
    showTime();
  }

  panel.addEventListener("toggle", function (event) {
    if (event.newState === "open") placePanel();
  });
  window.addEventListener("resize", placePanel);
  window.addEventListener("scroll", placePanel, true);

  audio.addEventListener("loadedmetadata", armSeek);
  audio.addEventListener("durationchange", armSeek);
  armSeek();
  audio.addEventListener("timeupdate", showTime);
  audio.addEventListener("ended", function () {
    showPlaying(false);
    showTime();
  });
  audio.addEventListener("error", function () { showPlaying(false); });
  window.addEventListener("pagehide", function () { audio.pause(); });
})();
