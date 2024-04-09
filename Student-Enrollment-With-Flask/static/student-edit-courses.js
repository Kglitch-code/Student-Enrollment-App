function jsonToTable(elementID, json) {
    if (typeof json === 'undefined') {
        console.log("undefined JSON")
    } else {
        const dict = JSON.parse(json);
        const ids = JSON.parse(classIDS);
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
                addClass(dict[i]['Class Name'], ids[i]["ID"]); // Call addClass function with class name as parameter
            };
            buttonCell.appendChild(addButton);

            let deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.onclick = function () {
                deleteClass(dict[i]['Class Name'], ids[i]["ID"]); // Call deleteClass function with class name as parameter
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

function addClass(className, classID) {
    // Send data to server to add class using fetch API
    fetch('/student/dashboard/all-classes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            option: 'add',
            class_id: classID
        })
    })
    .then(response => {
        if (response.ok) {
            // Handle success response
            console.log("Class added: " + className);
            // Reload the page to reflect the changes
            updateStudentPage();
        } else {
            // Handle error response
            console.log("Failed to add class: " + className);
        }
    })
    .catch(error => {
        // Handle network error
        // console.error('Error adding class:', error);
        console.log("Failed to add class: " + className);
    });
}

function updateStudentPage() {
    window.location.replace("/student/dashboard/all-classes");
    // Fetch updated class data from the server
    fetch('/student/dashboard')
    console.log(response)
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch class data');
        }
        return response.json();
    })
    .then(data => {
        // Update classinfodata with the newly fetched data
        classinfodata = data;
        // Show updated class data on student.html page
        showClassData("allClassesTable");
    })
    .catch(error => {
        // console.error('Error updating student page:', error);
        alert("Failed to update student page");
    });
}

function deleteClass(className, classID) {
    // Send data to server to add class using fetch API
    fetch('/student/dashboard/all-classes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            option: 'delete',
            class_id: classID
        })
    })
    .then(response => {
        if (response.ok) {
            // Handle success response
            console.log("Class added: " + className);
            // Reload the page to reflect the changes
            updateStudentPage();
        } else {
            // Handle error response
            console.log("Failed to add class: " + className);
        }
    })
    .catch(error => {
        // Handle network error
        // console.error('Error adding class:', error);
        console.log("Failed to add class: " + className);
    });
}

window.onload = function () {
    showClassData("allClassesTable");
};
