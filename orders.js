    //  async function fetchOrders() {
    //         try {
    //             const response = await fetch('/get_orders'); // Fetch orders from Flask API
    //             const data = await response.json();

    //             const ordersTable = document.getElementById('orders-body');
    //             const noOrdersMessage = document.getElementById('no-orders');

    //             ordersTable.innerHTML = ""; // Clear previous entries

    //             if (data.orders.length === 0) {
    //                 noOrdersMessage.style.display = "block"; // Show "No orders" message
    //                 return;
    //             }

    //             noOrdersMessage.style.display = "none"; // Hide "No orders" message

    //             data.orders.forEach(order => {
    //                 const row = document.createElement("tr");

    //                 row.innerHTML = `
    //                     <td>${order.id}</td>
    //                     <td>${order.name}</td>
    //                     <td>${order.email}</td>
    //                     <td>${order.address}</td>
    //                     <td>$${order.total_price}</td>
    //                 `;

    //                 ordersTable.appendChild(row);
    //             });
    //         } catch (error) {
    //             console.error("Error fetching orders:", error);
    //             document.getElementById("orders-body").innerHTML = "<tr><td colspan='5'>Failed to load orders</td></tr>";
    //         }
    //     }

    //     window.onload = fetchOrders; // Fetch orders when page loads



    document.addEventListener("DOMContentLoaded", function () {
        fetchOrders();
        fetchTotalSales();
        fetchTotalOrders();
        fetchTopOrders();
    });
    
    async function fetchOrders() {
        try {
            const response = await fetch('/get_orders');
            const data = await response.json();
    
            const ordersTable = document.getElementById('orders-body');
            ordersTable.innerHTML = "";
    
            if (data.orders.length === 0) {
                ordersTable.innerHTML = "<tr><td colspan='5' class='text-center'>No orders found.</td></tr>";
                return;
            }
    
            data.orders.forEach(order => {
                ordersTable.innerHTML += `
                    <tr>
                        <td>${order.id}</td>
                        <td>${order.name}</td>
                        <td>${order.email}</td>
                        <td>${order.address}</td>
                        <td>$${order.total_price.toFixed(2)}</td>
                    </tr>`;
            });
        } catch (error) {
            console.error("Error fetching orders:", error);
        }
    }
    
    async function fetchTotalSales() {
        const response = await fetch("/total_sales");
        const data = await response.json();
        document.getElementById("total-sales").textContent = `$${data.total_sales.toFixed(2)}`;
    }
    
    async function fetchTotalOrders() {
        const response = await fetch("/total_orders");
        const data = await response.json();
        document.getElementById("total-orders").textContent = data.total_orders;
    }
    
    async function fetchTopOrders() {
        const response = await fetch("/top_orders");
        const data = await response.json();
    
        const topOrdersTable = document.getElementById('top-orders-body');
        topOrdersTable.innerHTML = "";
    
        if (data.top_orders.length === 0) {
            topOrdersTable.innerHTML = "<tr><td colspan='5' class='text-center'>No top orders found.</td></tr>";
            return;
        }
    
        data.top_orders.forEach(order => {
            topOrdersTable.innerHTML += `
                <tr>
                    <td>${order.id}</td>
                    <td>${order.name}</td>
                    <td>${order.email}</td>
                    <td>${order.address}</td>
                    <td>$${order.total_price.toFixed(2)}</td>
                </tr>`;
        });
    }
    

    async function fetchTotalSales() {
        try {
            const response = await fetch("/total_sales");
            const data = await response.json();
            document.getElementById("total-sales").textContent = `$${parseFloat(data.total_sales).toFixed(2)}`;
        } catch (error) {
            console.error("Error fetching total sales:", error);
        }
    }
    
    async function fetchTotalOrders() {
        try {
            const response = await fetch("/total_orders");
            const data = await response.json();
            document.getElementById("total-orders").textContent = data.total_orders;
        } catch (error) {
            console.error("Error fetching total orders:", error);
        }
    }
    
    document.addEventListener("DOMContentLoaded", function () {
        fetchOrders();
        fetchTotalSales();  // ✅ Now correctly updates total sales
        fetchTotalOrders(); // ✅ Now correctly updates total orders
        fetchTopOrders();
    });
    