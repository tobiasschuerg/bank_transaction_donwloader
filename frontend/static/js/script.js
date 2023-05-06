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
  const minConfidence = 0.2;
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
        transactionCreditor +
          " " +
          transactionDebtor +
          " " +
          transactionDescription
      );
      if (
        suggestedCategoryData &&
        suggestedCategoryData.confidence > minConfidence
      ) {
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
        suggestedCategoryData.confidence > minConfidence
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

function submitForm() {
    document.getElementById('filter-form').submit();
}

function resetDates() {
    document.getElementById('start_date').value = '';
    document.getElementById('end_date').value = '';
    submitForm();
}

    function editDescription(element, transactionId) {
    // Check if the input element is already present
    if (element.querySelector('input')) {
      return;
    }

    const currentValue = element.textContent.trim();
    element.innerHTML = `
      <input type="text" class="form-control" value="${currentValue}" onfocusout="submitDescription(this, '${transactionId}', false, '${currentValue}')" />
    `;

    const inputElement = element.querySelector('input');
    inputElement.focus();

    // Add event listeners for the Escape and Enter keys
    inputElement.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        // Cancel editing and restore the original description
        element.textContent = currentValue;
      } else if (event.key === 'Enter') {
        event.preventDefault(); // Prevent form submission on pressing Enter
        submitDescription(inputElement, transactionId, true, currentValue);
      }
    });
  }

  function submitDescription(element, transactionId, forceSubmit, originalDescription) {
    const newDescription = element.value.trim();

    // Don't save if the input is blank and forceSubmit is false
    if (!newDescription && !forceSubmit) {
      element.parentElement.textContent = originalDescription;
      return;
    }

    // Make an AJAX request to the update transaction description route
    fetch(`/transaction/${transactionId}/description`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ description: newDescription }),
    })
      .then((response) => {
        if (response.status === 204) {
          // Update the description cell content
          element.parentElement.textContent = newDescription;
        } else {
          console.error('Failed to update the description');
        }
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }