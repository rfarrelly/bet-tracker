document.getElementById("filter-form").addEventListener("submit", function(event) {
    event.preventDefault();

    let teamFilter = document.getElementById("team-filter").value.toLowerCase();
    let dateFilter = document.getElementById("date-filter").value;

    document.querySelectorAll("#fixtures-table tbody tr").forEach(row => {
        let home = row.cells[2].textContent.toLowerCase();
        let away = row.cells[3].textContent.toLowerCase();
        let date = row.cells[0].textContent;

        if ((teamFilter && !home.includes(teamFilter) && !away.includes(teamFilter)) ||
            (dateFilter && date !== dateFilter)) {
            row.style.display = "none";
        } else {
            row.style.display = "";
        }
    });
});
