function calculateRisk() {
    const startRisk = parseFloat(document.getElementById('startRisk').value);
    const result = document.getElementById('result').value;
    const cycleNumber = parseInt(document.getElementById('cycleNumber').value);
    let currentRisk = startRisk;
    let message = "";

    if (result === "zero") {
        message = `Initial risk is set to ${currentRisk}%.`;
    } else if (result === "win") {
        currentRisk += 0.25;
        message = `You won! Risk increased to ${currentRisk}%.`;
    } else if (result === "loss") {
        currentRisk = Math.max(0.5, currentRisk - 0.25);
        message = `You lost. Risk reduced to ${currentRisk}%.`;

        if (currentRisk <= 0.5) {
            message += " Stop trading, take a break and try again tomorrow.";
        }
    }

    document.getElementById('riskOutput').innerText = message;
}
//welcome.js