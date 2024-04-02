const xhttp = new XMLHttpRequest();
const async = true;

/*
Create a json as a child node of the element with ID "elementID" from the json stored in the string json
No output values, it just directly edits the node in the document
*/
function jsonToTable(elementID, json){
    console.log(elementID);
    if(typeof json === 'undefined'){
        console.log("undefined JSON")
    }
    else{
        const dict = JSON.parse(json); //Get the json from the json string
        console.log(dict);
        let table = document.createElement("table");

        //Headers
        let headerRow = document.createElement("tr");
        for(let i = 0; i < headers.length; i++){
            let header = document.createElement("th");
            let text = document.createTextNode(headers[i]);
            header.appendChild(text);

            headerRow.appendChild(header);
        }
        table.appendChild(headerRow);

        console.log(dict)
        //Rows
        let keys;
        let grades;
        let arrayTrue = false
        if(dict.length > 1){
            keys = extractNames(dict)
            grades = extractGrades(dict)
            arrayTrue = true
        }
        else{
            keys = dict.name
            grades = dict.grade
        }
        console.log(keys)
        console.log(grades)
        for(let i = 0; i < keys.length; i++){
            let row = document.createElement("tr");

            let key = document.createElement("td");
            let text;
            if(arrayTrue)
                text = document.createTextNode(keys[i]);
            else
                text = document.createTextNode(keys);
            key.appendChild(text); //Add the text to the td
            if (i%2 ==1){
                key.setAttribute("class", "oddRow");
            }
            else{
                key.setAttribute("class", "evenRow");
            }
            row.appendChild(key); //Add the td to the table

            let value = document.createElement("td");
            if(arrayTrue)
                text = document.createTextNode(grades[i]);
            else
            text = document.createTextNode(grades);
            value.appendChild(text);//Add the text to the td
            if (i%2 ==1){
                value.setAttribute("class", "oddRow");
            }
            else{
                value.setAttribute("class", "evenRow");
            }
            row.appendChild(value);//Add the td to the table

            table.appendChild(row);
        }
        document.getElementById(elementID).appendChild(table);
    }
}

/*
Uses the "/view_users" route to get all information in the database
Adds a table as a child node of the element with id elementID
Outputs the json

    NOTE: Currently does not function completely properly as "/view_users" is WIP
*/
function showAllData(elementID){
    let data;
    thisURL = "/view_users";
    xhttp.open("GET", thisURL, async);
    xhttp.send();
    xhttp.onreadystatechange = () => {
        if (xhttp.readyState === 4) {
            if (xhttp.status == 200) {
                data = xhttp.responseText;
                // document.getElementById(elementID).innerHTML = ''; //Empties response
                console.log(data);
                jsonToTable(elementID, data);
            }
            else{
                pass;
            }
        }
    };
    return(data);
}

window.onload = function() {
    showAllData("DataTable");
};