(function () {

  var list = document.getElementById("months");

  fetch("../months-manifest.json")
    .then(function (response) {
      if (!response.ok) {
        throw new Error("Could not load months manifest.");
      }
      return response.json();
    })
    .then(function (data) {
      if (!data.months || data.months.length === 0) {
        list.textContent = "No months available yet.";
        return;
      }

      // Show most recent first
      var months = data.months.slice().reverse();

      months.forEach(function (folder) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = "../index.html?month=" + folder;
        a.textContent = Utils.formatMonthAndYearFromFolder(folder);
        li.appendChild(a);
        list.appendChild(li);
      });
    })
    .catch(function () {
      list.textContent = "Could not load archive.";
    });
})();
