fetch('/api/healthy')
    .then(function(response){
        return response.json();
    })
    .then(function(data) {
        document.getElementById("dane").innerHTML = JSON.stringify(data);
    })
    .catch(function(error) {
        console.log("Blad polaczenia");
        document.getElementById("dane").innerHTML = "Brak danych"
    })