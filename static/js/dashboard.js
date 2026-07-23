document.addEventListener("DOMContentLoaded", function () {
  function updateClock() {
    const now = new Date();
    const time = now.toLocaleTimeString("zh-TW", { hour12: false });
    const date = now.toLocaleDateString("zh-TW", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      weekday: "short"
    });

    const liveTime = document.getElementById("liveTime");
    const liveDate = document.getElementById("liveDate");
    const welcomeDate = document.getElementById("welcomeDate");

    if (liveTime) liveTime.textContent = time;
    if (liveDate) liveDate.textContent = date;
    if (welcomeDate) {
      welcomeDate.textContent = `今天是 ${date}，祝您有個美好的一天！`;
    }
  }

  updateClock();
  window.setInterval(updateClock, 1000);

  const chartCanvas = document.getElementById("leaveTrendChart");
  if (chartCanvas && window.Chart) {
    new Chart(chartCanvas, {
      type: "line",
      data: {
        labels: ["7/1", "7/5", "7/10", "7/15", "7/20", "7/25", "7/31"],
        datasets: [{
          label: "請假時數",
          data: [2, 5, 3, 8, 10, 5, 1],
          borderColor: "#48a85f",
          backgroundColor: "rgba(72,168,95,.13)",
          fill: true,
          tension: 0.35,
          pointRadius: 3,
          pointHoverRadius: 5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: "#718096", font: { size: 10 } }
          },
          y: {
            beginAtZero: true,
            grid: { color: "#e9f1ea" },
            ticks: { color: "#718096", font: { size: 10 } }
          }
        }
      }
    });
  }

  const sectionLinks = document.querySelectorAll(
    'a[href$="#pending"], a[href$="#late"], a[href="#pending"], a[href="#late"]'
  );

  if (!document.getElementById("section-navigation-fix-styles")) {
    const style = document.createElement("style");
    style.id = "section-navigation-fix-styles";
    style.textContent = `
      #pending, #late {
        scroll-margin-top: 96px;
        transition: box-shadow .25s ease, border-color .25s ease,
                    background-color .25s ease, transform .25s ease;
      }
      .section-navigation-highlight {
        border-color: #63bd77 !important;
        box-shadow:
          0 0 0 4px rgba(72, 168, 95, .15),
          0 16px 40px rgba(40, 90, 55, .13) !important;
        transform: translateY(-2px);
      }
    `;
    document.head.appendChild(style);
  }

  function highlightSection(section) {
    document.querySelectorAll(".section-navigation-highlight").forEach((element) => {
      element.classList.remove("section-navigation-highlight");
    });

    section.classList.add("section-navigation-highlight");

    window.setTimeout(() => {
      section.classList.remove("section-navigation-highlight");
    }, 1800);
  }

  function scrollToSection(sectionId, updateHash = true) {
    const section = document.getElementById(sectionId);
    if (!section) return false;

    section.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });

    highlightSection(section);

    if (updateHash) {
      window.history.replaceState(null, "", `#${sectionId}`);
    }

    return true;
  }

  sectionLinks.forEach((link) => {
    link.addEventListener("click", function (event) {
      const url = new URL(link.href, window.location.href);
      const sectionId = url.hash.replace("#", "");

      if (!["pending", "late"].includes(sectionId)) return;

      const targetExists = document.getElementById(sectionId);
      const samePath = url.pathname === window.location.pathname;

      if (!samePath || !targetExists) return;

      event.preventDefault();

      const mobileNav = document.getElementById("mobileNav");
      const isOffcanvasVisible =
        mobileNav &&
        mobileNav.classList.contains("show") &&
        window.bootstrap &&
        window.bootstrap.Offcanvas;

      if (isOffcanvasVisible) {
        const instance =
          window.bootstrap.Offcanvas.getInstance(mobileNav) ||
          window.bootstrap.Offcanvas.getOrCreateInstance(mobileNav);

        mobileNav.addEventListener(
          "hidden.bs.offcanvas",
          function () {
            scrollToSection(sectionId);
          },
          { once: true }
        );

        instance.hide();
      } else {
        scrollToSection(sectionId);
      }
    });
  });

  const initialSectionId = window.location.hash.replace("#", "");
  if (["pending", "late"].includes(initialSectionId)) {
    window.setTimeout(() => {
      scrollToSection(initialSectionId, false);
    }, 250);
  }
});
