
const form = document.querySelector('form.predict');

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const data = new FormData(form);
  fetch(form.action, {
    method: "POST",
    body: JSON.stringify(data.getAll('text')),
  }).then(response => response.json()).then(json => {
    document.querySelector('.answer').innerHTML = JSON.stringify(json, null, 2);
    hljs.highlightAll();
  })
})

const addRow = document.querySelector('button#add-row');
let counter = 0;


addRow.addEventListener('click', () => {
  const fieldset = document.querySelector('fieldset.fields')
  const name = 'id_text_' + counter;
  const label = document.createElement('label');
  label.for = name;
  label.innerHTML = document.querySelector('label[for="id_text"]').innerHTML;
  const input = document.createElement('input');
  input.type = 'text';
  input.id = name;
  input.name = "text"

  fieldset.appendChild(label)
  fieldset.appendChild(input)
})


