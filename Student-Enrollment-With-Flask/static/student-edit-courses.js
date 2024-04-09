function jsonToTable(elementID, json) {
    if (typeof json === 'undefined') {
        console.log("undefined JSON")
    } else {
        const dict = JSON.parse(json);
        let table = document.createElement("table");

        //Headers
        let headers = Object.keys(dict[0]);
        let headerRow = document.createElement("tr");
        for (let i = 0; i < headers.length; i++) {
            let header = document.createElement("th");
            let text = document.createTextNode(headers[i]);
            header.appendChild(text);
            headerRow.appendChild(header);
        }
        table.appendChild(headerRow);

        //Rows
        for (let i = 0; i < dict.length; i++) {
            let row = document.createElement("tr");
            //Add row distinction for colors
            if (i % 2 == 1) {
                row.setAttribute("class", "oddRow");
            } else {
                row.setAttribute("class", "evenRow");
            }
            for (let j = 0; j < headers.length; j++) {
                let key = document.createElement("td");
                let text = document.createTextNode(dict[i][headers[j]]);
                key.appendChild(text); //Add the text to the td
                row.appendChild(key); //Add the td to the table
            }

            // Add Add/Delete buttons
            let buttonCell = document.createElement("td");
            let addButton = document.createElement("button");
            addButton.textContent = "Add";
            addButton.onclick = function () {
                addClass(dict[i]['Class Name']); // Call addClass function with class name as parameter
            };
            buttonCell.appendChild(addButton);

            let deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.onclick = function () {
                deleteClass(dict[i]['Class Name']); // Call deleteClass function with class name as parameter
            };
            buttonCell.appendChild(deleteButton);

            row.appendChild(buttonCell);

            // Append row to table body
            table.appendChild(row);
        }
        document.getElementById(elementID).appendChild(table);
    }
}

function showClassData(elementID) {
    document.getElementById(elementID).innerHTML = "Classes";
    jsonToTable(elementID, classinfodata);
}

function addClass(className) {
    // Implement logic to add class (send data to server using AJAX or form submission)
    alert("Add class: " + className);
}

function deleteClass(className) {
    // Implement logic to delete class (send data to server using AJAX or form submission)
    alert("Delete class: " + className);
}

window.onload = function () {
    showClassData("allClassesTable");
};
