(function () {
  "use strict";

  // The slider reads 0-100 on screen, but the *actual* body blend is clamped to
  // this range: 0% -> BODY_MIN, 100% -> BODY_MAX. Used for both the live
  // cross-fade opacity and the downloaded composite so they always match.
  const BODY_MIN = 0.40;
  const BODY_MAX = 0.90;
  const bodyOpacity = (pct) => BODY_MIN + (pct / 100) * (BODY_MAX - BODY_MIN);

  // ---- Per-card slider: cross-fade bodyclean over base --------------------
  //
  // The right pane stacks two precomputed images: `base` (body reflective) at
  // the bottom and `bodyclean` (body cleaned) on top. Setting the top image's
  // opacity to t = bodyOpacity(slider) renders base*(1-t) + bodyclean*t, which
  // reproduces the Colab body-alpha blend (clamped to the BODY_MIN..BODY_MAX range).

  function setupCard(card) {
    if (card.dataset.activated) return;
    card.dataset.activated = "1";

    const imgs = card.querySelectorAll(".pane-img");
    imgs.forEach((img) => {
      if (img.dataset.src && !img.src) img.src = img.dataset.src;
    });

    const slider = card.querySelector(".body-slider");
    const base = card.querySelector(".blend-base");
    const top = card.querySelector(".blend-top");
    const valueOut = card.querySelector(".control-value");
    const readout = card.querySelector(".level-readout");
    const downloadBtn = card.querySelector(".download-btn");
    if (!slider || !top) return;

    const apply = () => {
      const t = Number(slider.value);
      top.style.opacity = String(bodyOpacity(t));
      const label = t + "%";
      if (valueOut) valueOut.textContent = label;
      if (readout) readout.textContent = label;
    };

    slider.addEventListener("input", apply);
    apply();

    if (downloadBtn && base) {
      downloadBtn.addEventListener("click", () => downloadBlend(card, base, top, slider));
    }
  }

  // Composite base + bodyclean at the current level onto a canvas and save it,
  // so the downloaded file is exactly the blended image on screen (full res).
  function downloadBlend(card, base, top, slider) {
    if (!base.complete || !top.complete) return;
    const pct = Number(slider.value);
    const t = bodyOpacity(pct);
    const w = base.naturalWidth || base.width;
    const h = base.naturalHeight || base.height;

    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(base, 0, 0, w, h);
    ctx.globalAlpha = t;
    ctx.drawImage(top, 0, 0, w, h);
    ctx.globalAlpha = 1;

    const nameEl = card.querySelector(".card-name");
    const name = (nameEl ? nameEl.textContent : "car").trim();

    canvas.toBlob(
      (blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${name}_blended_${pct}.jpg`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      },
      "image/jpeg",
      0.92
    );
  }

  // ---- Pagination: one car per page, images loaded on demand --------------

  function initPagination() {
    const grid = document.querySelector(".gallery-grid");
    if (!grid) return;

    const cards = Array.from(grid.querySelectorAll(".reflect-card"));
    const pageSize = parseInt(grid.dataset.pageSize, 10) || 1;
    const totalPages = Math.max(1, Math.ceil(cards.length / pageSize));

    const prevBtn = document.getElementById("prev-page");
    const nextBtn = document.getElementById("next-page");
    const indicator = document.getElementById("page-indicator");

    let page = 0;

    function showPage(n) {
      page = Math.max(0, Math.min(totalPages - 1, n));
      cards.forEach((card, i) => {
        const visible = Math.floor(i / pageSize) === page;
        card.classList.toggle("hidden", !visible);
        if (visible) setupCard(card);
      });
      if (indicator) indicator.textContent = `Car ${page + 1} of ${totalPages}`;
      if (prevBtn) prevBtn.disabled = page === 0;
      if (nextBtn) nextBtn.disabled = page === totalPages - 1;
    }

    if (prevBtn) prevBtn.addEventListener("click", () => showPage(page - 1));
    if (nextBtn) nextBtn.addEventListener("click", () => showPage(page + 1));

    document.addEventListener("keydown", (e) => {
      if (e.target && e.target.classList.contains("body-slider")) return;
      if (e.key === "ArrowLeft") showPage(page - 1);
      else if (e.key === "ArrowRight") showPage(page + 1);
    });

    showPage(0);
  }

  initPagination();
})();
