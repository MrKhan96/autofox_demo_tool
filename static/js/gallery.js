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

  // Loads the before/after images for one .compare-wrap (from data-src, so
  // images for cars not currently on screen are never requested) and wires
  // up the slider once both are loaded.
  function activateWrap(wrap) {
    if (wrap.dataset.activated) return;
    wrap.dataset.activated = "1";

    const before = wrap.querySelector(".img-before");
    const after = wrap.querySelector(".img-after");
    let loaded = 0;
    const onReady = () => {
      loaded += 1;
      if (loaded >= 2) setupSlider(wrap);
    };
    before.onload = onReady;
    after.onload = onReady;
    before.src = before.dataset.src;
    after.src = after.dataset.src;
  }

  // ---- Pagination: one car per page, images loaded on demand -------------

  function initPagination() {
    const grid = document.querySelector(".gallery-grid");
    if (!grid) return;

    const cards = Array.from(grid.querySelectorAll(".gallery-card"));
    const pageSize = parseInt(grid.dataset.pageSize, 10) || 1;
    const totalPages = Math.max(1, Math.ceil(cards.length / pageSize));

    const prevBtn = document.getElementById("prev-page");
    const nextBtn = document.getElementById("next-page");
    const indicator = document.getElementById("page-indicator");

    let page = 0;

    function showPage(n) {
      page = Math.max(0, Math.min(totalPages - 1, n));
      cards.forEach((card, i) => {
        const cardPage = Math.floor(i / pageSize);
        const visible = cardPage === page;
        card.classList.toggle("hidden", !visible);
        if (visible) {
          card.querySelectorAll(".compare-wrap").forEach(activateWrap);
        }
      });
      if (indicator) indicator.textContent = `Car ${page + 1} of ${totalPages}`;
      if (prevBtn) prevBtn.disabled = page === 0;
      if (nextBtn) nextBtn.disabled = page === totalPages - 1;
    }

    if (prevBtn) prevBtn.addEventListener("click", () => showPage(page - 1));
    if (nextBtn) nextBtn.addEventListener("click", () => showPage(page + 1));

    showPage(0);
  }

  initPagination();
})();
