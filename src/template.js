const secTemplates = document.querySelectorAll('.templates-container');
const selectTemplates = document.querySelectorAll('.template');
const templates = document.querySelectorAll('.templates');
const allSecs = document.querySelector(".main-content");

function chooseTemplates() {

function templateSelection() {
  for (let i = 0; i <selectTemplates.length; i++) {
    selectTemplates[i].addEventListener("click", function() {
      let currentTemplate = document.querySelectorAll("active-template");
      currentTemplate[0].className = currentTemplate[0].className.replace("active-Template", ""
      );
      this.className += " active-template";
    })
  }
}
templates.addEventListener('click', (event) => {
  const id = event.target.dataset.imgId;
  if (data-imgId) {
    // remove 'selected' class from other templates
    secTemplates.querySelectorAll('.template').forEach((template) => {
      template.classList.remove('selected');
    });
    // add 'selected' class to the clicked template
    event.target.closest('.template').classList.add('selected');
  }
});
}
