function valueUpdate() {
    var weight, price
    weight = parseFloat(document.getElementById("calcweight").value).toFixed(2);

    console.log("Updating Calculator Values.")
    price = 0.00

    if(weight >= 0 && weight <= 9.9) {
        price = "$" + weight * 0.50
    } else if(weight >= 10 && weight < 25) {
        price = "$" + weight
    } else if(weight >= 25 && weight < 50) {
        price = "$" + weight * 2
    } else if(weight >= 50) {
        price = "Too Heavy!"
    } else {
        price = "0"
    }

    document.getElementById("calcprice").value = price
    console.log(weight, price)
}