(function () {
  "use strict";

  // ---- Before / After slider (generalized: works on any .compare-wrap) ----

  function setupSlider(wrap) {
    const before = wrap.querySelector(".img-before");
    const beforeBox = wrap.querySelector(".compare-before");
    const handle = wrap.querySelector(".compare-handle");

    const sizeBeforeImage = () => {
      const w = wrap.clientWidth;
      before.style.width = w + "px";
      before.style.height = "100%";
      before.style.maxWidth = "none";
    };

    const setPosition = (percent) => {
      percent = Math.max(0, Math.min(100, percent));
      beforeBox.style.width = percent + "%";
      handle.style.left = percent + "%";
    };

    sizeBeforeImage();
    setPosition(50);

    let dragging = false;
    const moveTo = (clientX) => {
      const rect = wrap.getBoundingClientRect();
      setPosition(((clientX - rect.left) / rect.width) * 100);
    };
    const start = (e) => {
      dragging = true;
      moveTo(e.touches ? e.touches[0].clientX : e.clientX);
    };
    const move = (e) => {
      if (!dragging) return;
      moveTo(e.touches ? e.touches[0].clientX : e.clientX);
    };
    const end = () => (dragging = false);

    wrap.addEventListener("mousedown", start);
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", end);
    wrap.addEventListener("touchstart", start);
    wrap.addEventListener("touchmove", move);
    wrap.addEventListener("touchend", end);
    window.addEventListener("resize", sizeBeforeImage);
  }

  document.querySelectorAll(".compare-wrap").forEach((wrap) => {
    const before = wrap.querySelector(".img-before");
    const after = wrap.querySelector(".img-after");
    let loaded = 0;
    const onReady = () => {
      loaded += 1;
      if (loaded >= 2) setupSlider(wrap);
    };
    if (before.complete) onReady();
    else before.onload = onReady;
    if (after.complete) onReady();
    else after.onload = onReady;
  });
})();
