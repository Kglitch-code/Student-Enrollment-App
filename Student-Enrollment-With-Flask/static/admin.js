let selectedRow = "";
let selectedFeature = "";
let selectedTable = "";
let selectedRowNum = "";
let selectedFeatureNum = "";

document.addEventListener('click', function(event) {
    console.log(event);
    var clickedElement = event.target;
    var onclickAttribute = clickedElement.getAttribute('onclick');
    
    if (onclickAttribute !== null) {
        console.log('The onclick function activated by the click:', onclickAttribute);
        // You can perform further actions based on the onclick function if needed
    } else {
        console.log('No onclick function was activated by the click.');
    }
});

function deselectFeature(elementID, i, j){
    if(selectedRow){
        let elements = document.querySelectorAll('.' + selectedRow);
        elements.forEach(function(element) {
            element.style.backgroundColor = ''; //Remove Styles for Existing row
        });
        
        let inp=document.getElementById("inputValue")
        let inpText = inp.getAttribute("pastValue")
        let TD = inp.parentElement;
        inp.remove();
        TD.innerHTML= inpText;

        selectedRow = "";
        selectedFeature = "";
        selectedTable = "";
        selectedRowNum = "";
        selectedFeatureNum = "";
        return true;
    }
    return false
}

// function deselectFeature(){
//     deselectFeature(selectedTable, selectedRowNum, selectedFeatureNum)
//     return
// }

function selectFeature(elementID, i, j) { 
    deselectFeature(elementID, i, j)

    oldselectedFeature = selectedFeature;

    selectedRow=(elementID + "row" + i);
    selectedFeature = (elementID+ "row"+i+"."+j);
    selectedTable = elementID;
    selectedRowNum = i;
    selectedFeatureNum = j;

    
    let elements = document.querySelectorAll('.' + elementID + "row" + i);
    elements.forEach(function(element) {
        element.style.backgroundColor = 'white'; // Select Current Row
    });

    if(selectedFeature != oldselectedFeature){
        selectedTD = document.getElementById(selectedFeature);

        let innertext = selectedTD.innerHTML;
        selectedTD.innerHTML = "";
        inp = document.createElement("input");
        inp.setAttribute("value", innertext);
        inp.setAttribute("pastValue", innertext);
        inp.setAttribute("id", "inputValue");
        selectedTD.appendChild(inp);
        inp.focus();
        inp.select();
    }
}

/*
Create a json as a child node of the element with ID "elementID" from the json stored in the string json
No output values, it just directly edits the node in the document
*/
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
                key.setAttribute("class", elementID+"row"+i);
                key.setAttribute("id", elementID+ "row"+i+"."+j);
                key.setAttribute("onclick", "selectFeature(\""+elementID+"\"," + i+","+j+ ")");
                key.appendChild(text); //Add the text to the td
                row.appendChild(key); //Add the td to the table
            }
            table.appendChild(row);
        }
        document.getElementById(elementID).appendChild(table);
    }
}

/*
Adds the data to the user table
*/
function showUserData(elementID){
    document.getElementById(elementID).innerHTML = "Users";
    jsonToTable(elementID, usersdata);
}

function showClassData(elementID){
    document.getElementById(elementID).innerHTML = "Classes";
    jsonToTable(elementID, classesdata);
}

function showClassEnrollmentData(elementID){
    document.getElementById(elementID).innerHTML = "Class Enrollments";
    jsonToTable(elementID, classenrollmentdata);
}

window.onload = function() {
    // console.log(usersdata);
    // showUserData("UserTable");
    // showClassData("ClassTable");
    // showClassEnrollmentData("ClassEnrollmentTable");
};