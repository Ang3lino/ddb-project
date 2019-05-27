
    const selRelation = document.getElementById('relation');
    const selSite = document.getElementById("select-site");

    const selMultAttributes = document.getElementById('selected_attributes');
    const selMultExpressions = document.getElementById("select-expressions");

    const btnSendSite = document.getElementById("btn-send-site");
    const btnAddSelection = document.getElementById('btn-add-selection');

    const tablePrimaryKeys = document.getElementById('table-primary-keys');

    let attributeIndexes = []; // Array< Array< Int > >

    function addPrimaryKeysTable(primaryKeys) {
        tablePrimaryKeys.innerHTML = primaryKeys.reduce(
            (acc, cur) => acc + `<tr><td> ${cur} </td></tr> `, ''
        )
    }

    btnSendSite.onclick = e => {
      const reqObj = {
        site: selSite.value,
        relation: selRelation.value,
        attributes: valuesFromMultipleSelect(selMultExpressions).map(cur => attributeIndexes[cur])
      }
      console.log(reqObj)
      const attr = valuesFromMultipleSelect(selMultExpressions).map(cur => attributeIndexes[cur])

      fetch('/vertical_send_site/' + JSON.stringify(reqObj))
        .then(res => res.json())
        .then(res => {
          alert("Se ha creado su fragmento")
        })
        .catch(err => console.log(err))

    }


    btnAddSelection.onclick = e => {
      const attributes = textsFromMultipleSelect(selMultAttributes)
      const query = `SELECT ${attributes.join(', ')} FROM ${selRelation.value}`
      addChildSelect(selMultExpressions, query, attributeIndexes.length)
      attributeIndexes.push(valuesFromMultipleSelect(selMultAttributes))
    }

    function addChildSelect(target, text, value) {
      const option = document.createElement('option')
      option.value = value
      option.text = text
      target.appendChild(option)
    }

    function replaceChildrenSelect(target, texts, values) {
      removeChildren(target)
      const minLength = Math.min(texts.length, values.length)
      for (let i = 0; i < minLength; ++i) {
        const option = document.createElement('option')
        option.value = values[i]
        option.text = texts[i]
        target.appendChild(option)
      }
    }

    String.prototype.replaceAll = function (search, replacement) {
      var target = this;
      return target.split(search).join(replacement);
    };

    function valuesFromMultipleSelect(selectObject) {
      return Array.from(selectObject.selectedOptions).map(option => option.value)
    }

    function textsFromMultipleSelect(selectObject) {
      return Array.from(selectObject.selectedOptions).map(option => option.text)
    }

    function removeChildren(parent) {
      while (parent.firstChild) parent.removeChild(parent.firstChild)
    }

    // When the relation select field changes the attributes from this will change too
    selRelation.onchange = e => {
      fetch('/relation_attributes/' + selRelation.value)
        .then(res => res.json())
        .then(data => { // Array<Array<String>>
          const first = d => d[0]
          const isPrimary = d => d[3] === 'PRI' || d[3] === 'MUL'
          const display = data.filter(d => !isPrimary(d)).map(first)
          const primaryKeys = data.filter(isPrimary).map(first)
          const nonPrimaryKeyIndexes = [...data.entries()].filter(t => !isPrimary(t[1])).map(first)
          addPrimaryKeysTable(primaryKeys)
          replaceChildrenSelect(selMultAttributes, display, nonPrimaryKeyIndexes)
        })
    };

