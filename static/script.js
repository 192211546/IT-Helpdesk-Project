// Toggle sidebar on mobile
document.getElementById("menuBtn").addEventListener("click", function () {
  document.getElementById("sidebar").classList.toggle("open");
});

// Auto-submit the status form when a new status is chosen
document.querySelectorAll(".status-select").forEach(function (sel) {
  sel.addEventListener("change", function () { sel.form.submit(); });
});

// Simple client-side validation (the server validates too)
var form = document.getElementById("ticketForm");
if (form) {
  form.addEventListener("submit", function (e) {
    var missing = Array.from(form.querySelectorAll("[required]")).some(function (f) {
      return !f.value.trim();
    });
    if (missing) {
      e.preventDefault();
      document.getElementById("formError").textContent = "Please fill in all required fields.";
    }
  });
}

// Hide flash messages after 4 seconds
setTimeout(function () {
  document.querySelectorAll(".alert").forEach(function (a) { a.style.display = "none"; });
}, 4000);
