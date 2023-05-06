document.getElementById("bankName").addEventListener("change", function () {
  document.getElementById("bank-filter-form").submit();
});

// Toggle Creditor Account column visibility
document
  .getElementById("toggleCreditorAccount")
  .addEventListener("change", function () {
    const display = this.checked ? "" : "none";
    const cells = document.getElementsByClassName("creditor-account");
    for (let i = 0; i < cells.length; i++) {
      cells[i].style.display = display;
    }
  });

function hideColumn(columnClass) {
  const display = "none";
  const cells = document.getElementsByClassName(columnClass);
  for (let i = 0; i < cells.length; i++) {
    cells[i].style.display = display;
  }
}

// Toggle Debtor Account column visibility
document
  .getElementById("toggleDebtorAccount")
  .addEventListener("change", function () {
    const display = this.checked ? "" : "none";
    const cells = document.getElementsByClassName("debtor-account");
    for (let i = 0; i < cells.length; i++) {
      cells[i].style.display = display;
    }
  });

// Format date according to user's locale
const dateCells = document.querySelectorAll("td[data-date]");
const dateFormatter = new Intl.DateTimeFormat(navigator.language);

for (const cell of dateCells) {
  const date = new Date(cell.getAttribute("data-date"));
  cell.textContent = dateFormatter.format(date);
}

// Initialize Bootstrap tooltips
document.addEventListener("DOMContentLoaded", function () {
  // Hide columns on page load
  hideColumn("creditor-account");
  hideColumn("debtor-account");

  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

document.addEventListener("DOMContentLoaded", function () {
  // Add event listeners for save-category buttons
  fetchCategories();
  const saveCategoryButtons = document.querySelectorAll(".save-category");
  saveCategoryButtons.forEach((button) => {
    button.addEventListener("click", function (event) {
      const selectElement = event.target.previousElementSibling;
      const category = selectElement.value;
      const transactionId =
        event.target.parentElement.parentElement.firstElementChild.innerText;
      saveCategory(transactionId, category);
    });
  });
});

async function fetchCategories() {
  const response = await fetch("/categories");
  const categories = await response.json();
  const categoryDropdowns = document.querySelectorAll(".category-select");
  categoryDropdowns.forEach(async (dropdown) => {
    const transactionDescription = dropdown.dataset.description;
    const transactionCreditor = dropdown.dataset.creditor;
    const transactionDebtor = dropdown.dataset.debtor;
    let suggestedCategoryData = null;

    if (transactionDescription) {
      suggestedCategoryData = await getCategorySuggestion(
        transactionCreditor + " " + transactionDebtor + " " + transactionDescription
      );
      if (suggestedCategoryData && suggestedCategoryData.confidence > 0.4) {
        dropdown.classList.add("suggested-category");
      }
    }

    categories.forEach((categoryObj) => {
      const option = document.createElement("option");
      option.value = categoryObj.id;
      option.innerText = categoryObj.category;
      dropdown.appendChild(option);

      if (
        suggestedCategoryData &&
        suggestedCategoryData.suggested_category === categoryObj.category &&
        suggestedCategoryData.confidence > 0.2
      ) {
        console.log("selected", transactionDescription, suggestedCategoryData);
        option.selected = true;
      }
    });
  });
}

async function saveCategory(transactionId, categoryId) {
  console.log("category id:", categoryId);
  const response = await fetch(`/transaction/${transactionId}/category`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ category_id: categoryId }),
  });

  if (response.ok) {
    location.reload();
  } else {
    console.error("Failed to save category");
  }
}

async function getCategorySuggestion(transactionDescription) {
  const formData = new FormData();
  formData.append("transaction", transactionDescription);

  const response = await fetch("http://127.0.0.1:5001/api/suggest_category", {
    method: "POST",
    body: formData,
  });

  if (response.ok) {
    const data = await response.json();
    return data;
  } else {
    console.error("Failed to fetch category suggestion");
    return null;
  }
}
