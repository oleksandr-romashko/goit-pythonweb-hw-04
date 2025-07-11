document.addEventListener("DOMContentLoaded", () => {
  const elements = document.querySelectorAll(".utc-timestamp");
  const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];

  elements.forEach(el => {
    const utcString = el.dataset.utc;
    if (utcString) {
      const date = new Date(utcString);
      if (!isNaN(date)) {
        const month = months[date.getMonth()];
        const day = String(date.getDate()).padStart(2, "0");
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");

        el.textContent = `${month} ${day}, ${year} ${hours}:${minutes}`;
      } else {
        el.textContent = "Invalid date";
      }
    }
  });
});
