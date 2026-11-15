(function () {
  var button = document.querySelector("[data-listen]");
  if (!button || !window.speechSynthesis) {
    if (button) button.hidden = true;
    return;
  }

  var article = document.querySelector("article.story");
  var synthesis = window.speechSynthesis;
  var htmlLang = document.documentElement.lang || "en";
  var voiceLang = htmlLang.indexOf("zh") === 0 ? "zh-CN" : "en-US";
  var playLabel = button.getAttribute("data-play") || "Listen";
  var stopLabel = button.getAttribute("data-stop") || "Stop";
  var reading = false;
  var keepAlive = 0;
  var session = 0;

  function storyChunks() {
    var chunks = [];
    var title = article.querySelector("h1");
    if (title) {
      var clone = title.cloneNode(true);
      var number = clone.querySelector(".num");
      if (number) number.remove();
      var name = clone.textContent.replace(/\s+/g, " ").trim();
      if (name) chunks.push(name);
    }
    article.querySelectorAll(".prose p, .moral p").forEach(function (paragraph) {
      var text = paragraph.textContent.replace(/\s+/g, " ").trim();
      if (text) chunks.push(text);
    });
    return chunks;
  }

  function chooseVoice() {
    var voices = synthesis.getVoices();
    var prefix = voiceLang.slice(0, 2).toLowerCase();
    var i;
    for (i = 0; i < voices.length; i += 1) {
      if (voices[i].lang === voiceLang) return voices[i];
    }
    for (i = 0; i < voices.length; i += 1) {
      if (voices[i].lang.toLowerCase().indexOf(prefix) === 0) return voices[i];
    }
    return null;
  }

  function showPlaying(playing) {
    reading = playing;
    button.textContent = playing ? stopLabel : playLabel;
    button.setAttribute("aria-pressed", playing ? "true" : "false");
  }

  function stopKeepAlive() {
    if (keepAlive) {
      window.clearInterval(keepAlive);
      keepAlive = 0;
    }
  }

  function stop() {
    session += 1;
    stopKeepAlive();
    synthesis.cancel();
    showPlaying(false);
  }

  function start() {
    var chunks = storyChunks();
    var voice = chooseVoice();
    var current = session + 1;
    if (!chunks.length) return;
    session = current;
    chunks.forEach(function (text, index) {
      var utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = voiceLang;
      if (voice) utterance.voice = voice;
      utterance.onend = function () {
        if (current !== session || index !== chunks.length - 1) return;
        stopKeepAlive();
        showPlaying(false);
      };
      synthesis.speak(utterance);
    });
    showPlaying(true);
    stopKeepAlive();
    keepAlive = window.setInterval(function () {
      if (!reading || !synthesis.speaking) return;
      synthesis.pause();
      synthesis.resume();
    }, 10000);
  }

  button.addEventListener("click", function () {
    if (reading || synthesis.speaking || synthesis.pending) stop();
    else start();
  });

  window.addEventListener("pagehide", stop);
})();
