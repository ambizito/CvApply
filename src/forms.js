function createPDF() {

    if(document.getElementById("nome").value == "" || document.getElementById("cidade").value == "") {
        alert("Preencha todos os campos!");
    }
    else{
        var doc = new jsPDF();

        doc.text(document.getElementById("nome").value, 10,10);
        doc.text(document.getElementById("cidade").value, 25,25);


        doc.save(teste.pdf);
    }
  
}
