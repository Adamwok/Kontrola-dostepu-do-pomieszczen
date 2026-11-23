fetch('/api/health')
    .then(function(response){
        return response.json();
    })
    .then(function(data) {
        document.getElementById("dane").innerHTML = JSON.stringify(data);
    })
    .catch(function(error) {
        console.log("Blad polaczenia z backendem");
        document.getElementById("dane").innerHTML = "Błąd połączenia z backendem"
    })