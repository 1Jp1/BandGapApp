const inputBtn = document.getElementById("calcButton");
const fileInput = document.getElementById("input-archive");
const optionsSelect = document.getElementById("options-select");
const fileNameArea = document.getElementById("file-name")
const elementSelect = document.getElementById("headers-option")

const inputsArea = document.getElementById("infoArea")
const hihiddenBandGapInput = document.getElementById("hiddenBandGapInput")
const bandGapLowerValue = document.getElementById("lower-bandGap")
const bandGapUpperValue = document.getElementById("upper-bandGap")






inputBtn.addEventListener("click", function () {
    if (fileNameArea.textContent != "Select Any File") {

        inputFile = fileInput.files[0]
        value = elementSelect.value * 2
        option = optionsSelect.value

        const formData =  new FormData();
        formData.append("archive", inputFile);
        formData.append("value",value)
        formData.append("option", option )

        if (optionsSelect.value === "3") {
            if (!bandGapLowerValue.value || !bandGapUpperValue.value) {
                alert("Por favor, completa ambos valores de Band Gap.");
                return;
            }
            
            // Convertir a números para validación adicional
            const lowerValue = parseFloat(bandGapLowerValue.value);
            const upperValue = parseFloat(bandGapUpperValue.value);
            
            if (isNaN(lowerValue) || isNaN(upperValue)) {
                alert("Los valores de Band Gap deben ser números válidos.");
                return;
            }
            
            if (lowerValue >= upperValue) {
                alert("El valor inferior del Band Gap debe ser menor que el superior.");
                return;
            }
            lowerBandGap = bandGapLowerValue.value
            upperBandGap = bandGapUpperValue.value
            
            formData.append("lowerBandGap", lowerBandGap)
            formData.append("upperBandGap", upperBandGap)



        }

        console.log("El valor de value es" , value)

        fetch("http://localhost:5000/graph",{
            method:"POST",
            body:formData
            
        })
        .then(response => response.json()) // Recibir la respuesta como JSON
        .then(result => {
            // Mostrar la gráfica o tabla en el frontend
            if (result.image) {
                // Si se devuelve una imagen (gráfica)
                document.getElementById("grafica-container").innerHTML = `<img src="data:image/png;base64,${result.image}" alt="Gráfica" class = "img-graph">`;
            } else if (result.table) {
                // Si se devuelve una tabla
                document.getElementById("grafica-container").innerHTML = result.table;
            } else if (result.error) {
                // Si hay un error
                console.error("Error:", result.error);
                alert("Ocurrió un error: " + result.error);
            }
        })
        .catch(error => {
            console.error("Error al enviar datos a Flask:", error);
        });
        
    } else {
        alert("Por favor, selecciona un archivo CSV primero.");
    }
});

fileInput.addEventListener("change", function () {
    let fileName = this.files[0] ? this.files[0].name : "Archive Selected";
    document.getElementById("file-name").textContent = fileName;

    const file = this.files[0];
    if (file && file.name.endsWith(".csv")) {
        enviarArchivo(file);
    } else {
        alert("Por favor, selecciona un archivo CSV.");
    }

});

// Función para procesar el CSV
function enviarArchivo(file) {
    let formData = new FormData();
    formData.append("archivo", file);

    

    fetch("http://localhost:5000/read", { // Flask en el puerto 5000
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.headers) {
            console.log("Datos filtrados:", data.headers);
            // Aquí puedes hacer algo con la información, por ejemplo:
            mostrarDatos(data.headers);
        } else {
            console.warn("No se recibieron datos filtrados.");
        }
    })
    .catch(error => {
        console.error("Error al enviar el archivo:", error);
    });
}

// Función para mostrar los datos filtrados en la interfaz
function mostrarDatos(datos) {
    let listOptions = "";
    let contador = 0;

    datos.forEach(dato => {
        listOptions += `<option value="${contador}">${dato}</option>`;
        contador++;
    });

    // Obtener la referencia al elemento 'select'
    const headersOption = document.getElementById("headers-option");

    // Asignar el contenido generado al 'select'
    if (headersOption) { // Verificar que el elemento existe
      headersOption.innerHTML = listOptions;
    } else {
      console.error("Elemento 'headers-option' no encontrado.");
    }
}


optionsSelect.addEventListener("change",function(){

    if(optionsSelect.value === "3"){
        inputsArea.style.flex = '1.5';
        hihiddenBandGapInput.style.display = 'flex';
    }else{
        inputsArea.style.flex = '1';
        hihiddenBandGapInput.style.display = 'none';
    }

})