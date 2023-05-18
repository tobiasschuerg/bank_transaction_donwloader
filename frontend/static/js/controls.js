// On page load
document.addEventListener("DOMContentLoaded", (event) => {
  if (localStorage.getItem("creditorAccountChecked") === "true") {
    document.getElementById("toggleCreditorAccount").click();
  }
  if (localStorage.getItem("debtorAccountChecked") === "true") {
    document.getElementById("toggleDebtorAccount").click();
  }

  document
    .getElementById("toggleCreditorAccount")
    .addEventListener("change", function () {
      localStorage.setItem("creditorAccountChecked", this.checked);
    });

  document
    .getElementById("toggleDebtorAccount")
    .addEventListener("change", function () {
      localStorage.setItem("debtorAccountChecked", this.checked);
    });
});
