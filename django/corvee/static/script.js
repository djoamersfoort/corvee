$(document).ready(function() {
  $("#switch").change(function() {
    location.href = "/main/"+(day == "saturday" ? "friday" : "saturday");
  });
});
