(function () {

  const now = new Date();
  const currentMonth = String(now.getMonth() + 1).padStart(2, "0");
  const currentYear = now.getFullYear();
  const currentFolder = currentMonth + "-" + currentYear;

  const queryParams = new URLSearchParams(window.location.search);
  const folder = queryParams.get("month") || currentFolder;

  const isArchive = folder !== currentFolder;
  document.getElementById("intro-current").style.display = isArchive ? "none" : "";
  document.getElementById("intro-archive").style.display = isArchive ? "" : "none";
  document.getElementById("month-title").textContent = Utils.formatMonthAndYearFromFolder(folder);

  const container = document.getElementById("photos");

  fetch(folder + "/manifest.json")
    .then(function (response) {
      if (!response.ok) {
        throw new Error("No photos found for this month.");
      }
      return response.json();
    })
    .then(function (data) {
      if (!data.photos || data.photos.length === 0) {
        container.textContent = "No photos for this month yet.";
        return;
      }

      data.photos.forEach(function (filename) {
        const photoFrame = document.createElement("div");
        photoFrame.className = "photo-frame";
        const tilt = (Math.random() * 6 - 3).toFixed(2);
        photoFrame.style.transform = "rotate(" + tilt + "deg)";

        const img = document.createElement("img");
        img.src = folder + "/" + filename;
        img.alt = filename;
        img.className = "photo-thumb";

        photoFrame.appendChild(img);
        container.appendChild(photoFrame);
      });
    })
    .catch(function () {
      container.textContent = "No photos available for this month.";
    });

  fetch("months-manifest.json")
    .then(function (response) { return response.json(); })
    .then(function (data) {
      const months = data.months || [];
      const idx = months.indexOf(folder);
      if (idx === -1) return;

      const prevFolder = idx > 0 ? months[idx - 1] : null;
      const nextFolder = idx < months.length - 1 ? months[idx + 1] : null;

      const nav = document.getElementById("navigation");
      nav.style.marginTop = "16px";

      if (prevFolder) {
        const prevBtn = document.createElement("a");
        prevBtn.href = "index.html?month=" + prevFolder;
        prevBtn.textContent = "← " + Utils.formatMonthAndYearFromFolder(prevFolder);
        prevBtn.style.marginRight = "16px";
        nav.appendChild(prevBtn);
      }

      if (nextFolder) {
        const nextBtn = document.createElement("a");
        nextBtn.href = "index.html?month=" + nextFolder;
        nextBtn.textContent = Utils.formatMonthAndYearFromFolder(nextFolder) + " →";
        nav.appendChild(nextBtn);
      }
    });
})();
