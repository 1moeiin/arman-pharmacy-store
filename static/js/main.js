(function () {
  "use strict";

  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : null;
  }
  const csrftoken = getCookie("csrftoken");

  /* ------------------------------------------------------------------ */
  /* Scroll reveal — progressive enhancement only. Every element is      */
  /* already fully present in the server-rendered HTML; JS merely        */
  /* animates its entrance. If JS fails/is disabled, .reveal falls back  */
  /* to fully visible content via the no-js guard below.                 */
  /* ------------------------------------------------------------------ */
  document.documentElement.classList.remove("no-js");

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function initReveal() {
    const targets = document.querySelectorAll(".reveal");
    if (!targets.length) return;
    if (reduceMotion || !("IntersectionObserver" in window)) {
      targets.forEach((el) => el.classList.add("is-visible"));
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    targets.forEach((el, i) => {
      el.style.setProperty("--stagger-index", i % 8);
      observer.observe(el);
    });

    // Safety net: a crawler that executes JS but never scrolls (common for
    // search engine renderers taking a single viewport snapshot) would
    // otherwise see below-the-fold .reveal content stuck at opacity:0. Force
    // everything visible shortly after load so no real content is ever
    // hidden from indexing — only the animation timing is skipped.
    window.setTimeout(() => {
      targets.forEach((el) => el.classList.add("is-visible"));
      observer.disconnect();
    }, 2500);
  }

  /* ------------------------------------------------------------------ */
  /* Mobile nav                                                          */
  /* ------------------------------------------------------------------ */
  function initMobileNav() {
    const toggle = document.querySelector(".menu-toggle");
    const nav = document.querySelector(".main-nav");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", () => {
      const isOpen = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(isOpen));
    });
  }

  /* ------------------------------------------------------------------ */
  /* Toasts                                                              */
  /* ------------------------------------------------------------------ */
  function toastRegion() {
    let region = document.querySelector(".toast-region");
    if (!region) {
      region = document.createElement("div");
      region.className = "toast-region";
      region.setAttribute("role", "status");
      region.setAttribute("aria-live", "polite");
      document.body.appendChild(region);
    }
    return region;
  }

  function showToast(message, type) {
    const region = toastRegion();
    const toast = document.createElement("div");
    toast.className = "toast " + (type || "info");
    toast.textContent = message;
    region.appendChild(toast);
    setTimeout(() => {
      toast.style.transition = "opacity 200ms ease";
      toast.style.opacity = "0";
      setTimeout(() => toast.remove(), 220);
    }, 3200);
  }
  window.showToast = showToast;

  /* ------------------------------------------------------------------ */
  /* Cart — AJAX enhancement over plain <form method="post"> actions.    */
  /* Every add/remove/update control is a real form; JS intercepts the   */
  /* submit only to avoid a full page reload, and falls back cleanly if  */
  /* fetch fails.                                                        */
  /* ------------------------------------------------------------------ */
  function updateCartBadge(count) {
    const badge = document.querySelector(".cart-badge");
    if (!badge) return;
    badge.textContent = count;
    badge.hidden = count === 0;
    badge.classList.remove("pop-once");
    void badge.offsetWidth;
    badge.classList.add("pop-once");
  }

  function initCartForms() {
    document.querySelectorAll("form[data-cart-action]").forEach((form) => {
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(form);
        const submitBtn = form.querySelector("button[type=submit]");
        if (submitBtn) submitBtn.disabled = true;
        try {
          const response = await fetch(form.action, {
            method: "POST",
            headers: { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": csrftoken },
            body: formData,
          });
          const data = await response.json();
          if (data.ok) {
            updateCartBadge(data.cart_count);
            const message = form.dataset.successMessage || "سبد خرید به‌روزرسانی شد.";
            showToast(message, "success");
            if (form.dataset.cartAction === "remove") {
              const row = form.closest("[data-cart-line]");
              if (row) row.remove();
            }
            document.dispatchEvent(new CustomEvent("cart:updated", { detail: data }));
          } else {
            showToast(data.error || "خطایی رخ داد.", "error");
          }
        } catch (err) {
          form.submit();
        } finally {
          if (submitBtn) submitBtn.disabled = false;
        }
      });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Quantity stepper                                                    */
  /* ------------------------------------------------------------------ */
  function initQuantitySteppers() {
    document.querySelectorAll(".quantity-stepper").forEach((stepper) => {
      const input = stepper.querySelector("input");
      const max = parseInt(input?.max, 10) || 999;
      stepper.querySelectorAll("button").forEach((button) => {
        button.addEventListener("click", () => {
          let value = parseInt(input.value, 10) || 1;
          value += button.dataset.step === "up" ? 1 : -1;
          input.value = Math.min(Math.max(value, 1), max);
          input.dispatchEvent(new Event("change", { bubbles: true }));
        });
      });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Product gallery thumbnails                                          */
  /* ------------------------------------------------------------------ */
  function initGallery() {
    const main = document.querySelector("[data-gallery-main]");
    if (!main) return;
    document.querySelectorAll("[data-gallery-thumb]").forEach((thumb) => {
      thumb.addEventListener("click", () => {
        main.src = thumb.dataset.fullSrc || thumb.src;
        main.alt = thumb.alt;
        document.querySelectorAll("[data-gallery-thumb]").forEach((t) => t.classList.remove("active"));
        thumb.classList.add("active");
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initReveal();
    initMobileNav();
    initCartForms();
    initQuantitySteppers();
    initGallery();
  });
})();
