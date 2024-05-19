// Ensure the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    var dataDiv = document.getElementById('data');
    var totalIncome = parseFloat(dataDiv.getAttribute('data-total-income'));
    var totalExpenses = parseFloat(dataDiv.getAttribute('data-total-expenses'));
    var totalAssets = parseFloat(dataDiv.getAttribute('data-total-assets'));
    var totalLiabilities = parseFloat(dataDiv.getAttribute('data-total-liabilities'));

    var ctx = document.getElementById('incomeExpenseChart').getContext('2d');
    var incomeExpenseChart = new Chart(ctx, {
        type: 'bar', // You can change the type to 'line', 'pie', etc.
        data: {
            labels: ['TOTAL INCOME', 'TOTAL EXPENSES'],
            datasets: [{
                label: 'Amount',
                data: [totalIncome, totalExpenses],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(255, 99, 132, 0.2)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // New chart code...
    var ctxNetWorth = document.getElementById('netWorthChart').getContext('2d');
    var netWorthChart = new Chart(ctxNetWorth, {
        type: 'pie',
        data: {
            labels: ['Total Assets', 'Total Liabilities'],
            datasets: [{
                label: 'Net Worth',
                data: [totalAssets, totalLiabilities],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 99, 132, 0.6)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });            
});