// rail.js — منطق سایدبار جدید (آیکون‌ریل)

(function () {
  const rail = document.getElementById("jRail");
  const pill = document.getElementById("jRailPill");
  if (!rail || !pill) return;

  const items = Array.from(rail.querySelectorAll(".j-rail-item[data-path]"));
  const path = window.location.pathname;

  function findActiveItem() {
    // اول تطابق دقیق، بعد تطابق ابتدای مسیر (برای /journal/<id> هم "Journal" روشن بمونه)
    let exact = items.find((el) => el.dataset.path === path);
    if (exact) return exact;
    const candidates = items
      .filter((el) => el.dataset.path !== "/" && path.startsWith(el.dataset.path))
      .sort((a, b) => b.dataset.path.length - a.dataset.path.length);
    return candidates[0] || null;
  }

  function movePillTo(el) {
    if (!el) {
      pill.style.opacity = "0";
      return;
    }
    const railRect = rail.getBoundingClientRect();
    const elRect = el.getBoundingClientRect();
    pill.style.top = (elRect.top - railRect.top) + "px";
    pill.style.height = elRect.height + "px";
    pill.style.opacity = "1";
    items.forEach((i) => i.classList.remove("j-active"));
    el.classList.add("j-active");
  }

  const active = findActiveItem();
  // اولین بار بدون انیمیشن جابه‌جا بشه، بعدش transition فعال بشه
  pill.style.transition = "none";
  movePillTo(active);
  requestAnimationFrame(() => {
    pill.style.transition = "top 0.35s cubic-bezier(.4,0,.2,1), height 0.35s ease, opacity 0.25s ease";
  });

  window.addEventListener("resize", () => movePillTo(rail.querySelector(".j-active")));

  // ---- دارک/لایت مود ----
  const toggleBtn = document.getElementById("jThemeToggle");
  const themeLabel = document.getElementById("jThemeLabel");
  const root = document.documentElement;

  function applyTheme(theme) {
    if (theme === "light") {
      root.classList.add("j-light");
      if (themeLabel) themeLabel.textContent = "Light Mode";
      if (toggleBtn) toggleBtn.classList.add("j-theme-light");
    } else {
      root.classList.remove("j-light");
      if (themeLabel) themeLabel.textContent = "Dark Mode";
      if (toggleBtn) toggleBtn.classList.remove("j-theme-light");
    }
  }

  const savedTheme = localStorage.getItem("jTheme") || "dark";
  applyTheme(savedTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const next = root.classList.contains("j-light") ? "dark" : "light";
      localStorage.setItem("jTheme", next);
      applyTheme(next);
    });
  }
})();
