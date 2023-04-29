document.getElementById("bankName").addEventListener("change", function () {
    document.getElementById("bank-filter-form").submit();
});

// Toggle Creditor Account column visibility
document.getElementById("toggleCreditorAccount").addEventListener("change", function () {
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
document.getElementById("toggleDebtorAccount").addEventListener("change", function () {
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

    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});