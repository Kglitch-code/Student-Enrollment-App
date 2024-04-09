function jsonToTable(elementID, json){
    if(typeof json === 'undefined'){
        console.log("undefined JSON")
    }
    else{
        const dict = JSON.parse(json);
        let table = document.createElement("table");

        //Headers
        let headers = Object.keys(dict[0]);
        let headerRow = document.createElement("tr");
        for(let i = 0; i < headers.length; i++){
            let header = document.createElement("th");
            let text = document.createTextNode(headers[i]);
            header.appendChild(text);
            header.setAttribute("header", headers[i]);

            headerRow.appendChild(header);
        }
        table.appendChild(headerRow);

        //Rows
        for(let i = 0; i < dict.length; i++){
            let row = document.createElement("tr");
            //Add row distinction for colors
            if (i%2 ==1){
                row.setAttribute("class", "oddRow");
            }
            else{
                row.setAttribute("class", "evenRow");
            }
            for(let j in headers){
                let key = document.createElement("td");
                let text = document.createTextNode(dict[i][headers[j]]);
                key.appendChild(text); //Add the text to the td
                row.appendChild(key); //Add the td to the table
            }
            table.appendChild(row);
        }
        document.getElementById(elementID).appendChild(table);
    }
}

//Takes the column with the header "Header" in the table with id elementID
function addLinks(elementID, Header, IDList){
    const cIDs = JSON.parse(IDList);
    let tableDiv = document.getElementById(elementID);
    let table = tableDiv.children[0]
    let headers = tableDiv.getElementsByTagName("th");
    columnNum = -1;
    for(let i = 0; i < headers.length; i++){
        if(headers[i].getAttribute("header") == Header){
            columnNum = i;
        }
    }
    if(columnNum != -1){
        for (let i = 1; i < table.rows.length; i++) {
            let row = table.rows[i];
            if (row.cells.length > columnNum) {
                let cell = row.cells[columnNum]
                let text = cell.innerHTML
                cell.innerHTML = ""
                let ref = document.createElement("a")
                ref.innerHTML = text
                ref.setAttribute("href", "/teacher/dashboard/" + cIDs[i-1].ID)
                cell.appendChild(ref);
            }
        }
    }
    else{
        console.log("Header not Found");
    }
}

function showClassData(elementID){
    document.getElementById(elementID).innerHTML = "Classes";
    jsonToTable(elementID, classinfodata);
}

function showGradesData(elementID){
    document.getElementById(elementID).innerHTML = "Grades";
    jsonToTable(elementID, gradeList);
}

window.onload = function() {
    return
};