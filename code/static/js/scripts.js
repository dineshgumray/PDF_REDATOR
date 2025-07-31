document.addEventListener('DOMContentLoaded', function() {
    const fileLabel = document.getElementById('fileLabel');
    const fileInput = document.getElementById('fileInput');
    const fileNamesDiv = document.getElementById('fileNames');

    fileLabel.addEventListener('click', function(){
        fileInput.click();
    });

    fileInput.addEventListener('change', function(){
        fileNamesDiv.innerHTML = "";
        const files = this.files;

        if (files.length === 0) {
            fileNamesDiv.innerHTML = "<em>No files selected</em>";
        } else {
            const ul = document.createElement('ul');
            for (let i = 0; i < files.length; i++) {
                const li = document.createElement('li');
                li.textContent = files[i].name;
                ul.appendChild(li);
            }
            fileNamesDiv.appendChild(ul);
        }
    });
});

function addField() {
    const container = document.getElementById('fieldsContainer');
    const div = document.createElement('div');
    div.classList.add('field-group');
    div.innerHTML = `
        <input type="text" name="fields[]" placeholder="Field to redact">
        <input type="text" name="placeholders[]" placeholder="Placeholder text">
        <button type="button" class="delete-btn" onclick="deleteField(this)">Delete</button>
    `;
    container.appendChild(div);
}

function deleteField(button) {
    button.parentNode.remove();
}

if (performance.navigation.type === 1) {
    window.location.href = "/";
}