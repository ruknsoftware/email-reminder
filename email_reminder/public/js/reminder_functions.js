function filterFunction() {
	var input = document.getElementById("toggleInput");
    var filter = input.value.toUpperCase();
    var div = document.getElementById("toggleDropdown");
    var a = div.getElementsByTagName("a");

  for (i = 0; i < a.length; i++) {
    var txtValue = a[i].textContent || a[i].innerText;
            a[i].style.display = txtValue.toUpperCase().indexOf(filter) > -1 ? "" : "none";
  }
}

function toggleDropdown(display) {
    var a = document.querySelectorAll("#toggleDropdown a");

    a.forEach(function(link) {
        link.style.display = display;
    });
}

function focusIn() {
    console.log("test onclick focus in");
    field_clicked = true;
    toggleDropdown("");
}

function focusOut() {
    toggleDropdown("none");
}

