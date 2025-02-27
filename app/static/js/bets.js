document.addEventListener("DOMContentLoaded", function() {
    loadBets();
    
    document.getElementById("bet-form").addEventListener("submit", function(event) {
        event.preventDefault();
        
        let betData = {
            user_id: document.getElementById("user-id").value,
            bet_type: document.getElementById("bet-type").value,
            stake: parseFloat(document.getElementById("stake").value),
            odds: parseFloat(document.getElementById("odds").value),
            selections: document.getElementById("selections").value
        };

        fetch("/bets", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(betData)
        }).then(response => response.json())
          .then(() => loadBets());
    });
});

function loadBets() {
    fetch("/bets")
        .then(response => response.json())
        .then(data => {
            let betsTable = document.querySelector("#bets-table tbody");
            betsTable.innerHTML = "";
            data.forEach(bet => {
                let row = betsTable.insertRow();
                row.innerHTML = `
                    <td>${bet.user_id}</td>
                    <td>${bet.bet_type}</td>
                    <td>${bet.stake}</td>
                    <td>${bet.odds}</td>
                    <td>${bet.selections}</td>
                    <td><button onclick="deleteBet(${bet.id})">Delete</button></td>
                `;
            });
        });
}

function deleteBet(id) {
    fetch(`/bets/${id}`, { method: "DELETE" })
        .then(() => loadBets());
}
