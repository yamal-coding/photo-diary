var Utils = Utils || {};

Utils.MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

Utils.formatMonthAndYearFromFolder = function (f) {
  const parts = f.split("-");
  const monthIndex = parseInt(parts[0], 10) - 1;
  const year = parts[1];

  return Utils.MONTH_NAMES[monthIndex] + " " + year;
};

Utils.renderFooter = function () {
  const footer = document.createElement("footer");
  footer.className = "footer";
  footer.textContent = "Made by Yamal with love 📸 All the photos taken are mine";
  document.body.appendChild(footer);
};
