(function () {
  "use strict";

  const hero = document.querySelector("[data-hero]");
  if (!hero) return;

  const heroSearch = hero.querySelector(".home-search");
  if (heroSearch && "IntersectionObserver" in window) {
    new IntersectionObserver(
      ([entry]) => document.body.classList.toggle("hero-search-out", !entry.isIntersecting),
      { rootMargin: "-96px 0px 0px 0px" }
    ).observe(heroSearch);
  }

  const finePointer = window.matchMedia("(pointer: fine)").matches;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!finePointer || reduceMotion) return;

  let frame = 0;
  let x = 0;
  let y = 0;
  hero.addEventListener("pointermove", (event) => {
    const rect = hero.getBoundingClientRect();
    x = (event.clientX - rect.left) / rect.width - 0.5;
    y = (event.clientY - rect.top) / rect.height - 0.5;
    if (frame) return;
    frame = requestAnimationFrame(() => {
      hero.style.setProperty("--px", x.toFixed(3));
      hero.style.setProperty("--py", y.toFixed(3));
      frame = 0;
    });
  });
  hero.addEventListener("pointerleave", () => {
    hero.style.setProperty("--px", "0");
    hero.style.setProperty("--py", "0");
  });
})();
