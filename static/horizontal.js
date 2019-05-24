console.log('Corriendo horizontal')

const btnSendSite = document.getElementById('id-send-site');
const selectMintermFragment = document.getElementById("select-minterm-fragment");

btnSendSite.onclick = e => {
    const request = {
        minterms: mintermPredicates[Number(selectMintermFragment.value)], // Array<String>
        relation: selectRelation.value // String 
    }
    const requestString = JSON.stringify(request)
    fetch('/send_site/' + requestString)
        .then(res => res.json())
        .then(res => console.log(res))
        .catch(err => console.log(err))
}

const btnBuildMinterms = document.getElementById('btn-build-minterms');
let simplePredicates = new Set();
let mintermPredicates = [];

btnBuildMinterms.onclick = e => {
    if (document.getElementById('table-predicates').tBodies[0].rows.length > 0) {
        const json = {
            'relation': selectRelation.value,
            'predicates': [...simplePredicates] // convert set into list, we do this since we cannot stringify a set since data is not stored as values
        }
        const jsonStr = JSON.stringify(json)
        console.log(jsonStr)
        fetch('/build_minterms/' + jsonStr)
            .then(res => res.json())
            .then(mintermPredicatesResponse => { // [ [ ] ] list of list where each element contains tree minterms
                mintermPredicates = mintermPredicatesResponse
                for (let i = 0; i < mintermPredicatesResponse.length; ++i) {
                    const option = document.createElement('option')
                    option.value = i // query the index and obtain the minterms selected when sending minterm fragments
                    option.innerHTML = mintermPredicatesResponse[i].join(' | ')
                    selectMintermFragment.appendChild(option)
                }

            })
            .catch(err => console.log(err))
    }
}

const selectRelation = document.getElementById('sel-relation');
const selectAttributes = document.getElementById('sel-attributes');

String.prototype.replaceAll = function (search, replacement) {
    var target = this;
    return target.split(search).join(replacement);
};

// update the attributes as soon as you change the relation 
selectRelation.onchange = () => {
    const name = selectRelation.value;
    fetch('/relation_attributes/' + name)
        .then(res => res.json())
        .then(data => {
            const holder = '<option value="S">S</option>';
            selectAttributes.innerHTML = data.reduce((accumulator, current) =>
                accumulator + holder.replaceAll('S', current[0]), '')

            // alternative way 
            // let html = ''; 
            // data.forEach(attrInfo => html += holder.replaceAll('S', attrInfo[0]));
            // selectAttributes.innerHTML = html;
        })
}

const selectOperator = document.getElementById('sel-operator');
const textValue = document.getElementById('input-value');
const btnAddPredicate = document.getElementById('btn-add-predicate');

/**
 * Add a predicate, perform a JSON request by passing the relation and a predicate splitted 
 * by their attributes, it'll create rows for the table of predicates, clear the input value and 
 * add the predicate to simplePredicates from this script.
 */
function addPredicate() {
    const json = {
        relation: selectRelation.value,
        attribute: selectAttributes.value, operator: selectOperator.value, value: textValue.value
    }
    const jsonStr = JSON.stringify(json);
    textValue.value = ''
    fetch('/append_predicate/' + jsonStr)
        .then(res => res.json())
        .then(res => {
            if (res['ok']) {
                delete json.relation
                simplePredicates.add(json)

                const tbodyPredicates = document.getElementById('table-predicates').tBodies[0]
                const n = tbodyPredicates.rows.length
                const tr = document.createElement('tr')
                const td0 = document.createElement('td'), td1 = document.createElement('td')

                td0.appendChild(document.createTextNode(String(n)))
                td1.appendChild(document.createTextNode(
                    `${json['attribute']} ${json['operator']} ${json['value']}`));
                [td0, td1].forEach(td => tr.appendChild(td))
                tbodyPredicates.appendChild(tr)
            }
        })
        .catch(err => console.log(err));
}

btnAddPredicate.onclick = e => {
    if (textValue.value.length > 0) {
        addPredicate();
    }
}

textValue.onkeypress = e => {
    if (textValue.value.length > 0 && e.keyCode === 13) { // pressed enter
        addPredicate();
    }
}