
let relation = document.getElementById('relation');
let availableAttributes = document.getElementById('selected_attributes');

alert("hola"); 

String.prototype.replaceAll = function (search, replacement) {
    var target = this;
    return target.split(search).join(replacement);
};

// When the relation select field changes the attributes from this will change too
relation.onchange = e => {
    let name = relation.value;
    fetch('/relation_attributes/' + name).then(res => {
        res.json().then(data => { // important to call json 
            let holder = '<option value="S">S</option>', html = '';
            data.forEach(attrInfo => html += holder.replaceAll('S', attrInfo[0]));
            availableAttributes.innerHTML = html;
        })
    })
};