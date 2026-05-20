(function () {
  const params = new URLSearchParams(window.location.search);
  const src = params.get("src");
  const month = params.get("month");

  if (month) {
    const backLink = document.getElementById("back-link");
    const a = document.createElement("a");
    a.href = "../index.html?month=" + encodeURIComponent(month);
    a.textContent = "← Back to " + Utils.formatMonthAndYearFromFolder(month);
    backLink.appendChild(a);
  }

  if (src) {
    const container = document.getElementById("photo-container");

    const photoFrame = document.createElement("div");
    photoFrame.className = "photo-frame";
    Utils.applyRandomTilt(photoFrame);

    const img = document.createElement("img");
    img.src = "../" + src;
    img.alt = src.split("/").pop();
    img.className = "photo-full";

    photoFrame.appendChild(img);
    container.appendChild(photoFrame);
  }
})();
