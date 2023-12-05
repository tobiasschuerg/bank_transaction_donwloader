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

function submitFormWithCategoryMissing() {
  let checkbox = document.getElementById("toggleNoCategory");
  let url = new URL(window.location.href);

  // If the checkbox is checked, add 'category_missing=true' to the URL
  if (checkbox.checked) {
    url.searchParams.set("category", "null");
  } else {
    // If the checkbox is not checked, remove the 'category_missing' parameter from the URL
    url.searchParams.delete("category");
  }

  // Reload the page with the new URL
  window.location.href = url.toString();
}
