let selectedRow
let selectedRowNum

function deselectFeature(elementID, i){
    if(selectedRow){
        let elements = document.querySelectorAll('.' + selectedRow);
        elements.forEach(function(element) {
            element.style.backgroundColor = ''; //Remove Styles for Existing row
        });
        
        let inp=document.getElementById("inputValue")
        let form = inp.parentElement;
        let inpText = inp.getAttribute("pastValue")
        let TD = form.parentElement;
        inp.remove();
        TD.innerHTML= inpText;
        addOnClicks("ClassTable", "Grade", "selectGrade(", "Grade");

        selectedRow = "";
        selectedRowNum = "";
        return true;
    }
    return false
}

function selectFeature(elementID, i) { 
    deselectFeature(elementID, i)

    let oldselectedRow = selectedRow;

    selectedRow=(elementID + i);
    selectedRowNum = i;
    
    let elements = document.querySelectorAll('.' +selectedRow);
    elements.forEach(function(element) {
        element.style.backgroundColor = 'white'; // Select Current Row
    });

    if(selectedRow != oldselectedRow){
        selectedTD = document.getElementById(selectedRow);
        //Specific to this function
        let studentID = selectedTD.parentElement.children[1].innerHTML;

        let innertext = selectedTD.innerHTML;
        selectedTD.innerHTML = "";
        let form = document.createElement("form");
        form.setAttribute("action", "/teacher/dashboard/"+classID)
        form.setAttribute("method", "post")
        let inp = document.createElement("input");
        inp.setAttribute("value", innertext);
        inp.setAttribute("pastValue", innertext);
        inp.setAttribute("id", "inputValue");
        inp.setAttribute("name", "new_grade");
        let hidden = document.createElement("input");
        hidden.setAttribute("type", "hidden");
        hidden.setAttribute("value", studentID);
        hidden.setAttribute("id", "studentIDInput");
        hidden.setAttribute("name", "student_id");
        let button = document.createElement("input");
        button.setAttribute("type", "submit");
        button.setAttribute("value", "Submit Grade Change");
        button.setAttribute("id", "buttonInput");
        form.appendChild(inp);
        form.appendChild(hidden);
        form.appendChild(button);
        selectedTD.appendChild(form)
        inp.focus();
        inp.select();

        selectedTD.setAttribute("onClick", "")
    }
}

function addDeselectButton(){
    if(1)
    return
}

//Select a grade to edit
function selectGrade(num){
    selectFeature("Grade", num)
}

//Create a table under the div with id element id using the data found in json
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

//Add onClick Function to a column
//Takes in a string function, closes the function with "'i')"
function addOnClicks(elementID, Header, functionName, functionid=null){
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
                cell.setAttribute("onclick", functionName + i + ")")
                if(functionid!= null){
                    cell.setAttribute("id", functionid+i)
                }
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